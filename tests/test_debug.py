from debug import create_course

TEST_SUITE_NAME = "Debug Tests"


class TestCreateCourse:
    """create_course"""

    def test_creates_a_course_object(self):
        """creates an object for managing a course"""
        topic = "computer science"
        instructor = "ada lovelace"
        course = create_course(topic, instructor)

        # basic attributes are set
        assert course.topic == topic
        assert course.instructor == instructor

        # can add students and read the updated list
        course.add_student("zo")
        course.add_student("carmen")
        assert course.get_students() == ["zo", "carmen"]

        # can remove students and read the updated list
        course.remove_student("carmen")
        assert course.get_students() == ["zo"]

    def test_keeps_students_private(self):
        """keeps the students list private using a closure"""
        topic = "computer science"
        instructor = "ada lovelace"
        course = create_course(topic, instructor)

        # students is not an attribute that can be reached directly
        assert not hasattr(course, "students")

        course.add_student("zo")
        course.add_student("carmen")
        students = course.get_students()
        students.append("ben")  # if this is a copy, the original is unaffected

        # get_students returns a copy, not the original list
        assert course.get_students() == ["zo", "carmen"]

        other_course = create_course("english", "maya")

        # each course has its own students list
        assert other_course.get_students() is not course.get_students()
        assert other_course.get_students() == []
