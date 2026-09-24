# Encapsulation, Factories, and Closures

Write factory functions that keep their data private, using closures.

**Practicing:** closures, factory functions, encapsulation

> **The short responses for this assignment are in
> [swe-2-1-encapsulation-factories-closures-sr](https://github.com/The-Marcy-Lab-School/swe-2-1-encapsulation-factories-closures-sr).**
> Both repos are part of this assignment.

- [AI Use on This Assignment](#ai-use-on-this-assignment)
- [Setup](#setup)
- [From Scratch](#from-scratch)
  - [Question 1: `make_id_func`](#question-1-make_id_func)
  - [Question 2: `make_password_checker`](#question-2-make_password_checker)
  - [Question 3: `make_multiplier`](#question-3-make_multiplier)
  - [Question 4: `make_filter_by_length`](#question-4-make_filter_by_length)
  - [Question 5: `make_grade_tracker`](#question-5-make_grade_tracker)
  - [Question 6: `make_shopping_list`](#question-6-make_shopping_list)
- [Debug](#debug)
  - [Question 7: `create_course`](#question-7-create_course)
- [Submitting](#submitting)

## AI Use on This Assignment

Use whichever mode matches where you are with this material. Both are fine,
and most people move between them as a concept clicks.

**Tutor mode.** The AI explains, questions, quizzes, and critiques, and you
write every line you submit. For this assignment that means asking it how a
closure keeps a variable private, or having it quiz you until you can predict
what your own code will do. Ask it a hundred questions — that is the whole
point. What you do not do is ask it for the function. Paste this at the start
of a chat and it will hold for the rest of the conversation:

> You are acting as a tutor. Your job is to explain what this coding question
> is asking, clarify confusing wording, and highlight the relevant concepts I
> need to know — but do not provide the full solution or code that directly
> answers the question. Instead, rephrase the problem in simpler terms,
> identify what is being tested, and suggest what steps or thought processes
> might help. Ask me guiding questions to make sure I am thinking critically.
> Do not write the final function, algorithm, or code implementation.

**Implementer mode.** You write a specification first, the AI writes code from
it, and then you verify that code line by line. For this assignment your spec
has to name what stays private and what the returned object exposes. If what
comes back does more than you asked for, reject it — over-delivery is a
defect, and catching it is part of the job.

You own every line either way, and you will be asked to explain it.

## Setup

Work in `development/mod-2`. Make a draft branch before you start.

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
git checkout -b draft
```

Run `pytest` for everything, or `pytest -k MakeIdFunc` for one question's
tests. Scores land in `scores/scores.json`.

75% of tests passing counts as complete. Submit at that point even if it is
not perfect. Treat submitting as a checkpoint rather than a finish line, and
come back to improve it.

A **closure** is a function that remembers the variables around it after the
outer function returns. That memory keeps the data private.

## From Scratch

Write your solutions in `src/from_scratch.py`.

### Question 1: `make_id_func`

Write a higher-order function that returns an inner function with a closure.
The returned inner function should:

- Return `1` the first time it is called
- Return `2` the second time it is called
- Return `3` the third time it is called
- And so on

Each call to `make_id_func` starts its own count. This kind of function is how
you generate unique number IDs for things.

```python
id_maker1 = make_id_func()
id_maker2 = make_id_func()

print(id_maker1())   # 1
print(id_maker1())   # 2
print(id_maker1())   # 3

print(id_maker2())   # 1
print(id_maker2())   # 2
```

You need [`nonlocal`](https://www.w3schools.com/python/python_scope.asp).
Without it Python quietly makes a brand new local variable, and your counter
is stuck on 1 forever. That is a deeply annoying five minutes to debug, so
save yourself the five minutes.

### Question 2: `make_password_checker`

Write a higher-order function that takes a `correct_password` and returns an
inner function with a closure. The returned function should:

- Take a `guess` as an argument
- Keep track of how many attempts have been made
- Return `True` if the guess matches the correct password
- Return `False` if the guess is wrong
- Return the string `"Account locked"` after 3 failed attempts

```python
check = make_password_checker("secret123")
check("nope")        # False
check("nope")        # False
check("nope")        # False
check("secret123")   # "Account locked"
```

Note that last line. The right password does not save you once the account is
locked. That is the whole point of locking it.

### Question 3: `make_multiplier`

Write a function that takes a number called `multiplier` and returns a
function. The returned function should:

- Take a list of numbers as an argument
- Return a new list with each number multiplied by `multiplier`
- Use a comprehension or `map()`, not a `for` loop

```python
double = make_multiplier(2)
triple = make_multiplier(3)

double([1, 2, 3, 4])   # [2, 4, 6, 8]
triple([1, 2, 3, 4])   # [3, 6, 9, 12]
```

### Question 4: `make_filter_by_length`

Write a function that takes a number called `max_length` and returns a
function. The returned function should:

- Take a list of strings as an argument
- Return a new list of only the strings whose length is *less than or equal
  to* `max_length`
- Use a comprehension or `filter()`, not a `for` loop

```python
shorter_than_4 = make_filter_by_length(4)
animals = ["cat", "dog", "elephant", "bird", "llama"]

shorter_than_4(animals)   # ['cat', 'dog', 'bird']
```

### Question 5: `make_grade_tracker`

Write a factory function that returns an object for tracking student grades.

- Use a closure to keep a private `grades` list. You should **not** be able to
  reach `grades` from outside
- The returned object has methods that act on that list

Questions 5 and 6 return objects with methods. Build them with
`SimpleNamespace`, already imported for you:

```python
return SimpleNamespace(add_grade=add_grade, get_average=get_average)
```

| Method | Does | Returns |
| --- | --- | --- |
| `add_grade(grade)` | Adds a grade from 0 to 100 | `True`, or `False` if out of range |
| `get_average()` | Averages every grade | The average, or `0` if empty |

```python
tracker = make_grade_tracker()
tracker.add_grade(90)    # True
tracker.add_grade(150)   # False
tracker.get_average()    # 90
```

The object exposes these two methods and nothing else.

### Question 6: `make_shopping_list`

Write a factory function that returns an object for managing a shopping list.

- Use a closure to keep a private `items` list of grocery items
- The returned object has methods that act on that list

| Method | Does | Returns |
| --- | --- | --- |
| `get_items()` | Reads the list | A **copy**, never the original |
| `add_item(item)` | Adds an item and prints a message | The new length |
| `remove_item(item)` | Removes an item and prints a message | `True`, or `False` if not found |

```python
my_list = make_shopping_list()
my_list.add_item("eggs")      # prints "eggs successfully added! Now you have 1 item(s)."
my_list.add_item("milk")      # prints "milk successfully added! Now you have 2 item(s)."
my_list.remove_item("milk")   # prints "milk successfully removed. You now have 1 item(s)."
my_list.remove_item("jam")    # prints "jam not found."
my_list.get_items()           # ['eggs']
```

The printed messages must match exactly, punctuation included. Yes, including
the `item(s)`. We know.

Pay attention to that word **copy**. If `get_items` hands back the real list,
anyone can reach in and rearrange your shopping, and one of the tests will
catch you doing it.

## Debug

### Question 7: `create_course`

`create_course` in `src/debug.py` works, which is what makes it sneaky. It
builds a course, adds students, removes them, and every one of those behaviors
is correct. The problem is that `students` is sitting right there on the
returned object. Anything can reach in and change the roster without going
through `add_student` at all.

How would you hold that list somewhere the returned object can reach but
outside code cannot? Rewrite `create_course` so `students` lives in a closure,
and make `get_students` hand back a copy.

```python
course = create_course("computer science", "ada lovelace")
course.add_student("zo")
course.students.append("not a real student")   # should not be possible
```

Everything that worked before must still work. The tests show you exactly
what that means.

## Submitting

```sh
git add -A
git commit -m "your message"
git push
```

Open a pull request to your instructor for feedback. Remember to submit the
short response repo too.
