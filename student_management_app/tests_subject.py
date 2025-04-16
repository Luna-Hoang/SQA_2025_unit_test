import unittest
from django.test import TestCase
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
import re

from student_management_app.models import CustomUser, Courses, Subjects, SessionYearModel, Students, Staffs
from django.contrib.auth.models import User


class SubjectModelTest(TestCase):
    """
    Test suite for the Subject model.
    Check various scenarios when creating a new subject.
    """
    
    def setUp(self):
        """Set up test data before each method runs."""
        # Delete all existing subjects to start with a clean database
        Subjects.objects.all().delete()
        # Create a course to be used in tests
        self.course = Courses.objects.create(course_name="Test Course")
        # Create a staff user to be used in tests
        self.staff_user = CustomUser.objects.create_user(username="teststaff", password="password")
        self.staff = Staffs.objects.create(admin=self.staff_user)
        
    def tearDown(self):
        """Clean up after each test."""
        # Delete test data
        Subjects.objects.filter(subject_name__startswith="Test Subject").delete()
        CustomUser.objects.filter(username="teststaff").delete()
        Courses.objects.filter(course_name__startswith="Test Course").delete()
    
    def get_db_state(self, stage):
        """Record the current state of the database."""
        db_state = {
            'stage': stage,
            'subjects_count': Subjects.objects.count(),
            'courses_count': Courses.objects.count(),
            'users_count': CustomUser.objects.count(),
            'subjects': list(Subjects.objects.values('id', 'subject_name', 'course_id__course_name', 'staff_id__username'))
        }
        return db_state
        
    def print_db_state(self, state, label):
        """Print the DB state in a readable format."""
        subjects_info = ""
        if state.get('subjects', []):
            for subject in state['subjects']:
                subjects_info += f"\n    - ID: {subject['id']}, Subject Name: {subject['subject_name']}"
                subjects_info += f", Course: {subject['course_id__course_name']}, Instructor: {subject['staff_id__username']}"
        else:
            subjects_info = "\n    (No data)"
            
        print(f"\n{'='*80}")
        print(f"\n  📊 {label} ({state['stage']})")
        print(f"\n  📋 Number of Subjects: {state['subjects_count']}")
        print(f"\n  📋 Number of Courses: {state['courses_count']}")
        print(f"\n  📋 Number of Users: {state['users_count']}")
        print(f"\n  📝 Subject Details:{subjects_info}")
        print(f"\n{'='*80}\n")
        
    def test_1_successful_subject_creation(self):
        """Test 1: Successfully create a new subject."""
        print("\n\n" + "*"*100)
        print("\n🔍 TEST 1: SUCCESSFUL SUBJECT CREATION")
        print("*"*100 + "\n")
        
        # Get initial database state
        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")
        
        # Create a subject
        subject_name = "Mathematics"
        course_id = 1  # Assume course with ID 1 exists
        
        # Get database state before creation
        pre_creation_state = self.get_db_state('Before Subject Creation')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")
        
        print("\n📌 Creating subject with:")
        print(f"  - Name: {subject_name}")
        print(f"  - Course ID: {course_id}")
        
        # Perform subject creation
        subject = None
        error_caught = False
        error_message = None
        
        try:
            subject = Subjects.objects.create(
                subject_name=subject_name,
                course_id=Courses.objects.get(id=course_id),
                staff_id=self.staff_user
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SUBJECT: {error_message}")
        
        # Get database state after creation
        post_creation_state = self.get_db_state('After Subject Creation')
        self.print_db_state(post_creation_state, "AFTER CREATION")
        
        # Check result
        if not error_caught and subject and post_creation_state['subjects_count'] > pre_creation_state['subjects_count']:
            print("\n✅ TEST RESULT: SUCCESS")
            print(f"  - Subject created with ID: {subject.id}")
            print(f"  - Name: {subject.subject_name}")
            print(f"  - Course: {subject.course_id.course_name}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Could not create subject")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Could not create subject successfully")

    def test_2_duplicate_subject_name(self):
        """Test 2: Create subject with duplicate name."""
        print("\n\n" + "*"*100)
        print("\n🔍 TEST 2: CREATE SUBJECT WITH DUPLICATE NAME")
        print("*"*100 + "\n")
        
        # Get initial database state
        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")
        
        # Create an initial subject
        subject_name = "Physics"
        course_id = 1  # Assume course with ID 1 exists
        
        print("\n📌 Creating first subject with:")
        print(f"  - Name: {subject_name}")
        print(f"  - Course ID: {course_id}")
        
        # Create first subject
        first_subject = Subjects.objects.create(
            subject_name=subject_name,
            course_id=Courses.objects.get(id=course_id),
            staff_id=self.staff_user
        )
        
        # Get database state after first subject creation
        post_first_creation_state = self.get_db_state('After First Subject Creation')
        self.print_db_state(post_first_creation_state, "AFTER FIRST SUBJECT CREATION")
        
        print("\n📌 Attempting to create duplicate subject with:")
        print(f"  - Name: {subject_name} (same as first subject)")
        print(f"  - Course ID: {course_id}")
        
        # Attempt to create a duplicate subject
        duplicate_subject = None
        error_caught = False
        error_message = None
        
        try:
            with transaction.atomic():
                # Attempt to create a subject with the same name
                duplicate_subject = Subjects.objects.create(
                    subject_name=subject_name,
                    course_id=Courses.objects.get(id=course_id),
                    staff_id=self.staff_user
                )
                
                print("\n⚠️ ERROR DETECTED: Software allows duplicate subject creation")
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n✅ Software caught error when creating duplicate subject: {error_message}")
        
        # Get database state after attempting to create duplicate subject
        post_duplicate_attempt_state = self.get_db_state('After Attempting Duplicate Subject Creation')
        self.print_db_state(post_duplicate_attempt_state, "AFTER ATTEMPTING DUPLICATE SUBJECT CREATION")
        
        # Check if duplicate subject was blocked
        if error_caught and post_duplicate_attempt_state['subjects_count'] == post_first_creation_state['subjects_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Software prevented duplicate subject creation")
            print(f"  - Error message: {error_message}")
        else:
            # If duplicate subject was created, mark test as failed
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Software allows duplicate subject creation")
            print(f"  - Created {post_duplicate_attempt_state['subjects_count'] - post_first_creation_state['subjects_count']} additional duplicate subjects")
            
            # This test will FAIL if software does not catch duplicate error
            if post_duplicate_attempt_state['subjects_count'] > post_first_creation_state['subjects_count']:
                self.fail("Software does not check for duplicate subjects!")
            
            # Rollback DB - delete newly created duplicate subjects
            if duplicate_subject and duplicate_subject.id:
                duplicate_subject.delete()

    def test_3_missing_required_values(self):
        """Test 3: Missing required values (subjectName)."""
        print("\n\n" + "*"*100)
        print("\n🔍 TEST 3: MISSING REQUIRED VALUES")
        print("*"*100 + "\n")
        
        # Get initial database state
        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")
        
        # Get database state before creation
        pre_attempt_state = self.get_db_state('Before Creating Subject with Missing Values')
        self.print_db_state(pre_attempt_state, "BEFORE CREATING MISSING VALUES")
        
        print("\n📌 Attempting to create subject with missing values:")
        print("  - Name: NOT PROVIDED (missing required value)")
        print("  - Course ID: 1 (assumed existing)")
        
        # Attempt to create a subject with missing name
        subject = None
        error_caught = False
        error_message = None
        
        try:
            with transaction.atomic():
                # Attempt to create subject with missing required value
                subject = Subjects(
                    # Missing subject_name
                    course_id=Courses.objects.get(id=1),
                    staff_id=self.staff_user
                )
                subject.save()
                
                # If no error, subject was created despite missing required data
                print("\n⚠️ ERROR DETECTED: Software allows subject creation with missing name")
                
        except Exception as e:
            # If software catches error, record it
            error_caught = True
            error_message = str(e)
            print(f"\n✅ Software caught error when creating subject with missing values: {error_message}")
        
        # Get database state after creation
        post_attempt_state = self.get_db_state('After Creating Subject with Missing Values')
        self.print_db_state(post_attempt_state, "AFTER CREATING MISSING VALUES")
        
        # Check result
        if error_caught and post_attempt_state['subjects_count'] == pre_attempt_state['subjects_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Software prevented subject creation with missing required information")
            print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Software allows subject creation with missing required information")
            
            # This test will FAIL if software does not catch missing value error
            if post_attempt_state['subjects_count'] > pre_attempt_state['subjects_count']:
                self.fail("Software does not catch missing required value error!")
                
            # Rollback DB if needed
            if subject and subject.id:
                subject.delete()

    def test_4_subject_name_length(self):
        """Test 4: Subject name too short or too long."""
        print("\n\n" + "*"*100)
        print("\n🔍 TEST 4: SUBJECT NAME TOO SHORT OR TOO LONG")
        print("*"*100 + "\n")
        
        # Get initial database state
        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")
        
        # 4.1 Name too short (empty string)
        print("\n📌 4.1 Attempting to create subject with name too short:")
        print("  - Name: \"\" (empty string)")
        
        pre_attempt_state = self.get_db_state('Before Creating Subject with Short Name')
        self.print_db_state(pre_attempt_state, "BEFORE CREATING SHORT NAME")
        
        # Attempt to create subject with name too short
        subject_short = None
        error_caught_short = False
        error_message_short = None
        
        try:
            with transaction.atomic():
                subject_short = Subjects.objects.create(
                    subject_name="",  # Empty name
                    course_id=Courses.objects.get(id=1),
                    staff_id=self.staff_user
                )
                print("\n⚠️ ERROR DETECTED: Software allows subject creation with empty name")
        except Exception as e:
            error_caught_short = True
            error_message_short = str(e)
            print(f"\n✅ Software caught error when creating subject with empty name: {error_message_short}")
        
        post_short_attempt_state = self.get_db_state('After Creating Subject with Short Name')
        self.print_db_state(post_short_attempt_state, "AFTER CREATING SHORT NAME")
        
        # 4.2 Name too long (> 255 characters)
        print("\n📌 4.2 Attempting to create subject with name too long:")
        long_name = "A" * 256  # 256 characters, while the limit is 255
        print(f"  - Name: {long_name[:20]}... (256 characters)")
        
        pre_long_attempt_state = self.get_db_state('Before Creating Subject with Long Name')
        self.print_db_state(pre_long_attempt_state, "BEFORE CREATING LONG NAME")
        
        # Attempt to create subject with name too long
        subject_long = None
        error_caught_long = False
        error_message_long = None
        
        try:
            with transaction.atomic():
                subject_long = Subjects.objects.create(
                    subject_name=long_name,
                    course_id=Courses.objects.get(id=1),
                    staff_id=self.staff_user
                )
                print("\n⚠️ ERROR DETECTED: Software allows subject creation with name too long (> 255 characters)")
        except Exception as e:
            error_caught_long = True
            error_message_long = str(e)
            print(f"\n✅ Software caught error when creating subject with name too long: {error_message_long}")
        
        post_long_attempt_state = self.get_db_state('After Creating Subject with Long Name')
        self.print_db_state(post_long_attempt_state, "AFTER CREATING LONG NAME")
        
        # Summarize results
        if error_caught_short and post_short_attempt_state['subjects_count'] == pre_attempt_state['subjects_count'] and \
           error_caught_long and post_long_attempt_state['subjects_count'] == pre_long_attempt_state['subjects_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Software prevented subject creation with invalid name (too short/too long)")
            print(f"  - Short name error: {error_message_short}")
            print(f"  - Long name error: {error_message_long}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            if not error_caught_short:
                print("  - Software allows subject creation with empty name")
                # Rollback if needed
                if subject_short and subject_short.id:
                    subject_short.delete()
            if not error_caught_long:
                print("  - Software allows subject creation with name too long")
                # Rollback if needed
                if subject_long and subject_long.id:
                    subject_long.delete()

            # This test will FAIL if software does not catch length error
            if not (error_caught_short and error_caught_long):
                self.fail("Software does not check subject name length!")

    def test_5_invalid_course_id(self):
        """Test 5: Attempt to create a subject with an invalid courseID."""
        print("\n\n" + "*"*100)
        print("\n🔍 TEST 5: INVALID COURSEID")
        print("*"*100 + "\n")
        
        # Get initial database state
        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")
        
        # Attempt to create a subject with an invalid courseID
        subject_name = "Biology"
        invalid_course_id = 9999  # Assume this course ID does not exist
        print("\n📌 Attempting to create subject with:")
        print(f"  - Name: {subject_name}")
        print(f"  - Invalid Course ID: {invalid_course_id}")
        
        subject = None
        error_caught = False
        error_message = None
        
        try:
            with transaction.atomic():
                subject = Subjects.objects.create(
                    subject_name=subject_name,
                    course_id=Courses.objects.get(id=invalid_course_id),
                    staff_id=self.staff_user
                )
                print("\n⚠️ ERROR DETECTED: Software allows subject creation with invalid courseID")
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n✅ Software caught error when creating subject with invalid courseID: {error_message}")
        
        # Get database state after attempt
        post_attempt_state = self.get_db_state('After Attempting Invalid CourseID Creation')
        self.print_db_state(post_attempt_state, "AFTER ATTEMPTING INVALID COURSEID CREATION")
        
        # Check result
        if error_caught and post_attempt_state['subjects_count'] == initial_state['subjects_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Software prevented subject creation with invalid courseID")
            print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Software allows subject creation with invalid courseID")
            
            # This test will FAIL if software does not catch invalid courseID error
            if post_attempt_state['subjects_count'] > initial_state['subjects_count']:
                self.fail("Software does not check for invalid courseID!")
            
            # Rollback DB if needed
            if subject and subject.id:
                subject.delete()

    def test_6_invalid_subject_name_characters(self):
        """Test 6: subjectName contains invalid characters."""
        print("\n\n" + "*"*100)
        print("\n🔍 TEST 6: SUBJECTNAME CONTAINS INVALID CHARACTERS")
        print("*"*100 + "\n")
        
        # Get initial database state
        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")
        
        # Create list of subject names that may contain invalid characters
        invalid_names = [
            "Subject with <script>alert('XSS')</script> tag",  # XSS injection
            "Subject with SQL'; DROP TABLE Subject; --",       # SQL injection
            "Subject with \x00 null byte",                     # Null byte
            "Subject with control chars \n\r\t"                # Control characters
        ]
        
        # Attempt to create subject with each invalid name
        all_errors_caught = True
        error_details = []
        
        for i, name in enumerate(invalid_names):
            print(f"\n📌 {i+1}. Attempting to create subject with invalid character name:")
            print(f"  - Name: {name}")
            
            pre_attempt_state = self.get_db_state(f'Before Creating Subject with Invalid Name {i+1}')
            self.print_db_state(pre_attempt_state, f"BEFORE CREATING INVALID NAME {i+1}")
            
            invalid_subject = None
            error_caught = False
            error_message = None
            
            try:
                with transaction.atomic():
                    invalid_subject = Subjects.objects.create(
                        subject_name=name,
                        course_id=Courses.objects.get(id=1),
                        staff_id=self.staff_user
                    )
                    print(f"\n⚠️ ERROR DETECTED: Software allows subject creation with invalid character name")
                    error_details.append(f"Name {i+1}: Software allows saving '{name}'")
                    all_errors_caught = False
            except Exception as e:
                error_caught = True
                error_message = str(e)
                print(f"\n✅ Software caught error: {error_message}")
                error_details.append(f"Name {i+1}: Error caught: {error_message}")
            
            post_attempt_state = self.get_db_state(f'After Creating Subject with Invalid Name {i+1}')
            self.print_db_state(post_attempt_state, f"AFTER CREATING INVALID NAME {i+1}")
            
            # If subject was created, need to delete to not affect subsequent tests
            if invalid_subject and invalid_subject.id and post_attempt_state['subjects_count'] > pre_attempt_state['subjects_count']:
                print(f"  - Rollback: Delete invalid subject created (ID: {invalid_subject.id})")
                invalid_subject.delete()
        
        # Summarize results
        if all_errors_caught:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Software prevented subject creation with invalid character name")
            for detail in error_details:
                print(f"  - {detail}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Software allows subject creation with invalid character name")
            for detail in error_details:
                print(f"  - {detail}")
            
            # This test will FAIL if software does not catch invalid character error
            if not all_errors_caught:
                self.fail("Software does not check for invalid characters in subject name!") 