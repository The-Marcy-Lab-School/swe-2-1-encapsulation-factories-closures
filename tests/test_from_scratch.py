from types import SimpleNamespace

import pytest
from from_scratch import (
    make_filter_by_length,
    make_grade_tracker,
    make_id_func,
    make_multiplier,
    make_password_checker,
    make_shopping_list,
)

TEST_SUITE_NAME = "From Scratch Tests"


def last_printed(capsys):
    """Return the most recent line printed, like Jest's lastCalledWith."""
    lines = [line for line in capsys.readouterr().out.splitlines() if line.strip()]
    return lines[-1] if lines else ""


class TestMakeIdFunc:
    """make_id_func"""

    def test_each_call_starts_back_at_1(self):
        """Each new call of the function starts back at 1"""
        get_id1 = make_id_func()
        assert get_id1() == 1
        assert get_id1() == 2
        assert get_id1() == 3

        get_id2 = make_id_func()
        assert get_id2() == 1
        assert get_id2() == 2
        assert get_id2() == 3

        get_id3 = make_id_func()
        assert get_id3() == 1
        assert get_id3() == 2
        assert get_id3() == 3

    def test_increments_counter_by_1(self):
        """increments counter by 1"""
        get_id = make_id_func()
        assert get_id() == 1
        assert get_id() == 2
        assert get_id() == 3
        assert get_id() == 4
        assert get_id() == 5


class TestMakePasswordChecker:
    """make_password_checker"""

    def test_returns_correct_boolean(self):
        """returns the correct boolean based on the guess"""
        check_password = make_password_checker("secret123")
        assert check_password("secret123") is True
        assert check_password("wrong") is False

    def test_locks_after_3_failed_attempts(self):
        """returns Account locked after 3 failed attempts"""
        check_password = make_password_checker("secret123")
        assert check_password("nope") is False
        assert check_password("nope") is False
        assert check_password("nope") is False
        assert check_password("secret123") == "Account locked"


class TestMakeMultiplier:
    """make_multiplier"""

    def test_doubles_every_number(self):
        """returns the correct list with the numbers multiplied by the multiplier"""
        double = make_multiplier(2)
        assert double([1, 2, 3, 4]) == [2, 4, 6, 8]

    def test_works_for_any_multiplier(self):
        """returns a separate function for each multiplier"""
        triple = make_multiplier(3)
        by_zero = make_multiplier(0)
        assert triple([1, 2, 3, 4]) == [3, 6, 9, 12]
        assert by_zero([1, 2, 3]) == [0, 0, 0]
        # the first function is unaffected by making a second one
        assert triple([5]) == [15]


class TestMakeFilterByLength:
    """make_filter_by_length"""

    def test_filters_by_length(self):
        """returns a function that filters a list of strings by length"""
        shorter_than_5 = make_filter_by_length(5)
        fruits = ["apple", "banana", "cherry", "date"]
        assert shorter_than_5(fruits) == ["apple", "date"]
        assert shorter_than_5(["aaaaaaa", "bbbb", "ccc"]) == ["bbbb", "ccc"]

        shorter_than_10 = make_filter_by_length(10)
        assert shorter_than_10(fruits) == ["apple", "banana", "cherry", "date"]

        no_words = make_filter_by_length(0)
        assert no_words(fruits) == []


class TestMakeGradeTracker:
    """make_grade_tracker"""

    def test_returns_an_object(self):
        """returns an object"""
        student_grades = make_grade_tracker()
        assert isinstance(student_grades, SimpleNamespace)

    def test_add_grade(self):
        """.add_grade - adds a valid grade and returns whether it was added"""
        student_grades = make_grade_tracker()
        assert student_grades.add_grade(85) is True
        assert student_grades.add_grade(85.5) is True
        assert student_grades.add_grade(0) is True
        assert student_grades.add_grade(100) is True

        # invalid grades should return False
        assert student_grades.add_grade(105) is False
        assert student_grades.add_grade(-5) is False

    def test_get_average(self):
        """.get_average - returns the average of all grades in the list"""
        student_grades = make_grade_tracker()
        # with no grades the average is 0, not an error
        assert student_grades.get_average() == 0

        student_grades.add_grade(1)
        assert student_grades.get_average() == pytest.approx(1)
        student_grades.add_grade(3)
        assert student_grades.get_average() == pytest.approx(2)
        student_grades.add_grade(8)
        assert student_grades.get_average() == pytest.approx(4)

    def test_does_not_expose_grades(self):
        """.get_average - does not expose the grades list"""
        student_grades = make_grade_tracker()
        assert not hasattr(student_grades, "grades")

        # only the specified methods should be available
        assert list(vars(student_grades)) == ["add_grade", "get_average"]


class TestMakeShoppingList:
    """make_shopping_list"""

    def test_returns_an_object(self):
        """returns an object"""
        shopping_list = make_shopping_list()
        assert isinstance(shopping_list, SimpleNamespace)

    def test_get_items_returns_a_list(self):
        """.get_items - is a function that returns a list"""
        shopping_list = make_shopping_list()
        # empty until something is added
        assert shopping_list.get_items() == []

    def test_get_items_returns_a_copy(self):
        """.get_items - always returns a copy of the items list"""
        shopping_list = make_shopping_list()
        items1 = shopping_list.get_items()
        items2 = shopping_list.get_items()

        # a new list each time, not the same one
        assert items1 is not items2

    def test_add_item(self, capsys):
        """.add_item - adds an item, returns the new length, and prints the message"""
        shopping_list = make_shopping_list()

        banana = "Banana"
        apple = "Apple"
        carrot = "Carrot"

        assert shopping_list.add_item(banana) == 1
        assert shopping_list.get_items() == [banana]
        assert last_printed(capsys) == f"{banana} successfully added! Now you have 1 item(s)."

        assert shopping_list.add_item(apple) == 2
        assert shopping_list.get_items() == [banana, apple]
        assert last_printed(capsys) == f"{apple} successfully added! Now you have 2 item(s)."

        assert shopping_list.add_item(carrot) == 3
        assert shopping_list.get_items() == [banana, apple, carrot]
        assert last_printed(capsys) == f"{carrot} successfully added! Now you have 3 item(s)."

    def test_remove_item(self, capsys):
        """.remove_item - removes an item, returns True, and prints the message"""
        shopping_list = make_shopping_list()
        banana = "Banana"
        apple = "Apple"
        carrot = "Carrot"
        shopping_list.add_item(banana)
        shopping_list.add_item(apple)
        shopping_list.add_item(carrot)
        capsys.readouterr()  # discard the add messages

        assert shopping_list.remove_item(apple) is True
        assert shopping_list.get_items() == [banana, carrot]
        assert last_printed(capsys) == f"{apple} successfully removed. You now have 2 item(s)."

        assert shopping_list.remove_item(banana) is True
        assert shopping_list.get_items() == [carrot]
        assert last_printed(capsys) == f"{banana} successfully removed. You now have 1 item(s)."

        assert shopping_list.remove_item(carrot) is True
        assert shopping_list.get_items() == []
        assert last_printed(capsys) == f"{carrot} successfully removed. You now have 0 item(s)."

        date = "Date"
        assert shopping_list.remove_item(date) is False
        assert last_printed(capsys) == f"{date} not found."

    def test_does_not_expose_items(self):
        """does not expose the internal items list"""
        shopping_list = make_shopping_list()
        assert not hasattr(shopping_list, "items")

        # you cannot change the internal items list from outside the object
        gene = "Gene"
        shopping_list.add_item(gene)

        items_copy = shopping_list.get_items()
        assert shopping_list.get_items() == [gene]

        items_copy.append("Zo")
        assert shopping_list.get_items() == [gene]

        items_copy.clear()
        assert shopping_list.get_items() == [gene]

        # only the specified methods should be available
        assert len(vars(shopping_list)) == 3
        assert callable(shopping_list.add_item)
        assert callable(shopping_list.remove_item)
        assert callable(shopping_list.get_items)
