"""
score_tests - Marcy Lab School test scoring for pytest.

Python port of the `score-tests` npm package used by the JavaScript
assignments. Produces a `scores/scores.json` file with the same shape, so
existing grading tooling keeps working unchanged.

Students never edit this file. It is wired up by `conftest.py` at the repo
root and runs automatically on every `pytest` invocation.

HOW TEST NAMES ARE BUILT
------------------------
The JavaScript version nests `describe(suite) > describe(group) > test(name)`
and joins those strings with spaces. The Python version mirrors that using a
module-level constant plus docstrings:

    TEST_SUITE_NAME = "From Scratch Tests"        # module level

    class TestMakeIdFunc:
        '''make_id_func'''                        # the group

        def test_starts_at_one(self):
            '''starts on 1'''                     # the test
            ...

produces the name "From Scratch Tests make_id_func starts on 1".

Docstrings are optional. Without one, the name is derived from the function
name (`test_starts_at_one` -> "starts at one").

HOW IDS STAY STABLE
-------------------
Each suite gets a prefix from the first two letters of each word in its name
("From Scratch Tests" -> "FrScTe"). Tests are numbered in collection order the
first time they are seen, and that mapping is persisted in scores.json, so IDs
stay put across runs.

Renaming a test allocates it a NEW id, because the lookup is by name. Old
entries are never deleted, so past scores stay interpretable; to keep a
renamed test on its old id, point the new name at that id by hand in
`testNameToIdHash`. This matches the JavaScript package's behavior.

Running a subset (`pytest tests/test_debug.py`) only updates that suite.
Scores for suites that did not run are carried over untouched.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

SCORES_FILENAME = "scores.json"


def suite_prefix(suite_name: str) -> str:
    """'From Scratch Tests' -> 'FrScTe'. Matches the JavaScript scheme."""
    words = re.findall(r"[A-Za-z0-9]+", suite_name)
    if not words:
        return "Te"
    return "".join(w[0].upper() + (w[1].lower() if len(w) > 1 else "") for w in words)


def humanize(func_name: str) -> str:
    """'test_starts_at_one' -> 'starts at one'. Fallback when no docstring."""
    name = re.sub(r"^test_?", "", func_name)
    return name.replace("_", " ").strip() or func_name


def _first_line(doc: str | None) -> str | None:
    if not doc:
        return None
    for line in doc.strip().splitlines():
        if line.strip():
            return line.strip()
    return None


class ScoreCounter:
    """Accumulates outcomes for one pytest session and writes scores.json."""

    def __init__(self, scores_dir: Path):
        self.scores_dir = Path(scores_dir)
        self.path = self.scores_dir / SCORES_FILENAME
        # nodeid -> (suite_name, full_test_name)
        self.registry: dict[str, tuple[str, str]] = {}
        # A test counts as correct only if its `call` phase passed AND no
        # phase (setup/call/teardown) failed. Anything never run scores 0.
        self.call_passed: set[str] = set()
        self.failed: set[str] = set()
        self.data = self._load()

    # ---------- persistence ----------

    def _load(self) -> dict:
        try:
            with open(self.path, encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}
        data.setdefault("testScores", {})
        data.setdefault("idToTestNameHash", {})
        data.setdefault("testNameToIdHash", {})
        data.setdefault("humanReadable", {})
        return data

    # ---------- collection ----------

    def register(self, nodeid: str, suite_name: str, test_name: str) -> None:
        self.registry[nodeid] = (suite_name, test_name)

    def record_call(self, nodeid: str, passed: bool) -> None:
        if passed:
            self.call_passed.add(nodeid)
        else:
            self.failed.add(nodeid)

    def record_failure(self, nodeid: str) -> None:
        self.failed.add(nodeid)

    def is_correct(self, nodeid: str) -> bool:
        return nodeid in self.call_passed and nodeid not in self.failed

    # ---------- id allocation ----------

    def _next_id(self, suite_name: str) -> str:
        prefix = suite_prefix(suite_name)
        used = {
            int(m.group(1))
            for key in self.data["idToTestNameHash"]
            if (m := re.fullmatch(rf"{re.escape(prefix)}(\d+)", key))
        }
        n = 1
        while n in used:
            n += 1
        return f"{prefix}{n}"

    def id_for(self, suite_name: str, test_name: str) -> str:
        existing = self.data["testNameToIdHash"].get(test_name)
        if existing:
            return existing
        new_id = self._next_id(suite_name)
        self.data["testNameToIdHash"][test_name] = new_id
        self.data["idToTestNameHash"][new_id] = test_name
        return new_id

    # ---------- output ----------

    def write(self) -> None:
        if not self.registry:
            return

        scores: dict[str, dict[str, int]] = {}
        for nodeid, (suite_name, test_name) in self.registry.items():
            test_id = self.id_for(suite_name, test_name)
            scores.setdefault(suite_name, {})[test_id] = 1 if self.is_correct(nodeid) else 0

        # Preserve suites from previous runs that were not part of this run
        # (e.g. `pytest tests/test_debug.py` alone) so partial runs do not
        # silently zero out the rest of the assignment.
        for suite_name, suite_scores in self.data["testScores"].items():
            if suite_name not in scores:
                scores[suite_name] = suite_scores

        human: dict[str, str] = {}
        total = earned = 0
        for suite_name, suite_scores in scores.items():
            got = sum(suite_scores.values())
            out_of = len(suite_scores)
            human[suite_name] = f"{got}/{out_of}"
            earned += got
            total += out_of
        human["finalTestScore"] = f"FINAL SCORE: {earned}/{total}"

        self.data["testScores"] = scores
        self.data["humanReadable"] = human

        self.scores_dir.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)
            f.write("\n")


# --------------------------------------------------------------------------
# pytest plugin
# --------------------------------------------------------------------------


def build_test_name(item) -> tuple[str, str]:
    """Return (suite_name, full_test_name) for a collected pytest item."""
    module = getattr(item, "module", None)
    suite = getattr(module, "TEST_SUITE_NAME", None)
    if not suite:
        stem = Path(str(item.fspath)).stem
        suite = humanize(re.sub(r"^test_?", "", stem)).title() + " Tests"

    parts = [suite]

    cls = getattr(item, "cls", None)
    if cls is not None:
        parts.append(_first_line(cls.__doc__) or cls.__name__)

    func = getattr(item, "function", None)
    label = _first_line(getattr(func, "__doc__", None)) or humanize(
        getattr(item, "originalname", None) or item.name
    )
    parts.append(label)

    # Keep parametrized cases distinct: test_x[a] -> "... [a]"
    bracket = re.search(r"(\[.*\])$", item.name)
    if bracket:
        parts.append(bracket.group(1))

    return suite, " ".join(parts)


class ScoreTestsPlugin:
    def __init__(self, scores_dir: Path):
        self.counter = ScoreCounter(scores_dir)

    def pytest_collection_modifyitems(self, session, config, items):
        for item in items:
            suite, name = build_test_name(item)
            self.counter.register(item.nodeid, suite, name)

    def pytest_runtest_logreport(self, report):
        if report.nodeid not in self.counter.registry:
            return
        if report.when == "call":
            self.counter.record_call(report.nodeid, report.passed)
        elif report.failed:  # setup or teardown blew up
            self.counter.record_failure(report.nodeid)

    def pytest_sessionfinish(self, session, exitstatus):
        self.counter.write()


def register(config, repo_root: Path) -> None:
    """Called from conftest.py to install the plugin."""
    config.pluginmanager.register(
        ScoreTestsPlugin(Path(repo_root) / "scores"), "marcy-score-tests"
    )
