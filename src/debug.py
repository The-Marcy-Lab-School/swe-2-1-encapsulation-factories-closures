# Oops! This factory function exposes the students list.
# Can you make it private using a closure?

from types import SimpleNamespace


def create_course(topic, instructor):
    course = SimpleNamespace(topic=topic, instructor=instructor, students=[])

    def add_student(name):
        course.students.append(name)

    def remove_student(name):
        course.students.remove(name)

    def get_students():
        return course.students

    course.add_student = add_student
    course.remove_student = remove_student
    course.get_students = get_students
    return course
