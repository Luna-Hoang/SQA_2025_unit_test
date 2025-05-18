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
        print("\n" + "*"*100)
        print("\n🔍 C-ADD-NA-01: course_name has empty string - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        course_name = ""
        description = "Detect errors in student management"

        pre_creation_state = self.get_db_state('Before Creating Course')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating course with:")
        print(f"  - Course name: '{course_name}' (empty string)")
        print(f"  - Description: {description}\n")

        error_caught = False
        error_message = None

        try:
            Courses.objects.create(course_name=course_name)
            self.fail("❌ TEST RESULT: FAILED — Course should not have been created with empty course_name.\n")
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"✅ Expected error caught: {error_message}")
            connection.rollback()

        post_creation_state = self.get_db_state('After Attempting to Create Course')
        self.print_db_state(post_creation_state, "AFTER CREATION")

        if error_caught and post_creation_state['courses_count'] == pre_creation_state['courses_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Course was not created due to empty course_name as expected")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            if not error_caught:
                print("  - No error caught for empty course_name")
            else:
                print("  - Course count changed unexpectedly")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Course creation should fail when course_name is empty")

    def C_ADD_NA_02_course_name_has_1_character_ERROR(self):
        print("\n" + "*"*100)
        print("\n🔍 C-ADD-NA-02: course_name has 1 character - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        course_name = "A"
        description = "Course name too short"

        pre_creation_state = self.get_db_state('Before Creating Course')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating course with:")
        print(f"  - Course name: '{course_name}' (1 character)")
        print(f"  - Description: {description}\n")

        error_caught = False
        error_message = None

        try:
            Courses.objects.create(course_name=course_name)
            self.fail("❌ TEST RESULT: FAILED — Course should not have been created with course_name of 1 character.\n")
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"✅ Expected error caught: {error_message}")
            connection.rollback()

        post_creation_state = self.get_db_state('After Attempting to Create Course')
        self.print_db_state(post_creation_state, "AFTER CREATION")

        if error_caught and post_creation_state['courses_count'] == pre_creation_state['courses_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Course was not created due to course_name being too short (1 character)")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            if not error_caught:
                print("  - No error caught for short course_name")
            else:
                print("  - Course count changed unexpectedly")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Course creation should fail when course_name is less than 2 characters")

    def C_ADD_NA_03_course_name_has_2_characters_SUCCESS(self):
        print("\n" + "*"*100)
        print("\n🔍 C-ADD-NA-03: course_name has 2 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        course_name = "AI"
        description = "Course with minimum valid name length"

        pre_creation_state = self.get_db_state('Before Creating Course')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating course with:")
        print(f"  - Course name: '{course_name}' (2 characters)")
        print(f"  - Description: {description}\n")

        course = None
        error_caught = False
        error_message = None

        try:
            course = Courses.objects.create(course_name=course_name, description=description)
            print(f"✅ Course created successfully: {course}")
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"❌ ERROR: {error_message}")
            connection.rollback()

        post_creation_state = self.get_db_state('After Creating Course')
        self.print_db_state(post_creation_state, "AFTER CREATION")

        if not error_caught and post_creation_state['courses_count'] > pre_creation_state['courses_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print(f"  - Course created with name: {course.course_name}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Could not create course with valid 2-character name")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Course should have been created with course_name of 2 characters")

    def C_ADD_NA_04_course_name_has_3_characters_SUCCESS(self):
        print("\n" + "*"*100)
        print("\n🔍 C-ADD-NA-04: course_name has 3 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        course_name = "IT1"
        description = "Valid course name with 3 characters"

        pre_creation_state = self.get_db_state('Before Creating Course')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating course with:")
        print(f"  - Course name: '{course_name}' (3 characters)")
        print(f"  - Description: {description}\n")

        course = None
        error_caught = False
        error_message = None

        try:
            course = Courses.objects.create(course_name=course_name, description=description)
            print(f"✅ Course created successfully: {course}")
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"❌ ERROR: {error_message}")
            connection.rollback()

        post_creation_state = self.get_db_state('After Creating Course')
        self.print_db_state(post_creation_state, "AFTER CREATION")

        if not error_caught and post_creation_state['courses_count'] > pre_creation_state['courses_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print(f"  - Course created with name: {course.course_name}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Could not create course with valid 3-character name")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Course should have been created with course_name of 3 characters")

    def C_ADD_NA_05_course_name_has_49_characters_SUCCESS(self):
        print("\n" + "*"*100)
        print("\n🔍 C-ADD-NA-05: course_name has 49 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        course_name = "Introduction to Software Quality Assurance Concepts"
        description = "Course name with 49 characters"

        pre_creation_state = self.get_db_state('Before Creating Course')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating course with:")
        print(f"  - Course name: '{course_name}' ({len(course_name)} characters)")
        print(f"  - Description: {description}\n")

        course = None
        error_caught = False
        error_message = None

        try:
            course = Courses.objects.create(course_name=course_name, description=description)
            print(f"✅ Course created successfully: {course}")
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"❌ ERROR: {error_message}")
            connection.rollback()

        post_creation_state = self.get_db_state('After Creating Course')
        self.print_db_state(post_creation_state, "AFTER CREATION")

        if not error_caught and post_creation_state['courses_count'] > pre_creation_state['courses_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print(f"  - Course created with name: {course.course_name}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Could not create course with valid 49-character name")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Course should have been created with course_name of 49 characters")

    def C_ADD_NA_06_course_name_has_50_characters_SUCCESS(self):
        print("\n" + "*"*100)
        print("\n🔍 C-ADD-NA-06: course_name has 50 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        course_name = "Advanced Topics in Software Testing and QA Methods"
        description = "Course name with 50 characters"

        pre_creation_state = self.get_db_state('Before Creating Course')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating course with:")
        print(f"  - Course name: '{course_name}' ({len(course_name)} characters)")
        print(f"  - Description: {description}\n")

        course = None
        error_caught = False
        error_message = None

        try:
            course = Courses.objects.create(course_name=course_name, description=description)
            print(f"✅ Course created successfully: {course}")
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"❌ ERROR: {error_message}")
            connection.rollback()

        post_creation_state = self.get_db_state('After Creating Course')
        self.print_db_state(post_creation_state, "AFTER CREATION")

        if not error_caught and post_creation_state['courses_count'] > pre_creation_state['courses_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print(f"  - Course created with name: {course.course_name}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Could not create course with valid 50-character name")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Course should have been created with course_name of 50 characters")

    def C_ADD_NA_07_course_name_has_51_characters_ERROR(self):
        print("\n" + "*"*100)
        print("\n🔍 C-ADD-NA-07: course_name has 51 characters - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        course_name = "Comprehensive Guide to Software Testing Techniques"  # 51 characters
        description = "Course name too long"

        pre_creation_state = self.get_db_state('Before Creating Course')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating course with:")
        print(f"  - Course name: '{course_name}' ({len(course_name)} characters)")
        print(f"  - Description: {description}\n")

        error_caught = False
        error_message = None

        try:
            Courses.objects.create(course_name=course_name, description=description)
            self.fail("❌ TEST RESULT: FAILED — Course should not have been created with course_name of 51 characters.\n")
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"✅ Expected error caught: {error_message}")
            connection.rollback()

        post_creation_state = self.get_db_state('After Attempting to Create Course')
        self.print_db_state(post_creation_state, "AFTER CREATION")

        if error_caught and post_creation_state['courses_count'] == pre_creation_state['courses_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Course was not created due to course_name being too long (51 characters)")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            if not error_caught:
                print("  - No error caught for long course_name")
            else:
                print("  - Course count changed unexpectedly")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Course creation should fail when course_name is more than 50 characters")

    def C_ADD_NA_08_course_name_contains_special_character_ERROR(self):
        print("\n" + "*"*100)
        print("\n🔍 C-ADD-NA-08: course_name contains special character - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        course_name = "AI@"  # Contains special character "@"
        description = "Course name contains invalid special character"

        pre_creation_state = self.get_db_state('Before Creating Course')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating course with:")
        print(f"  - Course name: '{course_name}'")
        print(f"  - Description: {description}\n")

        error_caught = False
        error_message = None

        try:
            Courses.objects.create(course_name=course_name, description=description)
            self.fail("❌ TEST RESULT: FAILED — Course should not have been created with special characters in course_name.\n")
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"✅ Expected error caught: {error_message}")
            connection.rollback()

        post_creation_state = self.get_db_state('After Attempting to Create Course')
        self.print_db_state(post_creation_state, "AFTER CREATION")

        if error_caught and post_creation_state['courses_count'] == pre_creation_state['courses_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Course was not created due to special character in course_name")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            if not error_caught:
                print("  - No error caught for course_name with special characters")
            else:
                print("  - Course count changed unexpectedly")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Course creation should fail when course_name contains special characters")

    def C_ADD_NA_09_course_name_is_duplicated_ERROR(self):
        print("\n" + "*"*100)
        print("\n🔍 C-ADD-NA-09: course_name is duplicated - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        course_name = "BA"
        description = "Business Analysis Fundamentals"

        # Đảm bảo course_name 'BA' đã tồn tại trước đó
        print("\n📌 Pre-creating course with name 'BA' to simulate duplication...")
        try:
            Courses.objects.create(course_name=course_name, description="Initial course for duplication test")
            print("✅ Pre-creation successful.")
        except Exception as e:
            print(f"⚠️ Failed to pre-create course: {e}")
            self.fail("Pre-condition failed: could not create initial course for duplication test.")

        pre_creation_state = self.get_db_state('Before Creating Duplicated Course')
        self.print_db_state(pre_creation_state, "BEFORE DUPLICATE CREATION")

        print("\n📌 Attempting to create duplicated course with:")
        print(f"  - Course name: '{course_name}' (duplicated)")
        print(f"  - Description: {description}\n")

        error_caught = False
        error_message = None

        try:
            Courses.objects.create(course_name=course_name, description=description)
            self.fail("❌ TEST RESULT: FAILED — Course should not have been created with duplicated course_name.\n")
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"✅ Expected duplication error caught: {error_message}")
            connection.rollback()

        post_creation_state = self.get_db_state('After Attempting to Create Duplicated Course')
        self.print_db_state(post_creation_state, "AFTER CREATION")

        if error_caught and post_creation_state['courses_count'] == pre_creation_state['courses_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Course was not created because course_name was duplicated")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            if not error_caught:
                print("  - No error caught for duplicated course_name")
            else:
                print("  - Course count changed unexpectedly")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Course creation should fail when course_name is duplicated")

    def C_ADD_ID_01_course_id_has_empty_string_ERROR(self):
        print("\n" + "*"*100)
        print("\n🔍 C-ADD-ID-01: course_id has empty string - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        course_name = "Data Analysis"
        course_id = ""
        description = "Course ID is missing"

        pre_creation_state = self.get_db_state('Before Creating Course')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Attempting to create course with:")
        print(f"  - Course name: '{course_name}'")
        print(f"  - Course ID: '{course_id}' (empty)")
        print(f"  - Description: {description}\n")

        error_caught = False
        error_message = None

        try:
            Courses.objects.create(course_name=course_name, course_id=course_id, description=description)
            self.fail("❌ TEST RESULT: FAILED — Course should not have been created with empty course_id.\n")
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"✅ Expected error caught: {error_message}")
            connection.rollback()

        post_creation_state = self.get_db_state('After Attempting to Create Course')
        self.print_db_state(post_creation_state, "AFTER CREATION")

        if error_caught and post_creation_state['courses_count'] == pre_creation_state['courses_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Course was not created due to empty course_id")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            if not error_caught:
                print("  - No error caught for empty course_id")
            else:
                print("  - Course count changed unexpectedly")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Course creation should fail when course_id is empty")

    def C_ADD_ID_02_course_id_has_no_digit_ERROR(self):
        print("\n" + "*"*100)
        print("\n🔍 C-ADD-ID-02: course_id has no digit – ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        course_name = "Data Science Basics"
        course_id = "C"  # Không có số theo yêu cầu
        description = "course_id must follow format C + 3 digits"

        pre_creation_state = self.get_db_state('Before Creating Course')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Attempting to create course with:")
        print(f"  - Course name: '{course_name}'")
        print(f"  - Course ID: '{course_id}' (no digits)")
        print(f"  - Description: {description}\n")

        error_caught = False
        error_message = None

        try:
            Courses.objects.create(course_name=course_name, course_id=course_id, description=description)
            self.fail("❌ TEST RESULT: FAILED — Course should not have been created with course_id missing digits.\n")
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"✅ Expected error caught: {error_message}")
            connection.rollback()

        post_creation_state = self.get_db_state('After Attempting to Create Course')
        self.print_db_state(post_creation_state, "AFTER CREATION")

        if error_caught and post_creation_state['courses_count'] == pre_creation_state['courses_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Course was not created due to invalid course_id format (no digits)")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            if not error_caught:
                print("  - No error caught for invalid course_id format")
            else:
                print("  - Course count changed unexpectedly")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Course creation should fail when course_id does not have 3 digits after 'C'")

    def C_ADD_ID_03_course_id_has_2_digits_ERROR(self):
        print("\n" + "*"*100)
        print("\n🔍 C-ADD-ID-03: course_id has 2 digits – ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        course_name = "Software Engineering Basics"
        course_id = "C12"  # Chỉ có 2 chữ số, thiếu 1 chữ số để đúng định dạng
        description = "course_id must start with 'C' followed by exactly 3 digits"

        pre_creation_state = self.get_db_state('Before Creating Course')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Attempting to create course with:")
        print(f"  - Course name: '{course_name}'")
        print(f"  - Course ID: '{course_id}' (only 2 digits after 'C')")
        print(f"  - Description: {description}\n")

        error_caught = False
        error_message = None

        try:
            Courses.objects.create(course_name=course_name, course_id=course_id, description=description)
            self.fail("❌ TEST RESULT: FAILED — Course should not have been created with course_id of 2 digits.\n")
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"✅ Expected error caught: {error_message}")
            connection.rollback()

        post_creation_state = self.get_db_state('After Attempting to Create Course')
        self.print_db_state(post_creation_state, "AFTER CREATION")

        if error_caught and post_creation_state['courses_count'] == pre_creation_state['courses_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Course was not created due to invalid course_id format (only 2 digits after 'C')")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            if not error_caught:
                print("  - No error caught for invalid course_id format")
            else:
                print("  - Course count changed unexpectedly")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Course creation should fail when course_id does not have exactly 3 digits after 'C'")

    def C_ADD_ID_04_course_id_has_3_digits_SUCCESS(self):
        print("\n" + "*"*100)
        print("\n🔍 C-ADD-ID-04: course_id has 3 digits – SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        course_name = "Software Engineering Basics"
        course_id = "C123"  # đúng định dạng: C + 3 chữ số
        description = "Valid course_id with 3 digits"

        pre_creation_state = self.get_db_state('Before Creating Course')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating course with:")
        print(f"  - Course name: '{course_name}'")
        print(f"  - Course ID: '{course_id}' (3 digits after 'C')")
        print(f"  - Description: {description}\n")

        error_caught = False
        course = None

        try:
            course = Courses.objects.create(course_name=course_name, course_id=course_id, description=description)
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"❌ Unexpected error caught: {error_message}")
            connection.rollback()

        post_creation_state = self.get_db_state('After Creating Course')
        self.print_db_state(post_creation_state, "AFTER CREATION")

        if not error_caught and post_creation_state['courses_count'] == pre_creation_state['courses_count'] + 1:
            print("\n🟢 TEST RESULT: PASSED")
            print(f"  - Course created successfully with ID: {course.id}")
            print(f"  - Course name: {course.course_name}")
            print(f"  - Course ID: {course.course_id}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            if error_caught:
                print(f"  - Error: {error_message}")
            else:
                print("  - Course count did not increase as expected")
            self.fail("Course creation should succeed when course_id has exactly 3 digits after 'C'")

    def C_ADD_ID_05_course_id_has_4_digits_ERROR(self):
        print("\n" + "*"*100)
        print("\n🔍 C-ADD-ID-05: course_id has 4 digits - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        course_name = "Advanced Software Engineering"
        course_id = "C1234"  # Sai định dạng: có 4 chữ số thay vì 3
        description = "course_id has 4 digits which is invalid"

        pre_creation_state = self.get_db_state('Before Creating Course')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating course with:")
        print(f"  - Course name: '{course_name}'")
        print(f"  - Course ID: '{course_id}' (4 digits after 'C')")
        print(f"  - Description: {description}\n")

        error_caught = False
        error_message = None

        try:
            Courses.objects.create(course_name=course_name, course_id=course_id, description=description)
            self.fail("❌ TEST RESULT: FAILED — Course should NOT be created with invalid course_id of 4 digits.\n")
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"✅ Expected error caught: {error_message}")
            connection.rollback()

        post_creation_state = self.get_db_state('After Attempting to Create Course')
        self.print_db_state(post_creation_state, "AFTER CREATION")

        if error_caught and post_creation_state['courses_count'] == pre_creation_state['courses_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Course was not created due to invalid course_id format (4 digits)")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            if not error_caught:
                print("  - No error caught for invalid course_id format")
            else:
                print("  - Course count changed unexpectedly")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Course creation should fail when course_id has 4 digits instead of 3")

    def C_ADD_ID_06_course_id_has_non_digit_characters_ERROR(self):
        print("\n" + "*"*100)
        print("\n🔍 C-ADD-ID-06: course_id has non-digit characters - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        course_name = "Software Engineering Basics"
        course_id = "C1A-"  # course_id có ký tự không phải chữ số
        description = "course_id contains non-digit characters after 'C'"

        pre_creation_state = self.get_db_state('Before Creating Course')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating course with:")
        print(f"  - Course name: '{course_name}'")
        print(f"  - Course ID: '{course_id}' (contains non-digit characters)")
        print(f"  - Description: {description}\n")

        error_caught = False
        error_message = None

        try:
            Courses.objects.create(course_name=course_name, course_id=course_id, description=description)
            self.fail("❌ TEST RESULT: FAILED — Course should NOT be created with course_id containing non-digit characters.\n")
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"✅ Expected error caught: {error_message}")
            connection.rollback()

        post_creation_state = self.get_db_state('After Attempting to Create Course')
        self.print_db_state(post_creation_state, "AFTER CREATION")

        if error_caught and post_creation_state['courses_count'] == pre_creation_state['courses_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Course was not created due to invalid course_id with non-digit characters")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            if not error_caught:
                print("  - No error caught for invalid course_id format")
            else:
                print("  - Course count changed unexpectedly")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Course creation should fail when course_id contains non-digit characters")

    def C_ADD_ID_07_course_id_has_lowercase_letter_ERROR(self):
        print("\n" + "*"*100)
        print("\n🔍 C-ADD-ID-07: course_id has lowercase letter - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        course_name = "Database Fundamentals"
        course_id = "c123"  # course_id có chữ cái viết thường
        description = "course_id contains lowercase letter"

        pre_creation_state = self.get_db_state('Before Creating Course')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating course with:")
        print(f"  - Course name: '{course_name}'")
        print(f"  - Course ID: '{course_id}' (contains lowercase letter)")
        print(f"  - Description: {description}\n")

        error_caught = False
        error_message = None

        try:
            Courses.objects.create(course_name=course_name, course_id=course_id, description=description)
            self.fail("❌ TEST RESULT: FAILED — Course should NOT be created with course_id containing lowercase letter.\n")
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"✅ Expected error caught: {error_message}")
            connection.rollback()

        post_creation_state = self.get_db_state('After Attempting to Create Course')
        self.print_db_state(post_creation_state, "AFTER CREATION")

        if error_caught and post_creation_state['courses_count'] == pre_creation_state['courses_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Course was not created due to invalid course_id containing lowercase letter")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            if not error_caught:
                print("  - No error caught for invalid course_id format")
            else:
                print("  - Course count changed unexpectedly")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Course creation should fail when course_id contains lowercase letters")

    def C_ADD_ID_08_course_id_has_three_zero_digits_ERROR(self):
        print("\n" + "*"*100)
        print("\n🔍 C-ADD-ID-08: course_id has 3 digits are zero - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        course_name = "Network Security"
        course_id = "C000"  # 3 số 0, không hợp lệ
        description = "course_id has 3 digits all zero"

        pre_creation_state = self.get_db_state('Before Creating Course')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating course with:")
        print(f"  - Course name: '{course_name}'")
        print(f"  - Course ID: '{course_id}' (3 zero digits)")
        print(f"  - Description: {description}\n")

        error_caught = False
        error_message = None

        try:
            Courses.objects.create(course_name=course_name, course_id=course_id, description=description)
            self.fail("❌ TEST RESULT: FAILED — Course should NOT be created with course_id having three zero digits.\n")
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"✅ Expected error caught: {error_message}")
            connection.rollback()

        post_creation_state = self.get_db_state('After Attempting to Create Course')
        self.print_db_state(post_creation_state, "AFTER CREATION")

        if error_caught and post_creation_state['courses_count'] == pre_creation_state['courses_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Course was not created due to invalid course_id 'C000'")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            if not error_caught:
                print("  - No error caught for invalid course_id 'C000'")
            else:
                print("  - Course count changed unexpectedly")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Course creation should fail when course_id has three zero digits")

    def C_ADD_ID_09_course_id_has_three_nine_digits_SUCCESS(self):
        print("\n" + "*"*100)
        print("\n🔍 C-ADD-ID-09: course_id has 3 digits are 9 - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        course_name = "Advanced Database Systems"
        course_id = "C999"  # 3 số 9, hợp lệ
        description = "course_id with three 9 digits"

        pre_creation_state = self.get_db_state('Before Creating Course')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating course with:")
        print(f"  - Course name: '{course_name}'")
        print(f"  - Course ID: '{course_id}' (3 nine digits)")
        print(f"  - Description: {description}\n")

        course = None
        error_caught = False
        error_message = None

        try:
            course = Courses.objects.create(course_name=course_name, course_id=course_id, description=description)
            connection.commit()
            print("✅ Course created successfully.")
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"❌ Unexpected error caught: {error_message}")
            connection.rollback()

        post_creation_state = self.get_db_state('After Creating Course')
        self.print_db_state(post_creation_state, "AFTER CREATION")

        if not error_caught and post_creation_state['courses_count'] == pre_creation_state['courses_count'] + 1:
            print("\n🟢 TEST RESULT: PASSED")
            print(f"  - Course created with ID: {course.course_id}")
            print(f"  - Course name: {course.course_name}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            if error_caught:
                print(f"  - Error: {error_message}")
            else:
                print("  - Course count did not increase as expected.")
            self.fail("Course creation should succeed with valid course_id 'C999'")

    def C_ADD_ID_10_course_id_contains_whitespace_ERROR(self):
        print("\n" + "*"*100)
        print("\n🔍 C-ADD-ID-10: course_id contains whitespace – ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        course_name = "Database Systems"
        course_id = "C 12"  # course_id có khoảng trắng, sai định dạng
        description = "course_id contains whitespace"

        pre_creation_state = self.get_db_state('Before Creating Course')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating course with:")
        print(f"  - Course name: '{course_name}'")
        print(f"  - Course ID: '{course_id}' (contains whitespace)")
        print(f"  - Description: {description}\n")

        error_caught = False
        error_message = None

        try:
            Courses.objects.create(course_name=course_name, course_id=course_id, description=description)
            self.fail("❌ TEST RESULT: FAILED — Course should not have been created with whitespace in course_id.\n")
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"✅ Expected error caught: {error_message}")
            connection.rollback()

        post_creation_state = self.get_db_state('After Attempting to Create Course')
        self.print_db_state(post_creation_state, "AFTER CREATION")

        if error_caught and post_creation_state['courses_count'] == pre_creation_state['courses_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Course was not created due to whitespace in course_id")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            if not error_caught:
                print("  - No error caught for whitespace in course_id")
            else:
                print("  - Course count changed unexpectedly")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Course creation should fail when course_id contains whitespace")

    def C_ADD_ID_11_course_id_not_start_with_C_ERROR(self):
        print("\n" + "*"*100)
        print("\n🔍 C-ADD-ID-11: course_id does not start with C - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        course_name = "Advanced Programming"
        course_id = "1234"  # không bắt đầu bằng chữ C
        description = "course_id does not start with uppercase C"

        pre_creation_state = self.get_db_state('Before Creating Course')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating course with:")
        print(f"  - Course name: '{course_name}'")
        print(f"  - Course ID: '{course_id}' (does not start with C)")
        print(f"  - Description: {description}\n")

        error_caught = False
        error_message = None

        try:
            Courses.objects.create(course_name=course_name, course_id=course_id, description=description)
            self.fail("❌ TEST RESULT: FAILED — Course should not have been created with course_id not starting with 'C'.\n")
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"✅ Expected error caught: {error_message}")
            connection.rollback()

        post_creation_state = self.get_db_state('After Attempting to Create Course')
        self.print_db_state(post_creation_state, "AFTER CREATION")

        if error_caught and post_creation_state['courses_count'] == pre_creation_state['courses_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Course was not created because course_id does not start with uppercase 'C'")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            if not error_caught:
                print("  - No error caught for invalid course_id start character")
            else:
                print("  - Course count changed unexpectedly")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Course creation should fail when course_id does not start with uppercase 'C'")

    def C_ADD_ID_012_course_id_is_duplicated_ERROR(self):
        print("\n" + "*"*100)
        print("\n🔍 C-ADD-ID-012: course_id is duplicated - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        course_name = "Sample Course"
        course_id = "C123"
        description = "Duplicate course_id test"

        # Giả sử trong DB đã có course với course_id = "C123"
        # Ta tạo trước một course để có dữ liệu trùng lặp
        try:
            Courses.objects.create(course_name="Existing Course", course_id=course_id, description="Existing course for duplicate test")
            print("✅ Setup: Existing course with course_id='C123' created.")
        except Exception as e:
            print(f"⚠️ Setup warning: {str(e)}")
            connection.rollback()

        pre_creation_state = self.get_db_state('Before Creating Duplicate Course')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Attempting to create course with duplicated course_id:")
        print(f"  - Course name: '{course_name}'")
        print(f"  - Course ID: '{course_id}'")
        print(f"  - Description: {description}\n")

        error_caught = False
        error_message = None

        try:
            Courses.objects.create(course_name=course_name, course_id=course_id, description=description)
            self.fail("❌ TEST RESULT: FAILED — Course should not have been created with duplicated course_id.\n")
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"✅ Expected error caught: {error_message}")
            connection.rollback()

        post_creation_state = self.get_db_state('After Attempting to Create Duplicate Course')
        self.print_db_state(post_creation_state, "AFTER CREATION")

        if error_caught and post_creation_state['courses_count'] == pre_creation_state['courses_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Duplicate course_id was correctly rejected.")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            if not error_caught:
                print("  - No error caught for duplicated course_id")
            else:
                print("  - Course count changed unexpectedly")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Course creation should fail when course_id is duplicated")