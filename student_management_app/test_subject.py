import unittest
from django.test import TestCase
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
import os
from student_management_app.models import CustomUser, Courses, Subjects, SessionYearModel, Students, Staffs
from django.contrib.auth.models import User
from django.db import connection

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

    def S_ADD_NA_01_subject_name_empty_string_ERROR(self):
        """S-ADD-NA-01: subject_name has empty string - ERROR."""
        print("\n🔍 S-ADD-NA-01: subject_name has empty string - ERROR.")
        
        subject_name = ''
        course = Courses.objects.get_or_create(course_name='Default Course')

        with transaction.atomic():
            try:
                Subjects.objects.create(
                    subject_name=subject_name,
                    course_id=course,
                    staff_id=self.staff_user
                )
            except Exception as e:
                print(f"❌ Caught error as expected: {e}")
                transaction.set_rollback(True)
            else:
                self.fail("Should raise error for empty subject_name")

        self.assertEqual(Subjects.objects.filter(subject_name=subject_name).count(), 0)

    def S_ADD_NA_02_subject_name_one_char_ERROR(self):
        """S-ADD-NA-02: subject_name has 1 character - ERROR."""
        print("\n🔍 S-ADD-NA-02: subject_name has 1 character - ERROR.")
        
        subject_name = 'A'
        course = Courses.objects.get_or_create(course_name='Default Course')

        with transaction.atomic():
            try:
                Subjects.objects.create(
                    subject_name=subject_name,
                    course_id=course,
                    staff_id=self.staff_user
                )
            except Exception as e:
                print(f"❌ Caught error as expected: {e}")
                transaction.set_rollback(True)
            else:
                self.fail("Should raise error for subject_name with 1 character")

        self.assertEqual(Subjects.objects.filter(subject_name=subject_name).count(), 0)

    def S_ADD_NA_03_subject_name_two_chars_SUCCESS(self):
        """S-ADD-NA-03: subject_name has 2 characters - SUCCESS."""
        print("\n🔍 S-ADD-NA-03: subject_name has 2 characters - SUCCESS.")
        
        subject_name = 'BA'
        course = Courses.objects.get_or_create(course_name='Default Course')

        with transaction.atomic():
            subject = Subjects.objects.create(
                subject_name=subject_name,
                course_id=course,
                staff_id=self.staff_user
            )

        self.assertIsNotNone(subject)
        self.assertEqual(subject.subject_name, subject_name)

    def S_ADD_NA_04_subject_name_three_chars_SUCCESS(self):
        """S-ADD-NA-04: subject_name has 3 characters - SUCCESS."""
        print("\n🔍 S-ADD-NA-04: subject_name has 3 characters - SUCCESS.")
        
        subject_name = 'IT1'
        course = Courses.objects.get_or_create(course_name='Default Course')

        with transaction.atomic():
            subject = Subjects.objects.create(
                subject_name=subject_name,
                course_id=course,
                staff_id=self.staff_user
            )

        self.assertIsNotNone(subject)
        self.assertEqual(subject.subject_name, subject_name)

    def S_ADD_NA_05_subject_name_49_chars_SUCCESS(self):
        """S-ADD-NA-05: subject_name has 49 characters - SUCCESS."""
        print("\n🔍 S-ADD-NA-05: subject_name has 49 characters - SUCCESS.")
        
        subject_name = 'B'*49
        course = Courses.objects.get_or_create(course_name='Default Course')

        with transaction.atomic():
            subject = Subjects.objects.create(
                subject_name=subject_name,
                course_id=course,
                staff_id=self.staff_user
            )

        self.assertIsNotNone(subject)
        self.assertEqual(subject.subject_name, subject_name)

    def S_ADD_NA_06_subject_name_50_chars_SUCCESS(self):
        """S-ADD-NA-06: subject_name has 50 characters - SUCCESS."""
        print("\n🔍 S-ADD-NA-06: subject_name has 50 characters - SUCCESS.")
        
        subject_name = 'B'*50  # 50 ký tự
        course = Courses.objects.get_or_create(course_name='Default Course')

        with transaction.atomic():
            subject = Subjects.objects.create(
                subject_name=subject_name,
                course_id=course,
                staff_id=self.staff_user
            )

        self.assertIsNotNone(subject)
        self.assertEqual(subject.subject_name, subject_name)

    def S_ADD_NA_07_subject_name_51_chars_ERROR(self):
        """S-ADD-NA-07: subject_name has 51 characters - ERROR."""
        print("\n🔍 S-ADD-NA-07: subject_name has 51 characters - ERROR.")
        
        subject_name = 'B'*51  # 51 ký tự
        course = Courses.objects.get_or_create(course_name='Default Course')

        with transaction.atomic():
            try:
                Subjects.objects.create(
                    subject_name=subject_name,
                    course_id=course,
                    staff_id=self.staff_user
                )
            except Exception as e:
                print(f"❌ Caught error as expected: {e}")
                transaction.set_rollback(True)
            else:
                self.fail("Should raise error for subject_name with 51 characters")

        self.assertEqual(Subjects.objects.filter(subject_name=subject_name).count(), 0)

    def S_ADD_NA_08_subject_name_special_char_ERROR(self):
        """S-ADD-NA-08: subject_name contains special character - ERROR."""
        print("\n🔍 S-ADD-NA-08: subject_name contains special character - ERROR.")
        
        subject_name = 'AI@'  # Ký tự đặc biệt '@'
        course = Courses.objects.get_or_create(course_name='Default Course')

        with transaction.atomic():
            try:
                Subjects.objects.create(
                    subject_name=subject_name,
                    course_id=course,
                    staff_id=self.staff_user
                )
            except Exception as e:
                print(f"❌ Caught error as expected: {e}")
                transaction.set_rollback(True)
            else:
                self.fail("Should raise error for subject_name containing special characters")

        self.assertEqual(Subjects.objects.filter(subject_name=subject_name).count(), 0)

    def S_ADD_NA_09_subject_name_duplicated_ERROR(self):
        """S-ADD-NA-09: subject_name is duplicated - ERROR."""
        print("\n🔍 S-ADD-NA-09: subject_name is duplicated - ERROR.")
        
        subject_name = 'BA'
        course = Courses.objects.get_or_create(course_name='Default Course')

        # Tạo trước subject trùng tên
        Subjects.objects.create(
            subject_name=subject_name,
            course_id=course,
            staff_id=self.staff_user
        )

        with transaction.atomic():
            try:
                Subjects.objects.create(
                    subject_name=subject_name,
                    course_id=course,
                    staff_id=self.staff_user
                )
            except Exception as e:
                print(f"❌ Caught error as expected: {e}")
                transaction.set_rollback(True)
            else:
                self.fail("Should raise error for duplicated subject_name")

        self.assertEqual(Subjects.objects.filter(subject_name=subject_name).count(), 1)

    def S_ADD_STA_01_course_id_empty_string_ERROR(self):
        """S-ADD-STA-01: course_id has empty string - ERROR."""
        print("\n" + "*"*100)
        print("\n🔍 S-ADD-STA-01: course_id has empty string - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        course_id = ''  # Giá trị course_id là chuỗi rỗng
        subject_name = "Some Subject"

        pre_creation_state = self.get_db_state('Before Creating Subject')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating subject with:")
        print(f"  - Course ID: '{course_id}' (empty string)")
        print(f"  - Name: {subject_name}")

        error_caught = False
        error_message = None

        # Sử dụng transaction.atomic để tự động rollback khi có lỗi
        with transaction.atomic():
            try:
                # Lấy course với course_id rỗng sẽ lỗi
                course = Courses.objects.get(id=course_id)

                Subjects.objects.create(
                    subject_name=subject_name,
                    course_id=course,
                    staff_id=self.staff_user
                )
            except Exception as e:
                error_caught = True
                error_message = str(e)
                print(f"\n❌ ERROR CREATING SUBJECT: {error_message}")
                # Không cần gọi connection.rollback(), transaction.atomic() tự rollback

        post_creation_state = self.get_db_state('After Creating Subject')
        self.print_db_state(post_creation_state, "AFTER CREATION")

        # Assert subject creation phải thất bại, subjects_count không tăng
        self.assertTrue(error_caught or
                        post_creation_state['subjects_count'] == pre_creation_state['subjects_count'],
                        msg="Subject creation should fail for empty course_id")

        print("\n🟢 TEST RESULT: PASSED")
        print("  - Subject creation failed as expected due to empty course_id")
        if error_message:
            print(f"  - Error message: {error_message}")

    def S_ADD_STA_02_course_id_exists_SUCCESS(self):
        """S-ADD-STA-02: course_id exists in the system - SUCCESS."""
        print("\n" + "*"*100)
        print("\n🔍 S-ADD-STA-02: course_id exists in the system - SUCCESS.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        course_id = 'C123'
        subject_name = "Valid Subject"

        # Đảm bảo course với course_id tồn tại hoặc tạo mới nếu chưa có
        course, _ = Courses.objects.get_or_create(
            id=course_id,
            defaults={'course_name': 'Sample Course'}
        )

        pre_creation_state = self.get_db_state('Before Creating Subject')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating subject with:")
        print(f"  - Course ID: {course_id}")
        print(f"  - Name: {subject_name}")

        error_caught = False
        error_message = None

        with transaction.atomic():
            try:
                Subjects.objects.create(
                    subject_name=subject_name,
                    course_id=course,
                    staff_id=self.staff_user
                )
            except Exception as e:
                error_caught = True
                error_message = str(e)
                print(f"\n❌ ERROR CREATING SUBJECT: {error_message}")

        post_creation_state = self.get_db_state('After Creating Subject')
        self.print_db_state(post_creation_state, "AFTER CREATION")

        # Subject creation phải thành công, số lượng tăng lên 1
        self.assertFalse(error_caught, f"Error caught during subject creation: {error_message}")
        self.assertEqual(
            post_creation_state['subjects_count'],
            pre_creation_state['subjects_count'] + 1,
            "Subject count should increase by 1 after successful creation"
        )

        print("\n🟢 TEST RESULT: PASSED")
        print("  - Subject created successfully with existing course_id")

    def S_ADD_STA_03_course_id_not_exists_ERROR(self):
        """S-ADD-STA-03: course_id does not exist in the system - ERROR."""
        print("\n" + "*"*100)
        print("\n🔍 S-ADD-STA-03: course_id does not exist in the system - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        course_id = 'inactive'  # course_id không tồn tại
        subject_name = "Test Subject"

        pre_creation_state = self.get_db_state('Before Creating Subject')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating subject with:")
        print(f"  - Course ID: {course_id}")
        print(f"  - Name: {subject_name}")

        error_caught = False
        error_message = None

        with transaction.atomic():
            try:
                # Lấy course với course_id không tồn tại sẽ raise DoesNotExist exception
                course = Courses.objects.get(id=course_id)

                Subjects.objects.create(
                    subject_name=subject_name,
                    course_id=course,
                    staff_id=self.staff_user
                )
            except Exception as e:
                error_caught = True
                error_message = str(e)
                print(f"\n❌ ERROR CREATING SUBJECT: {error_message}")

        post_creation_state = self.get_db_state('After Creating Subject')
        self.print_db_state(post_creation_state, "AFTER CREATION")

        # Subject creation phải fail, subjects_count không tăng
        self.assertTrue(
            error_caught or post_creation_state['subjects_count'] == pre_creation_state['subjects_count'],
            "Subject creation should fail for non-existent course_id"
        )

        print("\n🟢 TEST RESULT: PASSED")
        print("  - Subject creation failed as expected due to non-existent course_id")
        if error_message:
            print(f"  - Error message: {error_message}")
