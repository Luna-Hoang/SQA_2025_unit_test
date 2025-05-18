from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta
import os
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.test.utils import override_settings
from .models import CustomUser, Students, Courses, SessionYearModel
from .forms import AddStudentForm
from django.db import connection

class StudentModelTest(TestCase):
    """
    Test suite for creating Students.
    Check various scenarios when creating a new student.
    """
    
    def setUp(self):
        """Set up test data before each method runs."""
        # Delete all existing students and users to start with a clean database
        Students.objects.all().delete()
        CustomUser.objects.filter(user_type='3').delete()
        
        # Ensure there is a Course with ID=1 (necessary for post_save signal)
        if not Courses.objects.filter(id=1).exists():
            course_id_1 = Courses.objects.create(id=1, course_name="Default Course")
            print("Created Course with ID=1 for post_save signal")
        else:
            course_id_1 = Courses.objects.get(id=1)
            print("Found existing Course with ID=1")
        
        # Ensure there is a SessionYear with ID=1 (necessary for post_save signal)
        if not SessionYearModel.objects.filter(id=1).exists():
            session_id_1 = SessionYearModel.objects.create(
                id=1,
                session_start_year=timezone.now().date(),
                session_end_year=(timezone.now() + timedelta(days=365)).date()
            )
            print("Created SessionYear with ID=1 for post_save signal")
        else:
            session_id_1 = SessionYearModel.objects.get(id=1)
            print("Found existing SessionYear with ID=1")
        
        # Save for use in tests
        self.default_course = course_id_1
        self.default_session = session_id_1
        
        # Create another course for testing
        self.course = Courses.objects.create(course_name="Test Course")
        
        # Create another academic year for testing
        self.session_year = SessionYearModel.objects.create(
            session_start_year=timezone.now().date(),
            session_end_year=(timezone.now() + timedelta(days=365)).date()
        )
    
    def get_db_state(self, stage):
        """Record the current state of the database."""
        db_state = {
            'stage': stage,
            'students_count': Students.objects.count(),
            'students': list(Students.objects.values('id', 'admin__username', 'admin__email', 'course_id__course_name', 'session_year_id__id'))
        }
        return db_state
    
    def print_db_state(self, state, label):
        """Print the DB state in a readable format."""
        students_info = ""
        if state['students']:
            for student in state['students']:
                students_info += f"\n    - ID: {student['id']}, Username: {student['admin__username']}, Email: {student['admin__email']}"
                students_info += f", Course: {student['course_id__course_name']}, Session Year ID: {student['session_year_id__id']}"
        else:
            students_info = "\n    (No data)"
            
        print(f"\n{'='*80}")
        print(f"\n  📊 {label} ({state['stage']})")
        print(f"\n  📋 Number of Students: {state['students_count']}")
        print(f"\n  📝 Details:{students_info}")
        print(f"\n{'='*80}\n")

    def STU_ADD_FN_01_first_name_empty_string_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-FN-01: first_name has empty string - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent1"
        email = "teststudent1@test.com"
        password = "Testpassword@123"
        first_name = ""  # Empty string to trigger error
        last_name = "Doe"
        gender = ""
        address = ""
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: '{first_name}' {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print(f"❌ User has linked student object, but this should not happen for empty first_name")
                student = user.students
            else:
                print(f"✅ User does not have linked student object as expected due to empty first_name")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING TEACHER: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Teacher')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Đúng ra phải không tạo được student, student_count không tăng
        if error_caught or post_creation_state['students_count'] == pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student creation failed as expected due to empty first_name")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student was created despite empty first_name")
            self.fail("Student creation should fail for empty first_name")

    def STU_ADD_FN_02_first_name_one_character_SUCCESS(self):
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-FN-02: first_name has 1 character - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent2"
        email = "teststudent2@test.com"
        password = "Testpassword@123"
        first_name = "J"  # 1 character
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: '{first_name}' {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print(f"✅ User has successfully linked student object")
                student = user.students
            else:
                print(f"❌ User does not have linked student object")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING STUDENT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if not error_caught and student and post_creation_state['students_count'] > pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student was successfully created with 1-character first_name")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student creation failed despite valid 1-character first_name")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Student creation should succeed for 1-character first_name")

    def STU_ADD_FN_03_first_name_two_characters_SUCCESS(self): 
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-FN-03: first_name has 2 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent3"
        email = "teststudent3@test.com"
        password = "Testpassword@123"
        first_name = "Jo"  # 2 characters
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: '{first_name}' {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print(f"✅ User has successfully linked student object")
                student = user.students
            else:
                print(f"❌ User does not have linked student object")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING STUDENT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if not error_caught and student and post_creation_state['students_count'] > pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student was successfully created with 2-character first_name")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student creation failed despite valid 2-character first_name")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Student creation should succeed for 2-character first_name")

    def STU_ADD_FN_04_first_name_49_characters_SUCCESS(self): 
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-FN-04: first_name has 49 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent4"
        email = "teststudent4@test.com"
        password = "Testpassword@123"
        first_name = "Johnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn"  # 49 characters
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: '{first_name}' {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print(f"✅ User has successfully linked student object")
                student = user.students
            else:
                print(f"❌ User does not have linked student object")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING STUDENT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if not error_caught and student and post_creation_state['students_count'] > pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student was successfully created with 49-character first_name")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student creation failed despite valid 49-character first_name")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Student creation should succeed for 49-character first_name")

    def STU_ADD_FN_05_first_name_50_characters_SUCCESS(self): 
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-FN-05: first_name has 50 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent5"
        email = "teststudent5@test.com"
        password = "Testpassword@123"
        first_name = "Johnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn"  # 50 characters
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: '{first_name}' {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print(f"✅ User has successfully linked student object")
                student = user.students
            else:
                print(f"❌ User does not have linked student object")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING STUDENT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if not error_caught and student and post_creation_state['students_count'] > pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student was successfully created with 50-character first_name")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student creation failed despite valid 50-character first_name")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Student creation should succeed for 50-character first_name")

    def STU_ADD_FN_06_first_name_51_characters_ERROR(self): 
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-FN-06: first_name has 51 characters - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent6"
        email = "teststudent6@test.com"
        password = "Testpassword@123"
        first_name = "Johnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn"  # 51 characters
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: '{first_name}' {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print(f"❌ User has linked student object, but this should not happen for 51-character first_name")
                student = user.students
            else:
                print(f"✅ User does not have linked student object as expected due to invalid first_name length")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n✅ Expected ERROR caught: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if error_caught or post_creation_state['students_count'] == pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student creation failed as expected due to first_name exceeding 50 characters")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student was created despite invalid 51-character first_name")
            self.fail("Student creation should fail for first_name length > 50")

    def STU_ADD_FN_07_first_name_contains_digits_ERROR(self): 
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-FN-07: first_name contains digits - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent7"
        email = "teststudent7@test.com"
        password = "Testpassword@123"
        first_name = "John111"  # Contains digits
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: '{first_name}' {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print(f"❌ User has linked student object, but this should not happen for first_name with digits")
                student = user.students
            else:
                print(f"✅ User does not have linked student object as expected due to invalid characters in first_name")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n✅ Expected ERROR caught: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if error_caught or post_creation_state['students_count'] == pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student creation failed as expected due to digits in first_name")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student was created despite invalid digits in first_name")
            self.fail("Student creation should fail when first_name contains digits")

    def STU_ADD_FN_08_first_name_contains_special_characters_ERROR(self): 
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-FN-08: first_name contains special characters - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent8"
        email = "teststudent8@test.com"
        password = "Testpassword@123"
        first_name = "John@"  # Contains special character
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: '{first_name}' {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print(f"❌ User has linked student object, but this should not happen for first_name with special characters")
                student = user.students
            else:
                print(f"✅ User does not have linked student object as expected due to invalid characters in first_name")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n✅ Expected ERROR caught: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if error_caught or post_creation_state['students_count'] == pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student creation failed as expected due to special characters in first_name")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student was created despite invalid special characters in first_name")
            self.fail("Student creation should fail when first_name contains special characters")

    def STU_ADD_LN_01_last_name_empty_string_ERROR(self): 
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-LN-01: last_name has empty string - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent_ln01"
        email = "teststudent_ln01@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = ""  # Empty string to trigger error
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} '{last_name}'")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print(f"❌ User has linked student object, but this should not happen for empty last_name")
                student = user.students
            else:
                print(f"✅ User does not have linked student object as expected due to empty last_name")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n✅ Expected ERROR caught: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if error_caught or post_creation_state['students_count'] == pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student creation failed as expected due to empty last_name")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student was created despite empty last_name")
            self.fail("Student creation should fail when last_name is empty")

    def STU_ADD_LN_02_last_name_one_character_SUCCESS(self): 
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-LN-02: last_name has 1 character - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent_ln02"
        email = "teststudent_ln02@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "S"  # 1 character
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} '{last_name}'")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print(f"✅ User has successfully linked student object")
                student = user.students
            else:
                print(f"❌ User does not have linked student object")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING STUDENT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if not error_caught and student and post_creation_state['students_count'] > pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student was successfully created with 1-character last_name")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student creation failed despite valid 1-character last_name")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Student creation should succeed for 1-character last_name")

    def STU_ADD_LN_03_last_name_two_characters_SUCCESS(self): 
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-LN-03: last_name has 2 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent_ln03"
        email = "teststudent_ln03@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "St"  # 2 characters
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} '{last_name}'")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print(f"✅ User has successfully linked student object")
                student = user.students
            else:
                print(f"❌ User does not have linked student object")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING STUDENT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if not error_caught and student and post_creation_state['students_count'] > pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student was successfully created with 2-character last_name")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student creation failed despite valid 2-character last_name")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Student creation should succeed for 2-character last_name")

    def STU_ADD_LN_04_last_name_49_characters_SUCCESS(self): 
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-LN-04: last_name has 49 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent_ln04"
        email = "teststudent_ln04@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Steveeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"  # 49 chars
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} '{last_name}'")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print(f"✅ User has successfully linked student object")
                student = user.students
            else:
                print(f"❌ User does not have linked student object")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING STUDENT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if not error_caught and student and post_creation_state['students_count'] > pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student was successfully created with 49-character last_name")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student creation failed despite valid 49-character last_name")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Student creation should succeed for 49-character last_name")

    def STU_ADD_LN_05_last_name_50_characters_SUCCESS(self): 
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-LN-05: last_name has 50 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent_ln05"
        email = "teststudent_ln05@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Steveeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"  # 50 chars
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} '{last_name}'")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print(f"✅ User has successfully linked student object")
                student = user.students
            else:
                print(f"❌ User does not have linked student object")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING STUDENT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if not error_caught and student and post_creation_state['students_count'] > pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student was successfully created with 50-character last_name")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student creation failed despite valid 50-character last_name")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Student creation should succeed for 50-character last_name")

    def STU_ADD_LN_06_last_name_51_characters_ERROR(self): 
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-LN-06: last_name has 51 characters - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent_ln06"
        email = "teststudent_ln06@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Steveeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"  # 51 chars
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} '{last_name}'")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )
            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print(f"❌ User has linked student object, but this should not happen for last_name length > 50")
                student = user.students
            else:
                print(f"✅ User does not have linked student object as expected due to last_name length > 50")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING STUDENT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Đúng ra phải không tạo được student, student_count không tăng
        if error_caught or post_creation_state['students_count'] == pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student creation failed as expected due to last_name length > 50")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student was created despite last_name length > 50")
            self.fail("Student creation should fail for last_name length > 50")

    def STU_ADD_LN_07_last_name_contains_digits_ERROR(self): 
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-LN-07: last_name contains digits - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent_ln07"
        email = "teststudent_ln07@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Steve111"  # contains digits
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} '{last_name}'")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )
            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print(f"❌ User has linked student object, but this should not happen when last_name contains digits")
                student = user.students
            else:
                print(f"✅ User does not have linked student object as expected due to digits in last_name")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING STUDENT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Đúng ra phải không tạo được student, student_count không tăng
        if error_caught or post_creation_state['students_count'] == pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student creation failed as expected due to digits in last_name")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student was created despite digits in last_name")
            self.fail("Student creation should fail for digits in last_name")

    def STU_ADD_LN_08_last_name_contains_special_chars_ERROR(self): 
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-LN-08: last_name contains special characters - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent_ln08"
        email = "teststudent_ln08@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Steve@"  # contains special character '@'
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} '{last_name}'")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )
            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print(f"❌ User has linked student object, but this should not happen when last_name contains special characters")
                student = user.students
            else:
                print(f"✅ User does not have linked student object as expected due to special characters in last_name")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING STUDENT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Đúng ra phải không tạo được student, student_count không tăng
        if error_caught or post_creation_state['students_count'] == pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student creation failed as expected due to special characters in last_name")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student was created despite special characters in last_name")
            self.fail("Student creation should fail for special characters in last_name")

    def STU_ADD_UN_01_username_empty_string_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-UN-01: user_name has empty string - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = ""  # empty username to trigger error
        email = "teststudent_un01@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: '{username}'")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )
            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print(f"❌ User has linked student object, but this should not happen for empty username")
                student = user.students
            else:
                print(f"✅ User does not have linked student object as expected due to empty username")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING STUDENT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Đúng ra phải không tạo được student, student_count không tăng
        if error_caught or post_creation_state['students_count'] == pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student creation failed as expected due to empty username")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student was created despite empty username")
            self.fail("Student creation should fail for empty username")

    def STU_ADD_UN_02_username_two_characters_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-UN-02: user_name has 2 characters - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "jo"  # 2 characters, should fail
        email = "teststudent_un02@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: '{username}'")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )
            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print(f"❌ User has linked student object, but this should not happen for username length 2")
                student = user.students
            else:
                print(f"✅ User does not have linked student object as expected due to username length 2")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING STUDENT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Đúng ra phải không tạo được student, student_count không tăng
        if error_caught or post_creation_state['students_count'] == pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student creation failed as expected due to username length < 3")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student was created despite username length < 3")
            self.fail("Student creation should fail for username length < 3")

    def STU_ADD_UN_03_username_three_characters_SUCCESS(self):
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-UN-03: user_name has 3 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "joh"  # 3 characters, valid
        email = "teststudent_un03@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: '{username}'")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print(f"✅ User has successfully linked student object")
                student = user.students
            else:
                print(f"❌ User does not have linked student object")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING STUDENT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if not error_caught and student and post_creation_state['students_count'] > pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student was successfully created with 3-character username")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student creation failed despite valid 3-character username")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Student creation should succeed for 3-character username")

    def STU_ADD_UN_04_username_four_characters_SUCCESS(self):
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-UN-04: user_name has 4 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "john"  # 4 characters, valid
        email = "teststudent_un04@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: '{username}'")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print(f"✅ User has successfully linked student object")
                student = user.students
            else:
                print(f"❌ User does not have linked student object")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING STUDENT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if not error_caught and student and post_creation_state['students_count'] > pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student was successfully created with 4-character username")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student creation failed despite valid 4-character username")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Student creation should succeed for 4-character username")

    def STU_ADD_UN_05_username_29_characters_SUCCESS(self):
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-UN-05: user_name has 29 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "johnsteveeeeeeeeeeeeeeeeeeeee"  # 29 characters, valid
        email = "teststudent_un05@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: '{username}'")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print(f"✅ User has successfully linked student object")
                student = user.students
            else:
                print(f"❌ User does not have linked student object")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING STUDENT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if not error_caught and student and post_creation_state['students_count'] > pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student was successfully created with 29-character username")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student creation failed despite valid 29-character username")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Student creation should succeed for 29-character username")

    def STU_ADD_UN_06_username_30_characters_SUCCESS(self):
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-UN-06: user_name has 30 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "johnsteveeeeeeeeeeeeeeeeeeeeee"  # 30 characters, valid
        email = "teststudent_un06@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: '{username}'")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print(f"✅ User has successfully linked student object")
                student = user.students
            else:
                print(f"❌ User does not have linked student object")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING STUDENT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if not error_caught and student and post_creation_state['students_count'] > pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student was successfully created with 30-character username")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student creation failed despite valid 30-character username")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Student creation should succeed for 30-character username")

    def STU_ADD_UN_07_username_31_characters_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-UN-07: user_name has 31 characters - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "johnsteveeeeeeeeeeeeeeeeeeeeeee"  # 31 characters, invalid (too long)
        email = "teststudent_un07@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: '{username}'")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print("❌ User has linked student object but should NOT for invalid username length")
                student = user.students
            else:
                print("✅ User does not have linked student object as expected due to invalid username length")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n✅ Expected ERROR caught: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # The student should NOT be created, count should not increase
        if error_caught or post_creation_state['students_count'] == pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student creation failed as expected due to invalid 31-character username")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student was created despite invalid 31-character username")
            self.fail("Student creation should fail for username longer than 30 characters")

    def STU_ADD_UN_08_username_starts_with_digit_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-UN-08: user_name starts with a digit - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "9johnsteve"  # username bắt đầu bằng số, invalid
        email = "teststudent_un08@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: '{username}'")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print("❌ User has linked student object but should NOT for username starting with digit")
                student = user.students
            else:
                print("✅ User does not have linked student object as expected due to invalid username starting digit")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n✅ Expected ERROR caught: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Student should NOT be created
        if error_caught or post_creation_state['students_count'] == pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student creation failed as expected due to username starting with digit")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student was created despite username starting with digit")
            self.fail("Student creation should fail for username starting with digits")

    def STU_ADD_UN_09_username_contains_special_characters_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-UN-09: user_name contains special characters - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "johnsteve#"  # username chứa ký tự đặc biệt, invalid
        email = "teststudent_un09@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: '{username}'")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print("❌ User has linked student object but should NOT for username containing special characters")
                student = user.students
            else:
                print("✅ User does not have linked student object as expected due to invalid username with special chars")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n✅ Expected ERROR caught: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Student should NOT be created
        if error_caught or post_creation_state['students_count'] == pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student creation failed as expected due to username containing special characters")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student was created despite username containing special characters")
            self.fail("Student creation should fail for username containing special characters")

    def STU_ADD_UN_10_username_is_duplicated_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-UN-10: user_name is duplicated - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "john"  # giả sử username này đã tồn tại trong db
        email = "teststudent_un10@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: '{username}'")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print("❌ User has linked student object but username is duplicated, nên không hợp lệ")
                student = user.students
            else:
                print("✅ User không có linked student object như mong đợi với username duplicated")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n✅ Expected ERROR caught: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Student không được tạo vì username đã tồn tại
        if error_caught or post_creation_state['students_count'] == pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student creation failed as expected due to duplicated username")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student được tạo dù username bị trùng")
            self.fail("Student creation should fail for duplicated username")

    def STU_ADD_EM_01_email_empty_string_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-EM-01: email has empty string - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent_em01"
        email = ""  # Empty email to trigger error
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: {username}")
        print(f"  - Email: '{email}'")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print("❌ User has linked student object but email is empty, không hợp lệ")
                student = user.students
            else:
                print("✅ User không có linked student object như mong đợi với email empty")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n✅ Expected ERROR caught: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Student không được tạo vì email empty
        if error_caught or post_creation_state['students_count'] == pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student creation failed as expected due to empty email")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student được tạo dù email trống")
            self.fail("Student creation should fail for empty email")

    def STU_ADD_EM_02_email_7_characters_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-EM-02: email has 7 characters - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent_em02"
        email = "s@x.com"  # 7 characters email to trigger error
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: {username}")
        print(f"  - Email: '{email}'")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print("❌ User has linked student object but email length invalid")
                student = user.students
            else:
                print("✅ User does not have linked student object as expected for invalid email length")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n✅ Expected ERROR caught: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if error_caught or post_creation_state['students_count'] == pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student creation failed as expected due to invalid email length (7 characters)")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student was created despite invalid email length (7 characters)")
            self.fail("Student creation should fail for email length < 8 characters")

    def STU_ADD_EM_03_email_8_characters_SUCCESS(self):
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-EM-03: email has 8 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent_em03"
        email = "st@x.com"  # 8 characters email, valid
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: {username}")
        print(f"  - Email: '{email}'")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print("✅ User has successfully linked student object")
                student = user.students
            else:
                print("❌ User does not have linked student object")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING STUDENT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if not error_caught and student and post_creation_state['students_count'] > pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student was successfully created with valid 8-character email")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student creation failed despite valid 8-character email")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Student creation should succeed for valid 8-character email")

    def STU_ADD_EM_04_email_9_characters_SUCCESS(self):
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-EM-04: email has 9 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent_em04"
        email = "ste@x.com"  # 9 characters email, valid
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: {username}")
        print(f"  - Email: '{email}'")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print("✅ User has successfully linked student object")
                student = user.students
            else:
                print("❌ User does not have linked student object")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING STUDENT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if not error_caught and student and post_creation_state['students_count'] > pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student was successfully created with valid 9-character email")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student creation failed despite valid 9-character email")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Student creation should succeed for valid 9-character email")

    def STU_ADD_EM_05_email_49_characters_SUCCESS(self):
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-EM-05: email has 49 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent_em05"
        email = "steveeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee@gmail.com"  # 49 characters email, valid
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: {username}")
        print(f"  - Email: '{email}'")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print("✅ User has successfully linked student object")
                student = user.students
            else:
                print("❌ User does not have linked student object")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING STUDENT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if not error_caught and student and post_creation_state['students_count'] > pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student was successfully created with valid 49-character email")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student creation failed despite valid 49-character email")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Student creation should succeed for valid 49-character email")

    def STU_ADD_EM_06_email_50_characters_SUCCESS(self):
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-EM-06: email has 50 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent_em06"
        email = "steveeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee@gmail.com"  # 50 characters email, valid
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: {username}")
        print(f"  - Email: '{email}'")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print("✅ User has successfully linked student object")
                student = user.students
            else:
                print("❌ User does not have linked student object")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING STUDENT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if not error_caught and student and post_creation_state['students_count'] > pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student was successfully created with valid 50-character email")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student creation failed despite valid 50-character email")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Student creation should succeed for valid 50-character email")

    def STU_ADD_EM_07_email_51_characters_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-EM-07: email has 51 characters - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent_em07"
        email = "steveeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeea@gmail.com"  # 51 characters email (one extra 'a')
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: {username}")
        print(f"  - Email: '{email}'")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print("❌ User has linked student object but this should NOT happen for invalid email length")
                student = user.students
            else:
                print("✅ User does not have linked student object as expected due to invalid email length")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n✅ Expected ERROR caught: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Email dài quá nên phải fail, student_count không tăng
        if error_caught or post_creation_state['students_count'] == pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student creation failed as expected due to email length > 50 characters")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student was created despite invalid email length")
            self.fail("Student creation should fail for email length > 50 characters")

    def STU_ADD_EM_08_email_missing_domain_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-EM-08: email missing domain - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent_em08"
        email = "steve@.com"  # Email missing domain part
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: {username}")
        print(f"  - Email: '{email}'")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print("❌ User has linked student object but this should NOT happen for invalid email format")
                student = user.students
            else:
                print("✅ User does not have linked student object as expected due to invalid email format")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n✅ Expected ERROR caught: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Email format sai nên phải fail, student_count không tăng
        if error_caught or post_creation_state['students_count'] == pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student creation failed as expected due to missing domain in email")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student was created despite invalid email format")
            self.fail("Student creation should fail for email missing domain")

    def STU_ADD_EM_09_email_missing_at_symbol_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-EM-09: email missing @ symbol - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent_em09"
        email = "stevegmail.com"  # Email missing '@' symbol
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: {username}")
        print(f"  - Email: '{email}'")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print("❌ User has linked student object but this should NOT happen for invalid email format")
                student = user.students
            else:
                print("✅ User does not have linked student object as expected due to invalid email format")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n✅ Expected ERROR caught: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Email format sai nên phải fail, student_count không tăng
        if error_caught or post_creation_state['students_count'] == pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student creation failed as expected due to missing '@' symbol in email")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student was created despite invalid email format")
            self.fail("Student creation should fail for email missing '@' symbol")

    def STU_ADD_EM_10_email_contains_special_characters_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-EM-10: email contains special characters, except '@' - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent_em10"
        email = "steve@gmail.com#"  # Email chứa ký tự đặc biệt #
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with:")
        print(f"  - Username: {username}")
        print(f"  - Email: '{email}'")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3  # Student
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print("❌ User has linked student object but this should NOT happen for invalid email format")
                student = user.students
            else:
                print("✅ User does not have linked student object as expected due to invalid email format")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n✅ Expected ERROR caught: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Email chứa ký tự đặc biệt ngoài '@' nên phải fail, student_count không tăng
        if error_caught or post_creation_state['students_count'] == pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student creation failed as expected due to special characters in email")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student was created despite invalid email format")
            self.fail("Student creation should fail for email containing special characters except '@'")

    def STU_ADD_EM_11_email_is_duplicated_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-EM-11: email is duplicated - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent_em11"
        email = "john@test.com"  # Email duplicated - phải tồn tại sẵn trong db
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        # Giả sử email 'john@test.com' đã tồn tại, tạo trước 1 user với email này
        try:
            existing_user = CustomUser.objects.create_user(
                username="existing_user_john",
                email=email,
                password="SomePassword@123",
                first_name="Existing",
                last_name="User",
                user_type=3
            )
        except Exception:
            # Nếu user đã tồn tại thì bỏ qua
            pass

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with duplicated email:")
        print(f"  - Username: {username}")
        print(f"  - Email: '{email}'")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print("❌ User has linked student object but this should NOT happen for duplicated email")
                student = user.students
            else:
                print("✅ User does not have linked student object as expected due to duplicated email")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n✅ Expected ERROR caught: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if error_caught or post_creation_state['students_count'] == pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student creation failed as expected due to duplicated email")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student was created despite duplicated email")
            self.fail("Student creation should fail for duplicated email")

    def STU_ADD_PW_01_password_empty_string_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-PW-01: password has empty string - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent_pw01"
        email = "teststudent_pw01@test.com"
        password = ""  # Empty password to trigger error
        first_name = "John"
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with empty password:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Password: '{password}' (empty)")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print("❌ User has linked student object but this should NOT happen for empty password")
                student = user.students
            else:
                print("✅ User does not have linked student object as expected due to empty password")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n✅ Expected ERROR caught: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if error_caught or post_creation_state['students_count'] == pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student creation failed as expected due to empty password")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student was created despite empty password")
            self.fail("Student creation should fail for empty password")

    def STU_ADD_PW_02_password_seven_characters_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-PW-02: password has 7 characters - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent_pw02"
        email = "teststudent_pw02@test.com"
        password = "John@12"  # 7 characters, invalid
        first_name = "John"
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with 7-character password:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Password: '{password}' (7 characters)")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print("❌ User has linked student object but this should NOT happen for 7-char password")
                student = user.students
            else:
                print("✅ User does not have linked student object as expected due to short password")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n✅ Expected ERROR caught: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if error_caught or post_creation_state['students_count'] == pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student creation failed as expected due to password length 7")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student was created despite password length 7")
            self.fail("Student creation should fail for password length < 8")

    def STU_ADD_PW_03_password_eight_characters_SUCCESS(self):
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-PW-03: password has 8 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent_pw03"
        email = "teststudent_pw03@test.com"
        password = "John@123"  # 8 characters, valid
        first_name = "John"
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with 8-character password:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Password: '{password}' (8 characters)")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print("✅ User has successfully linked student object")
                student = user.students
            else:
                print("❌ User does NOT have linked student object")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING STUDENT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if not error_caught and student and post_creation_state['students_count'] > pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student was successfully created with 8-character password")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student creation failed despite valid 8-character password")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Student creation should succeed for 8-character password")

    def STU_ADD_PW_04_password_nine_characters_SUCCESS(self):
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-PW-04: password has 9 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent_pw04"
        email = "teststudent_pw04@test.com"
        password = "John@1234"  # 9 characters, valid
        first_name = "John"
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with 9-character password:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Password: '{password}' (9 characters)")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print("✅ User has successfully linked student object")
                student = user.students
            else:
                print("❌ User does NOT have linked student object")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING STUDENT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if not error_caught and student and post_creation_state['students_count'] > pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student was successfully created with 9-character password")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student creation failed despite valid 9-character password")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Student creation should succeed for 9-character password")

    def STU_ADD_PW_05_password_sixty_three_characters_SUCCESS(self):
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-PW-05: password has 63 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent_pw05"
        email = "teststudent_pw05@test.com"
        password = "Johnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn@1234"  # 63 characters
        first_name = "John"
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with 63-character password:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Password: '{password}' (63 characters)")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print("✅ User has successfully linked student object")
                student = user.students
            else:
                print("❌ User does NOT have linked student object")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING STUDENT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if not error_caught and student and post_creation_state['students_count'] > pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student was successfully created with 63-character password")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student creation failed despite valid 63-character password")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Student creation should succeed for 63-character password")

    def STU_ADD_PW_06_password_sixty_four_characters_SUCCESS(self):
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-PW-06: password has 64 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent_pw06"
        email = "teststudent_pw06@test.com"
        password = "Johnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn@1234"  # 64 characters
        first_name = "John"
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with 64-character password:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Password: '{password}' (64 characters)")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print("✅ User has successfully linked student object")
                student = user.students
            else:
                print("❌ User does NOT have linked student object")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING STUDENT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if not error_caught and student and post_creation_state['students_count'] > pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student was successfully created with 64-character password")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student creation failed despite valid 64-character password")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Student creation should succeed for 64-character password")

    def STU_ADD_PW_07_password_sixty_five_characters_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-PW-07: password has 65 characters - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent_pw07"
        email = "teststudent_pw07@test.com"
        password = "Johnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn@1234"  # 65 characters
        first_name = "John"
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with 65-character password:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Password: '{password}' (65 characters)")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print("❌ User has linked student object, but should NOT be created with invalid password length")
                student = user.students
            else:
                print("✅ User does NOT have linked student object as expected due to invalid password length")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING STUDENT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Student creation should fail, students_count không tăng
        if error_caught or post_creation_state['students_count'] == pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student creation failed as expected due to password length > 64")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student was created despite invalid 65-character password length")
            self.fail("Student creation should fail for password length > 64")

    def STU_ADD_PW_08_password_missing_uppercase_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-PW-08: password missing uppercase letter - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent_pw08"
        email = "teststudent_pw08@test.com"
        password = "john@1234"  # no uppercase letter
        first_name = "John"
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with password missing uppercase letter:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Password: '{password}' (missing uppercase)")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print("❌ User has linked student object, but should NOT be created without uppercase letter in password")
                student = user.students
            else:
                print("✅ User does NOT have linked student object as expected due to missing uppercase letter")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING STUDENT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Student creation should fail, students_count không tăng
        if error_caught or post_creation_state['students_count'] == pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student creation failed as expected due to missing uppercase letter in password")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student was created despite password missing uppercase letter")
            self.fail("Student creation should fail for password missing uppercase letter")

    def STU_ADD_PW_09_password_missing_lowercase_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-PW-09: password missing lowercase letter - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent_pw09"
        email = "teststudent_pw09@test.com"
        password = "JOHN@1234"  # no lowercase letter
        first_name = "John"
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with password missing lowercase letter:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Password: '{password}' (missing lowercase)")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print("❌ User has linked student object, but should NOT be created without lowercase letter in password")
                student = user.students
            else:
                print("✅ User does NOT have linked student object as expected due to missing lowercase letter")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING STUDENT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Student creation should fail, students_count không tăng
        if error_caught or post_creation_state['students_count'] == pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student creation failed as expected due to missing lowercase letter in password")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student was created despite password missing lowercase letter")
            self.fail("Student creation should fail for password missing lowercase letter")

    def STU_ADD_PW_10_password_missing_digit_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-PW-10: password missing digit - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent_pw10"
        email = "teststudent_pw10@test.com"
        password = "John@nnn"  # missing digit
        first_name = "John"
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with password missing digit:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Password: '{password}' (missing digit)")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print("❌ User has linked student object, but should NOT be created without digit in password")
                student = user.students
            else:
                print("✅ User does NOT have linked student object as expected due to missing digit")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING STUDENT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Student creation should fail, students_count không tăng
        if error_caught or post_creation_state['students_count'] == pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student creation failed as expected due to missing digit in password")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student was created despite password missing digit")
            self.fail("Student creation should fail for password missing digit")

    def STU_ADD_PW_11_password_missing_special_char_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 STU-ADD-PW-11: password missing special characters - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststudent_pw11"
        email = "teststudent_pw11@test.com"
        password = "John1234"  # missing special character
        first_name = "John"
        last_name = "Doe"
        gender = "Other"
        address = "123 Test Street"
        status = "active"
        course_id = self.course.id
        session_year_id = self.session_year.id

        pre_creation_state = self.get_db_state('Before Creating Student')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating student with password missing special characters:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Password: '{password}' (missing special character)")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Gender: {gender}")
        print(f"  - Address: {address}")
        print(f"  - Status: {status}")
        print(f"  - Course ID: {course_id}")
        print(f"  - Session Year ID: {session_year_id}\n")

        student = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=3
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'students'):
                print("❌ User has linked student object, but should NOT be created without special character in password")
                student = user.students
            else:
                print("✅ User does NOT have linked student object as expected due to missing special character")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING STUDENT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Student')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Student creation should fail, students_count không tăng
        if error_caught or post_creation_state['students_count'] == pre_creation_state['students_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Student creation failed as expected due to missing special character in password")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Student was created despite password missing special character")
            self.fail("Student creation should fail for password missing special character")
