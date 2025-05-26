from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta
import os
import json
from .models import Courses, Subjects, Students
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError
from django.db import connection

class CoursesModelTest(TestCase):
    """
    Test suite for the Courses model.
    Check various scenarios when creating a new course.
    """
    
    def setUp(self):
        """Set up test data before each method runs."""
        # Delete all related students first
        Students.objects.all().delete()
        # Delete all related subjects
        Subjects.objects.all().delete()
        # Now delete all courses
        Courses.objects.all().delete()
    
    def get_db_state(self, stage):
        """Record the current state of the database."""
        db_state = {
            'stage': stage,
            'courses_count': Courses.objects.count(),
            'courses': list(Courses.objects.values('id', 'course_name', 'created_at', 'updated_at'))
        }
        return db_state
    
    def print_db_state(self, state, label):
        """Print the DB state in a readable format."""
        courses_info = ""
        if state['courses']:
            for course in state['courses']:
                created_at = course['created_at'].strftime('%Y-%m-%d %H:%M:%S') if course['created_at'] else 'N/A'
                updated_at = course['updated_at'].strftime('%Y-%m-%d %H:%M:%S') if course['updated_at'] else 'N/A'
                courses_info += f"\n    - ID: {course['id']}, Name: {course['course_name']}, Created: {created_at}, Updated: {updated_at}"
        else:
            courses_info = "\n    (No data)"
            
        print(f"\n{'='*80}")
        print(f"\n  📊 {label} ({state['stage']})")
        print(f"\n  📋 Number of Courses: {state['courses_count']}")
        print(f"\n  📝 Details:{courses_info}")
        print(f"\n{'='*80}\n")

    def C_ADD_NA_01_course_name_has_empty_string_ERROR(self):
        with transaction.atomic():
            try:
                print("\n🔍 C-ADD-NA-01: course_name is empty - ERROR")
                initial_count = Courses.objects.count()
                Courses.objects.create(course_name="")
                self.fail("Course should not be created with an empty course_name.")
            except Exception as e:
                transaction.set_rollback(True)
                print(f"✅ Expected error caught: {str(e)}")

            final_count = Courses.objects.count()
            self.assertEqual(initial_count, final_count, "Course count should not change when creation fails.")

    def C_ADD_NA_02_course_name_has_1_character_ERROR(self):
        with transaction.atomic():
            try:
                print("\n🔍 C-ADD-NA-02: course_name = 'A' (1 character) - ERROR")
                initial_count = Courses.objects.count()
                Courses.objects.create(course_name="A")
                self.fail("Course should not be created with 1 character course_name.")
            except Exception as e:
                transaction.set_rollback(True)
                print(f"✅ Expected error caught: {str(e)}")

            final_count = Courses.objects.count()
            self.assertEqual(initial_count, final_count, "Course count should not change when creation fails.")

    def C_ADD_NA_03_course_name_has_2_characters_SUCCESS(self):
        with transaction.atomic():
            try:
                print("\n🔍 C-ADD-NA-03: course_name = 'AI' (2 characters) - SUCCESS")
                initial_count = Courses.objects.count()
                course = Courses.objects.create(course_name="AI")
                final_count = Courses.objects.count()

                self.assertIsNotNone(course.id, "Course should be created and have an ID.")
                self.assertEqual(final_count, initial_count + 1, "Course count should increase by 1.")
            except Exception as e:
                transaction.set_rollback(True)
                self.fail(f"Unexpected error: {str(e)}")

    def C_ADD_NA_04_course_name_has_3_characters_SUCCESS(self):
        with transaction.atomic():
            try:
                print("\n🔍 C-ADD-NA-04: course_name = 'IT1' (3 characters) - SUCCESS")
                initial_count = Courses.objects.count()
                course = Courses.objects.create(course_name="IT1")
                final_count = Courses.objects.count()

                self.assertIsNotNone(course.id, "Course should be created and have an ID.")
                self.assertEqual(final_count, initial_count + 1, "Course count should increase by 1.")
            except Exception as e:
                transaction.set_rollback(True)
                self.fail(f"Unexpected error: {str(e)}")

    def C_ADD_NA_05_course_name_has_49_characters_SUCCESS(self):
        with transaction.atomic():
            try:
                course_name = "Introduction to Software Quality Assurance Concepts"
                print(f"\n🔍 C-ADD-NA-05: course_name = '{course_name}' ({len(course_name)} chars) - SUCCESS")

                initial_count = Courses.objects.count()
                course = Courses.objects.create(course_name=course_name)
                final_count = Courses.objects.count()

                self.assertIsNotNone(course.id, "Course should be created and have an ID.")
                self.assertEqual(final_count, initial_count + 1, "Course count should increase by 1.")
            except Exception as e:
                transaction.set_rollback(True)
                self.fail(f"Unexpected error: {str(e)}")

    def C_ADD_NA_06_course_name_has_50_characters_SUCCESS(self):
        with transaction.atomic():
            try:
                print("\n🔍 C-ADD-NA-06: course_name has 50 characters - SUCCESS")
                initial_count = Courses.objects.count()
                course_name = "Advanced Topics in Software Testing and QA Methods"
                self.assertEqual(len(course_name), 50, "course_name must be exactly 50 characters")

                course = Courses.objects.create(course_name=course_name)
                final_count = Courses.objects.count()

                self.assertEqual(final_count, initial_count + 1, "Course count should increase by 1")
                self.assertEqual(course.course_name, course_name, "Course name should match the input")
                print("✅ Course created successfully with valid 50-character name.")
            except Exception as e:
                transaction.set_rollback(True)
                self.fail(f"Course creation failed unexpectedly: {e}")

    def C_ADD_NA_07_course_name_has_51_characters_ERROR(self):
        with transaction.atomic():
            try:
                print("\n🔍 C-ADD-NA-07: course_name has 51 characters - ERROR")
                initial_count = Courses.objects.count()
                course_name = "Comprehensive Guide to Software Testing Techniques"
                self.assertEqual(len(course_name), 51, "course_name must be exactly 51 characters")

                Courses.objects.create(course_name=course_name)
                self.fail("Course should not be created with course_name of 51 characters.")
            except Exception as e:
                transaction.set_rollback(True)
                print(f"✅ Expected error caught: {str(e)}")

            final_count = Courses.objects.count()
            self.assertEqual(final_count, initial_count, "Course count should not change when creation fails.")


    def C_ADD_NA_08_course_name_contains_special_character_ERROR(self):
        with transaction.atomic():
            try:
                print("\n🔍 C-ADD-NA-08: course_name contains special character - ERROR")
                initial_count = Courses.objects.count()
                course_name = "AI@"  # Contains special character

                Courses.objects.create(course_name=course_name)
                self.fail("Course should not be created with special character in course_name.")
            except Exception as e:
                transaction.set_rollback(True)
                print(f"✅ Expected error caught: {str(e)}")

            final_count = Courses.objects.count()
            self.assertEqual(final_count, initial_count, "Course count should not change when creation fails.")

    def C_ADD_NA_09_course_name_is_duplicated_ERROR(self):
        print("\n🔍 C-ADD-NA-09: course_name is duplicated - ERROR")
        course_name = "BA"

        # Pre-condition setup
        try:
            Courses.objects.create(course_name=course_name)
        except Exception as e:
            self.fail(f"Precondition failed: Could not create initial course: {e}")

        with transaction.atomic():
            try:
                initial_count = Courses.objects.count()
                Courses.objects.create(course_name=course_name)
                self.fail("Course should not be created with duplicated course_name.")
            except Exception as e:
                transaction.set_rollback(True)
                print(f"✅ Expected duplication error caught: {str(e)}")

            final_count = Courses.objects.count()
            self.assertEqual(final_count, initial_count, "Course count should not change when duplicate creation fails.")