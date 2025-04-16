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

    def test_C1_empty_course_name(self):
        """C1: course_name is empty -> expect failure."""
        print("\n" + "*"*100)
        print("\n🔍 TEST C1: COURSE NAME IS EMPTY")
        print("*"*100 + "\n")

        course_name = ""
        
        initial_state = self.get_db_state("Initial State")
        self.print_db_state(initial_state, "INITIAL STATE")

        print("\n📌 Trying to create course with:")
        print(f"  - Name: '{course_name}' (empty string)\n")

        try:
            Courses.objects.create(course_name=course_name)
            self.fail("❌ TEST RESULT: FAILURE — Course should not have been created with empty name.\n")
        except Exception as e:
            print("✅ TEST RESULT: SUCCESS — Creation failed as expected.")
            print(f"  - Error: {str(e)}\n")
    
    def test_C2_course_name_1_char(self):
        """C2: course_name has 1 character -> expect failure."""
        print("\n" + "*"*100)
        print("\n🔍 TEST C2: COURSE NAME HAS 1 CHARACTER")
        print("*"*100 + "\n")

        course_name = "A"
        initial_state = self.get_db_state("Initial State")
        self.print_db_state(initial_state, "INITIAL STATE")

        print("\n📌 Trying to create course with:")
        print(f"  - Name: '{course_name}'\n")

        try:
            Courses.objects.create(course_name=course_name)
            self.fail("❌ TEST RESULT: FAILURE — Course should not have been created with 1 character.\n")
        except Exception as e:
            print("✅ TEST RESULT: SUCCESS — Creation failed as expected.")
            print(f"  - Error: {str(e)}\n")

    def test_C3_course_name_2_chars(self):
        """C3: course_name has 2 characters -> expect success."""
        print("\n" + "*"*100)
        print("\n🔍 TEST C3: COURSE NAME HAS 2 CHARACTERS")
        print("*"*100 + "\n")

        course_name = "BA"
        initial_state = self.get_db_state("Initial State")
        self.print_db_state(initial_state, "INITIAL STATE")

        print("\n📌 Creating course with:")
        print(f"  - Name: {course_name}\n")

        course = Courses.objects.create(course_name=course_name)

        post_state = self.get_db_state("After Creation")
        self.print_db_state(post_state, "AFTER CREATION")

        self.assertEqual(course.course_name, course_name)
        print("\n✅ TEST RESULT: SUCCESS")
        print(f"  - Course created with ID: {course.id}")
        print(f"  - Name: {course.course_name}\n")

    def test_C4_course_name_3_chars(self):
        """C4: course_name has 3 characters -> expect success."""
        print("\n" + "*"*100)
        print("\n🔍 TEST C4: COURSE NAME HAS 3 CHARACTERS")
        print("*"*100 + "\n")

        course_name = "IT1"
        initial_state = self.get_db_state("Initial State")
        self.print_db_state(initial_state, "INITIAL STATE")

        print("\n📌 Creating course with:")
        print(f"  - Name: {course_name}\n")

        course = Courses.objects.create(course_name=course_name)

        post_state = self.get_db_state("After Creation")
        self.print_db_state(post_state, "AFTER CREATION")

        self.assertEqual(course.course_name, course_name)
        print("\n✅ TEST RESULT: SUCCESS")
        print(f"  - Course created with ID: {course.id}")
        print(f"  - Name: {course.course_name}\n")

    def test_C5_course_name_49_chars(self):
        """C5: course_name has 49 characters -> expect success."""
        print("\n" + "*"*100)
        print("\n🔍 TEST C5: COURSE NAME HAS 49 CHARACTERS")
        print("*"*100 + "\n")

        course_name = "Introduction tSoftware Quality Assurance Concepts"
        self.assertEqual(len(course_name), 49)

        initial_state = self.get_db_state("Initial State")
        self.print_db_state(initial_state, "INITIAL STATE")

        print("\n📌 Creating course with:")
        print(f"  - Name: {course_name} ({len(course_name)} characters)\n")

        course = Courses.objects.create(course_name=course_name)

        post_state = self.get_db_state("After Creation")
        self.print_db_state(post_state, "AFTER CREATION")

        self.assertEqual(course.course_name, course_name)
        print("\n✅ TEST RESULT: SUCCESS")
        print(f"  - Course created with ID: {course.id}")
        print(f"  - Name: {course.course_name}\n")

    def test_C6_course_name_50_chars(self):
        """C6: course_name has 50 characters -> expect success."""
        print("\n" + "*"*100)
        print("\n🔍 TEST C6: COURSE NAME HAS 50 CHARACTERS")
        print("*"*100 + "\n")

        course_name = "Advanced Topics in Software Testing and QA Methods"
        self.assertEqual(len(course_name), 50)

        initial_state = self.get_db_state("Initial State")
        self.print_db_state(initial_state, "INITIAL STATE")

        print("\n📌 Creating course with:")
        print(f"  - Name: {course_name} ({len(course_name)} characters)\n")

        course = Courses.objects.create(course_name=course_name)

        post_state = self.get_db_state("After Creation")
        self.print_db_state(post_state, "AFTER CREATION")

        self.assertEqual(course.course_name, course_name)
        print("\n✅ TEST RESULT: SUCCESS")
        print(f"  - Course created with ID: {course.id}")
        print(f"  - Name: {course.course_name}\n")
    
    def test_C7_course_name_51_chars(self):
        """C7: course_name has 51 characters -> expect failure."""
        print("\n" + "*"*100)
        print("\n🔍 TEST C7: COURSE NAME HAS 51 CHARACTERS")
        print("*"*100 + "\n")

        course_name = "Comprehensive Guide too Software Testing Techniques"
        self.assertEqual(len(course_name), 51)

        initial_state = self.get_db_state("Initial State")
        self.print_db_state(initial_state, "INITIAL STATE")

        print("\n📌 Trying to create course with:")
        print(f"  - Name: {course_name} ({len(course_name)} characters)\n")

        try:
            Courses.objects.create(course_name=course_name)
            self.fail("❌ TEST RESULT: FAILURE — Course should not be created with 51 characters.\n")
        except Exception as e:
            print("✅ TEST RESULT: SUCCESS — Creation failed as expected.")
            print(f"  - Error: {str(e)}\n")

    def test_C8_course_name_with_special_char(self):
        """C8: course_name contains special character -> expect failure."""
        print("\n" + "*"*100)
        print("\n🔍 TEST C8: COURSE NAME CONTAINS SPECIAL CHARACTER")
        print("*"*100 + "\n")

        course_name = "AI@"

        initial_state = self.get_db_state("Initial State")
        self.print_db_state(initial_state, "INITIAL STATE")

        print("\n📌 Trying to create course with:")
        print(f"  - Name: {course_name}\n")

        try:
            Courses.objects.create(course_name=course_name)
            self.fail("❌ TEST RESULT: FAILURE — Course should not be created with special character.\n")
        except Exception as e:
            print("✅ TEST RESULT: SUCCESS — Creation failed as expected.")
            print(f"  - Error: {str(e)}\n")

    def test_C9_course_name_duplicate(self):
        """C9: course_name is duplicated -> expect failure."""
        print("\n" + "*"*100)
        print("\n🔍 TEST C9: DUPLICATE COURSE NAME")
        print("*"*100 + "\n")

        course_name = "BA"

        print(f"\n📌 Creating initial course with name: {course_name}")
        Courses.objects.create(course_name=course_name)
        print("✅ Initial course created.")

        print(f"\n📌 Trying to create duplicate course with same name: {course_name}")
        try:
            Courses.objects.create(course_name=course_name)
            self.fail("❌ TEST RESULT: FAILURE — Duplicate course should not be created.\n")
        except Exception as e:
            print("✅ TEST RESULT: SUCCESS — Duplicate creation failed as expected.")
            print(f"  - Error: {str(e)}\n")