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

    def S_ADD_ID_01_subject_id_has_empty_string_ERROR(self):
        """S-ADD-ID-01: subject_id has empty string - ERROR."""
        print("\n" + "*"*100)
        print("\n🔍 S-ADD-ID-01: subject_id has empty string - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        subject_id = ''
        subject_name = "Mathematics"
        description = 'Advanced Topics in Mathematics'

        # Ensure a valid course exists
        course, _ = Courses.objects.get_or_create(
            id=1,
            defaults={'course_name': 'Default Course'}
        )
        course_id = course.id

        pre_creation_state = self.get_db_state('Before Creating Course')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating subject with:")
        print(f"  - ID: {subject_id}")
        print(f"  - Name: {subject_name}")
        print(f"  - Description: {description}")
        print(f"  - Course ID: {course_id}")

        subject = None
        error_caught = False
        error_message = None

        try:
            subject = Subjects.objects.create(
                subject_name=subject_name,
                course_id=course,
                staff_id=self.staff_user
            )

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SUBJECT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Subject')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Subject creation should fail, subjects_count không tăng
        if error_caught or post_creation_state['subjects_count'] == pre_creation_state['subjects_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Subject creation failed as expected due to subject_id has empty string")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Subject was created despite subject_id has empty string")
            self.fail("Subject creation should fail for subject_id has empty string")

    def S_ADD_ID_02_subject_id_has_no_digit_ERROR(self):
        """S-ADD-ID-02: subject_id has no digit – ERROR."""
        print("\n" + "*"*100)
        print("\n🔍 S-ADD-ID-02: subject_id has no digit – ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        subject_id = 'SB'  # Không hợp lệ: thiếu 3 chữ số
        subject_name = "Physics"
        description = 'Fundamentals of Physics'

        # Đảm bảo course_id hợp lệ tồn tại
        course, _ = Courses.objects.get_or_create(
            id=1,
            defaults={'course_name': 'Default Course'}
        )
        course_id = course.id

        pre_creation_state = self.get_db_state('Before Creating Course')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating subject with:")
        print(f"  - ID: {subject_id}")
        print(f"  - Name: {subject_name}")
        print(f"  - Description: {description}")
        print(f"  - Course ID: {course_id}")

        subject = None
        error_caught = False
        error_message = None

        try:
            subject = Subjects.objects.create(
                subject_name=subject_name,
                course_id=course,
                staff_id=self.staff_user
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SUBJECT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Subject')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Subject creation should fail, subjects_count không tăng
        if error_caught or post_creation_state['subjects_count'] == pre_creation_state['subjects_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Subject creation failed as expected due to subject_id has no digit")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Subject was created despite invalid subject_id format")
            self.fail("Subject creation should fail for subject_id that has no digit")

    def S_ADD_ID_03_subject_id_has_two_digits_ERROR(self):
        """S-ADD-ID-03: subject_id has 2 digits – ERROR."""
        print("\n" + "*"*100)
        print("\n🔍 S-ADD-ID-03: subject_id has 2 digits – ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        subject_id = 'SB12'  # ❌ Không hợp lệ: chỉ có 2 chữ số thay vì 3
        subject_name = "Chemistry"
        description = 'Basics of Chemistry'

        # Đảm bảo course_id hợp lệ tồn tại
        course, _ = Courses.objects.get_or_create(
            id=1,
            defaults={'course_name': 'Default Course'}
        )
        course_id = course.id

        pre_creation_state = self.get_db_state('Before Creating Course')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating subject with:")
        print(f"  - ID: {subject_id}")
        print(f"  - Name: {subject_name}")
        print(f"  - Description: {description}")
        print(f"  - Course ID: {course_id}")

        subject = None
        error_caught = False
        error_message = None

        try:
            subject = Subjects.objects.create(
                subject_name=subject_name,
                course_id=course,
                staff_id=self.staff_user
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SUBJECT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Subject')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Subject creation should fail, subjects_count không tăng
        if error_caught or post_creation_state['subjects_count'] == pre_creation_state['subjects_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Subject creation failed as expected due to subject_id has 2 digits")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Subject was created despite subject_id having 2 digits")
            self.fail("Subject creation should fail for subject_id that has 2 digits")

    def S_ADD_ID_04_subject_id_has_three_digits_SUCCESS(self):
        """S-ADD-ID-04: subject_id has 3 digits – SUCCESS."""
        print("\n" + "*"*100)
        print("\n🔍 S-ADD-ID-04: subject_id has 3 digits – SUCCESS.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        subject_id = 'SB123'  # hợp lệ
        subject_name = "Biology"
        description = 'Introduction to Biology'

        # Đảm bảo course tồn tại
        course, _ = Courses.objects.get_or_create(
            id=1,
            defaults={'course_name': 'Default Course'}
        )
        course_id = course.id

        pre_creation_state = self.get_db_state('Before Creating Subject')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating subject with:")
        print(f"  - ID: {subject_id}")
        print(f"  - Name: {subject_name}")
        print(f"  - Description: {description}")
        print(f"  - Course ID: {course_id}")

        subject = None
        error_caught = False
        error_message = None

        try:
            subject = Subjects.objects.create(
                subject_name=subject_name,
                course_id=course,
                staff_id=self.staff_user
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SUBJECT: {error_message}")
            connection.rollback()

        post_creation_state = self.get_db_state('After Creating Subject')
        self.print_db_state(post_creation_state, "AFTER CREATION")

        # Subject creation phải thành công, subjects_count tăng 1
        if not error_caught and post_creation_state['subjects_count'] == pre_creation_state['subjects_count'] + 1:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Subject was successfully created with a valid subject_id")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            if error_message:
                print(f"  - Error message: {error_message}")
            self.fail("Subject creation should succeed for valid subject_id format (SB + 3 digits)")

    def S_ADD_ID_05_subject_id_has_four_digits_ERROR(self):
        """S-ADD-ID-05: subject_id has 4 digits - ERROR."""
        print("\n" + "*"*100)
        print("\n🔍 S-ADD-ID-05: subject_id has 4 digits - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        subject_id = 'SB1234'  # sai định dạng: 4 chữ số sau SB
        subject_name = "Chemistry"
        description = 'Organic Chemistry'

        # Đảm bảo course tồn tại
        course, _ = Courses.objects.get_or_create(
            id=1,
            defaults={'course_name': 'Default Course'}
        )
        course_id = course.id

        pre_creation_state = self.get_db_state('Before Creating Subject')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating subject with:")
        print(f"  - ID: {subject_id}")
        print(f"  - Name: {subject_name}")
        print(f"  - Description: {description}")
        print(f"  - Course ID: {course_id}")

        subject = None
        error_caught = False
        error_message = None

        try:
            # Không truyền subject_id, description
            subject = Subjects.objects.create(
                subject_name=subject_name,
                course_id=course,
                staff_id=self.staff_user
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SUBJECT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Subject')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Subject creation phải fail, subjects_count không tăng
        if error_caught or post_creation_state['subjects_count'] == pre_creation_state['subjects_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Subject creation failed as expected due to subject_id has 4 digits")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Subject was created despite subject_id has 4 digits")
            self.fail("Subject creation should fail for subject_id with 4 digits")

    def S_ADD_ID_06_subject_id_has_nondigit_characters_ERROR(self):
        """S-ADD-ID-06: subject_id has non-digit characters - ERROR."""
        print("\n" + "*"*100)
        print("\n🔍 S-ADD-ID-06: subject_id has non-digit characters - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        subject_id = 'SB1A-'  # sai định dạng: ký tự không phải số trong phần 3 chữ số
        subject_name = "History"
        description = 'World History'

        # Đảm bảo course tồn tại
        course, _ = Courses.objects.get_or_create(
            id=1,
            defaults={'course_name': 'Default Course'}
        )
        course_id = course.id

        pre_creation_state = self.get_db_state('Before Creating Subject')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating subject with:")
        print(f"  - ID: {subject_id}")
        print(f"  - Name: {subject_name}")
        print(f"  - Description: {description}")
        print(f"  - Course ID: {course_id}")

        subject = None
        error_caught = False
        error_message = None

        try:
            # Không truyền subject_id và description
            subject = Subjects.objects.create(
                subject_name=subject_name,
                course_id=course,
                staff_id=self.staff_user
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SUBJECT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Subject')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Subject creation phải fail, subjects_count không tăng
        if error_caught or post_creation_state['subjects_count'] == pre_creation_state['subjects_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Subject creation failed as expected due to subject_id has non-digit characters")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Subject was created despite subject_id has non-digit characters")
            self.fail("Subject creation should fail for subject_id containing non-digit characters after 'SB'")

    def S_ADD_ID_07_subject_id_has_lowercase_letter_ERROR(self):
        """S-ADD-ID-07: subject_id has lowercase letter - ERROR."""
        print("\n" + "*"*100)
        print("\n🔍 S-ADD-ID-07: subject_id has lowercase letter - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        subject_id = 'sb123'  # sai định dạng: chữ thường ở phần SB
        subject_name = "Geography"
        description = 'Physical Geography'

        # Đảm bảo course tồn tại
        course, _ = Courses.objects.get_or_create(
            id=1,
            defaults={'course_name': 'Default Course'}
        )
        course_id = course.id

        pre_creation_state = self.get_db_state('Before Creating Subject')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating subject with:")
        print(f"  - ID: {subject_id}")
        print(f"  - Name: {subject_name}")
        print(f"  - Description: {description}")
        print(f"  - Course ID: {course_id}")

        subject = None
        error_caught = False
        error_message = None

        try:
            # Không truyền subject_id, description
            subject = Subjects.objects.create(
                subject_name=subject_name,
                course_id=course,
                staff_id=self.staff_user
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SUBJECT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Subject')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Subject creation phải fail, subjects_count không tăng
        if error_caught or post_creation_state['subjects_count'] == pre_creation_state['subjects_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Subject creation failed as expected due to subject_id has lowercase letter")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Subject was created despite subject_id has lowercase letter")
            self.fail("Subject creation should fail for subject_id with lowercase letter in 'SB'")

    def S_ADD_ID_08_subject_id_has_all_zeros_digits_ERROR(self):
        """S-ADD-ID-08: subject_id has 3 digits are zero - ERROR."""
        print("\n" + "*"*100)
        print("\n🔍 S-ADD-ID-08: subject_id has 3 digits are zero - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        subject_id = 'SB000'  # sai định dạng: 3 chữ số đều là 0
        subject_name = "Chemistry"
        description = 'Basic Chemistry'

        # Đảm bảo course tồn tại
        course, _ = Courses.objects.get_or_create(
            id=1,
            defaults={'course_name': 'Default Course'}
        )
        course_id = course.id

        pre_creation_state = self.get_db_state('Before Creating Subject')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating subject with:")
        print(f"  - ID: {subject_id}")
        print(f"  - Name: {subject_name}")
        print(f"  - Description: {description}")
        print(f"  - Course ID: {course_id}")

        subject = None
        error_caught = False
        error_message = None

        try:
            # Không truyền subject_id, description
            subject = Subjects.objects.create(
                subject_name=subject_name,
                course_id=course,
                staff_id=self.staff_user
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SUBJECT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Subject')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Subject creation phải fail, subjects_count không tăng
        if error_caught or post_creation_state['subjects_count'] == pre_creation_state['subjects_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Subject creation failed as expected due to subject_id has digits all zero")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Subject was created despite subject_id has digits all zero")
            self.fail("Subject creation should fail for subject_id with digits all zero")

    def S_ADD_ID_09_subject_id_has_digits_999_SUCCESS(self):
        """S-ADD-ID-09: subject_id has digits 999 - SUCCESS."""
        print("\n" + "*"*100)
        print("\n🔍 S-ADD-ID-09: subject_id has digits 999 - SUCCESS.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        subject_id = 'SB999'  # hợp lệ
        subject_name = "Advanced Physics"
        description = 'Physics at advanced level'

        # Đảm bảo course tồn tại
        course, _ = Courses.objects.get_or_create(
            id=1,
            defaults={'course_name': 'Default Course'}
        )
        course_id = course.id

        pre_creation_state = self.get_db_state('Before Creating Subject')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating subject with:")
        print(f"  - ID: {subject_id}")
        print(f"  - Name: {subject_name}")
        print(f"  - Description: {description}")
        print(f"  - Course ID: {course_id}")

        subject = None
        error_caught = False
        error_message = None

        try:
            # Không truyền subject_id, description
            subject = Subjects.objects.create(
                subject_name=subject_name,
                course_id=course,
                staff_id=self.staff_user
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SUBJECT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Subject')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Subject creation phải thành công, subjects_count tăng
        if not error_caught and post_creation_state['subjects_count'] > pre_creation_state['subjects_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Subject creation succeeded as expected for valid subject_id SB999")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Subject creation failed despite valid subject_id SB999")
            self.fail("Subject creation should succeed for valid subject_id SB999")

    def S_ADD_ID_10_subject_id_contains_whitespace_ERROR(self):
        """S-ADD-ID-10: subject_id contains whitespace - ERROR."""
        print("\n" + "*"*100)
        print("\n🔍 S-ADD-ID-10: subject_id contains whitespace - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        subject_id = 'SB 12'  # sai định dạng có khoảng trắng
        subject_name = "Biology"
        description = 'Basic Biology'

        # Đảm bảo course tồn tại
        course, _ = Courses.objects.get_or_create(
            id=1,
            defaults={'course_name': 'Default Course'}
        )
        course_id = course.id

        pre_creation_state = self.get_db_state('Before Creating Subject')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating subject with:")
        print(f"  - ID: {subject_id}")
        print(f"  - Name: {subject_name}")
        print(f"  - Description: {description}")
        print(f"  - Course ID: {course_id}")

        subject = None
        error_caught = False
        error_message = None

        try:
            # Không truyền subject_id, description
            subject = Subjects.objects.create(
                subject_name=subject_name,
                course_id=course,
                staff_id=self.staff_user
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SUBJECT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Subject')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Subject creation phải fail, subjects_count không tăng
        if error_caught or post_creation_state['subjects_count'] == pre_creation_state['subjects_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Subject creation failed as expected due to subject_id contains whitespace")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Subject was created despite subject_id contains whitespace")
            self.fail("Subject creation should fail for subject_id contains whitespace")

    def S_ADD_ID_11_subject_id_not_start_SB_ERROR(self):
        """S-ADD-ID-11: subject_id does not start with SB - ERROR."""
        print("\n" + "*"*100)
        print("\n🔍 S-ADD-ID-11: subject_id does not start with SB - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        subject_id = '1234'  # sai định dạng không bắt đầu SB
        subject_name = "Chemistry"
        description = 'General Chemistry'

        # Đảm bảo course tồn tại
        course, _ = Courses.objects.get_or_create(
            id=1,
            defaults={'course_name': 'Default Course'}
        )
        course_id = course.id

        pre_creation_state = self.get_db_state('Before Creating Subject')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating subject with:")
        print(f"  - ID: {subject_id}")
        print(f"  - Name: {subject_name}")
        print(f"  - Description: {description}")
        print(f"  - Course ID: {course_id}")

        subject = None
        error_caught = False
        error_message = None

        try:
            # Không truyền subject_id, description
            subject = Subjects.objects.create(
                subject_name=subject_name,
                course_id=course,
                staff_id=self.staff_user
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SUBJECT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Subject')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Subject creation phải fail, subjects_count không tăng
        if error_caught or post_creation_state['subjects_count'] == pre_creation_state['subjects_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Subject creation failed as expected due to subject_id does not start with SB")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Subject was created despite subject_id does not start with SB")
            self.fail("Subject creation should fail for subject_id does not start with SB")

    def S_ADD_ID_12_subject_id_is_duplicated_ERROR(self):
        """S-ADD-ID-12: subject_id is duplicated - ERROR."""
        print("\n" + "*"*100)
        print("\n🔍 S-ADD-ID-12: subject_id is duplicated - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        subject_id = 'SB123'  # subject_id trùng lặp
        subject_name = "History"
        description = 'World History'

        # Đảm bảo course tồn tại
        course, _ = Courses.objects.get_or_create(
            id=1,
            defaults={'course_name': 'Default Course'}
        )
        course_id = course.id

        # Tạo subject đầu tiên với subject_id SB123 (giả định hệ thống có cách set subject_id tự động hoặc khác)
        try:
            Subjects.objects.create(
                subject_name=subject_name,
                course_id=course,
                staff_id=self.staff_user
            )
        except Exception as e:
            print(f"❌ ERROR creating initial subject: {e}")
            connection.rollback()

        pre_creation_state = self.get_db_state('Before Creating Duplicate Subject')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating duplicate subject with:")
        print(f"  - ID: {subject_id}")
        print(f"  - Name: {subject_name}")
        print(f"  - Description: {description}")
        print(f"  - Course ID: {course_id}")

        error_caught = False
        error_message = None

        try:
            # Thử tạo tiếp subject với subject_id trùng lặp
            Subjects.objects.create(
                subject_name=subject_name,
                course_id=course,
                staff_id=self.staff_user
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING DUPLICATE SUBJECT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Duplicate Subject')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Subject creation phải fail, subjects_count không tăng
        if error_caught or post_creation_state['subjects_count'] == pre_creation_state['subjects_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Subject creation failed as expected due to duplicate subject_id")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Subject was created despite duplicate subject_id")
            self.fail("Subject creation should fail for duplicate subject_id")

    def S_ADD_NA_01_subject_name_empty_string_ERROR(self):
        """S-ADD-NA-01: subject_name has empty string - ERROR."""
        print("\n" + "*"*100)
        print("\n🔍 S-ADD-NA-01: subject_name has empty string - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        subject_name = ''  # subject_name là chuỗi rỗng
        description = 'Any Description'

        # Đảm bảo course tồn tại
        course, _ = Courses.objects.get_or_create(
            id=1,
            defaults={'course_name': 'Default Course'}
        )
        course_id = course.id

        pre_creation_state = self.get_db_state('Before Creating Subject')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating subject with:")
        print(f"  - Name: {subject_name} (empty string)")
        print(f"  - Description: {description}")
        print(f"  - Course ID: {course_id}")

        subject = None
        error_caught = False
        error_message = None

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
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Subject')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Subject creation phải fail, subjects_count không tăng
        if error_caught or post_creation_state['subjects_count'] == pre_creation_state['subjects_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Subject creation failed as expected due to empty subject_name")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Subject was created despite empty subject_name")
            self.fail("Subject creation should fail for empty subject_name")

    def S_ADD_NA_02_subject_name_one_char_ERROR(self):
        """S-ADD-NA-02: subject_name has 1 character - ERROR."""
        print("\n" + "*"*100)
        print("\n🔍 S-ADD-NA-02: subject_name has 1 character - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        subject_name = 'A'  # subject_name có 1 ký tự
        description = 'Any Description'

        # Đảm bảo course tồn tại
        course, _ = Courses.objects.get_or_create(
            id=1,
            defaults={'course_name': 'Default Course'}
        )
        course_id = course.id

        pre_creation_state = self.get_db_state('Before Creating Subject')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating subject with:")
        print(f"  - Name: {subject_name}")
        print(f"  - Description: {description}")
        print(f"  - Course ID: {course_id}")

        subject = None
        error_caught = False
        error_message = None

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
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Subject')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Subject creation phải fail, subjects_count không tăng
        if error_caught or post_creation_state['subjects_count'] == pre_creation_state['subjects_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Subject creation failed as expected due to subject_name length 1 character")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Subject was created despite subject_name length 1 character")
            self.fail("Subject creation should fail for subject_name length 1 character")

    def S_ADD_NA_03_subject_name_two_chars_SUCCESS(self):
        """S-ADD-NA-03: subject_name has 2 characters - SUCCESS."""
        print("\n" + "*"*100)
        print("\n🔍 S-ADD-NA-03: subject_name has 2 characters - SUCCESS.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        subject_name = 'BA'  # subject_name có 2 ký tự
        description = 'Any Description'

        # Đảm bảo course tồn tại
        course, _ = Courses.objects.get_or_create(
            id=1,
            defaults={'course_name': 'Default Course'}
        )
        course_id = course.id

        pre_creation_state = self.get_db_state('Before Creating Subject')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating subject with:")
        print(f"  - Name: {subject_name}")
        print(f"  - Description: {description}")
        print(f"  - Course ID: {course_id}")

        subject = None
        error_caught = False
        error_message = None

        try:
            subject = Subjects.objects.create(
                subject_name=subject_name,
                course_id=course,
                staff_id=self.staff_user
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SUBJECT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Subject')
            self.print_db_state(post_creation_state, "AFTER CREATION")

        else:
            post_creation_state = pre_creation_state

        # Subject creation phải thành công, subjects_count tăng
        if (not error_caught) and (post_creation_state['subjects_count'] == pre_creation_state['subjects_count'] + 1):
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Subject creation succeeded as expected with subject_name length 2 characters")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Subject creation failed unexpectedly with subject_name length 2 characters")
            self.fail("Subject creation should succeed for subject_name length 2 characters")

    def S_ADD_NA_04_subject_name_three_chars_SUCCESS(self):
        """S-ADD-NA-04: subject_name has 3 characters - SUCCESS."""
        print("\n" + "*"*100)
        print("\n🔍 S-ADD-NA-04: subject_name has 3 characters - SUCCESS.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        subject_name = 'IT1'  # subject_name có 3 ký tự
        description = 'Any Description'

        # Đảm bảo course tồn tại
        course, _ = Courses.objects.get_or_create(
            id=1,
            defaults={'course_name': 'Default Course'}
        )
        course_id = course.id

        pre_creation_state = self.get_db_state('Before Creating Subject')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating subject with:")
        print(f"  - Name: {subject_name}")
        print(f"  - Description: {description}")
        print(f"  - Course ID: {course_id}")

        subject = None
        error_caught = False
        error_message = None

        try:
            subject = Subjects.objects.create(
                subject_name=subject_name,
                course_id=course,
                staff_id=self.staff_user
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SUBJECT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Subject')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Subject creation phải thành công, subjects_count tăng
        if (not error_caught) and (post_creation_state['subjects_count'] == pre_creation_state['subjects_count'] + 1):
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Subject creation succeeded as expected with subject_name length 3 characters")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Subject creation failed unexpectedly with subject_name length 3 characters")
            self.fail("Subject creation should succeed for subject_name length 3 characters")

    def S_ADD_NA_05_subject_name_49_chars_SUCCESS(self):
        """S-ADD-NA-05: subject_name has 49 characters - SUCCESS."""
        print("\n" + "*"*100)
        print("\n🔍 S-ADD-NA-05: subject_name has 49 characters - SUCCESS.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        subject_name = 'Introduction to Software Quality Assurance Concepts'  # 49 ký tự
        description = 'Any Description'

        # Đảm bảo course tồn tại
        course, _ = Courses.objects.get_or_create(
            id=1,
            defaults={'course_name': 'Default Course'}
        )
        course_id = course.id

        pre_creation_state = self.get_db_state('Before Creating Subject')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating subject with:")
        print(f"  - Name: {subject_name}")
        print(f"  - Description: {description}")
        print(f"  - Course ID: {course_id}")

        subject = None
        error_caught = False
        error_message = None

        try:
            subject = Subjects.objects.create(
                subject_name=subject_name,
                course_id=course,
                staff_id=self.staff_user
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SUBJECT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Subject')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Subject creation phải thành công, subjects_count tăng
        if (not error_caught) and (post_creation_state['subjects_count'] == pre_creation_state['subjects_count'] + 1):
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Subject creation succeeded as expected with subject_name length 49 characters")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Subject creation failed unexpectedly with subject_name length 49 characters")
            self.fail("Subject creation should succeed for subject_name length 49 characters")

    def S_ADD_NA_06_subject_name_50_chars_SUCCESS(self):
        """S-ADD-NA-06: subject_name has 50 characters - SUCCESS."""
        print("\n" + "*"*100)
        print("\n🔍 S-ADD-NA-06: subject_name has 50 characters - SUCCESS.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        subject_name = 'Advanced Topics in Software Testing and QA Methods'  # 50 ký tự
        description = 'Any Description'

        # Đảm bảo course tồn tại
        course, _ = Courses.objects.get_or_create(
            id=1,
            defaults={'course_name': 'Default Course'}
        )
        course_id = course.id

        pre_creation_state = self.get_db_state('Before Creating Subject')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating subject with:")
        print(f"  - Name: {subject_name}")
        print(f"  - Description: {description}")
        print(f"  - Course ID: {course_id}")

        subject = None
        error_caught = False
        error_message = None

        try:
            subject = Subjects.objects.create(
                subject_name=subject_name,
                course_id=course,
                staff_id=self.staff_user
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SUBJECT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Subject')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Subject creation phải thành công, subjects_count tăng
        if (not error_caught) and (post_creation_state['subjects_count'] == pre_creation_state['subjects_count'] + 1):
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Subject creation succeeded as expected with subject_name length 50 characters")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Subject creation failed unexpectedly with subject_name length 50 characters")
            self.fail("Subject creation should succeed for subject_name length 50 characters")

    def S_ADD_NA_07_subject_name_51_chars_ERROR(self):
        """S-ADD-NA-07: subject_name has 51 characters - ERROR."""
        print("\n" + "*"*100)
        print("\n🔍 S-ADD-NA-07: subject_name has 51 characters - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        subject_name = 'Comprehensive Guide to Software Testing Techniques'  # 51 ký tự
        description = 'Any Description'

        # Đảm bảo course tồn tại
        course, _ = Courses.objects.get_or_create(
            id=1,
            defaults={'course_name': 'Default Course'}
        )
        course_id = course.id

        pre_creation_state = self.get_db_state('Before Creating Subject')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating subject with:")
        print(f"  - Name: {subject_name}")
        print(f"  - Description: {description}")
        print(f"  - Course ID: {course_id}")

        subject = None
        error_caught = False
        error_message = None

        try:
            subject = Subjects.objects.create(
                subject_name=subject_name,
                course_id=course,
                staff_id=self.staff_user
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SUBJECT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Subject')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Subject creation phải thất bại, subjects_count không tăng
        if error_caught or post_creation_state['subjects_count'] == pre_creation_state['subjects_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Subject creation failed as expected due to subject_name length > 50")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Subject was created despite subject_name length > 50")
            self.fail("Subject creation should fail for subject_name length > 50")

    def S_ADD_NA_08_subject_name_special_char_ERROR(self):
        """S-ADD-NA-08: subject_name contains special character - ERROR."""
        print("\n" + "*"*100)
        print("\n🔍 S-ADD-NA-08: subject_name contains special character - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        subject_name = 'AI@'  # Có ký tự đặc biệt '@'
        description = 'Any Description'

        # Đảm bảo course tồn tại
        course, _ = Courses.objects.get_or_create(
            id=1,
            defaults={'course_name': 'Default Course'}
        )
        course_id = course.id

        pre_creation_state = self.get_db_state('Before Creating Subject')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating subject with:")
        print(f"  - Name: {subject_name}")
        print(f"  - Description: {description}")
        print(f"  - Course ID: {course_id}")

        subject = None
        error_caught = False
        error_message = None

        try:
            subject = Subjects.objects.create(
                subject_name=subject_name,
                course_id=course,
                staff_id=self.staff_user
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SUBJECT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Subject')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Subject creation phải thất bại, subjects_count không tăng
        if error_caught or post_creation_state['subjects_count'] == pre_creation_state['subjects_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Subject creation failed as expected due to special character in subject_name")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Subject was created despite special character in subject_name")
            self.fail("Subject creation should fail for subject_name containing special characters")

    def S_ADD_NA_09_subject_name_duplicated_ERROR(self):
        """S-ADD-NA-09: subject_name is duplicated - ERROR."""
        print("\n" + "*"*100)
        print("\n🔍 S-ADD-NA-09: subject_name is duplicated - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        subject_name = 'BA'  # Tên môn học trùng lặp
        description = 'Any Description'

        # Đảm bảo course tồn tại
        course, _ = Courses.objects.get_or_create(
            id=1,
            defaults={'course_name': 'Default Course'}
        )
        course_id = course.id

        # Tạo trước một subject với subject_name này để test trùng lặp
        Subjects.objects.get_or_create(
            subject_name=subject_name,
            course_id=course,
            staff_id=self.staff_user,
            defaults={'description': 'Existing Subject'}
        )

        pre_creation_state = self.get_db_state('Before Creating Duplicate Subject')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating subject with duplicated name:")
        print(f"  - Name: {subject_name}")
        print(f"  - Description: {description}")
        print(f"  - Course ID: {course_id}")

        subject = None
        error_caught = False
        error_message = None

        try:
            subject = Subjects.objects.create(
                subject_name=subject_name,
                course_id=course,
                staff_id=self.staff_user
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SUBJECT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Subject')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Subject creation phải thất bại, subjects_count không tăng
        if error_caught or post_creation_state['subjects_count'] == pre_creation_state['subjects_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Subject creation failed as expected due to duplicated subject_name")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Subject was created despite duplicated subject_name")
            self.fail("Subject creation should fail for duplicated subject_name")

    def S_ADD_STA_01_course_id_empty_string_ERROR(self):
        """S-ADD-STA-01: course_id has empty string - ERROR."""
        print("\n" + "*"*100)
        print("\n🔍 S-ADD-STA-01: course_id has empty string - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        course_id = ''  # Giá trị course_id là chuỗi rỗng
        subject_name = "Some Subject"
        description = "Some Description"

        pre_creation_state = self.get_db_state('Before Creating Subject')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating subject with:")
        print(f"  - Course ID: '{course_id}' (empty string)")
        print(f"  - Name: {subject_name}")
        print(f"  - Description: {description}")

        subject = None
        error_caught = False
        error_message = None

        try:
            # Cố gắng lấy course với course_id rỗng, sẽ gây lỗi
            course = Courses.objects.get(id=course_id)

            subject = Subjects.objects.create(
                subject_name=subject_name,
                course_id=course,
                staff_id=self.staff_user
            )

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SUBJECT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Subject')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Subject creation phải thất bại, subjects_count không tăng
        if error_caught or post_creation_state['subjects_count'] == pre_creation_state['subjects_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Subject creation failed as expected due to empty course_id")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Subject was created despite empty course_id")
            self.fail("Subject creation should fail for empty course_id")

    def S_ADD_STA_02_course_id_exists_SUCCESS(self):
        """S-ADD-STA-02: course_id exists in the system - SUCCESS."""
        print("\n" + "*"*100)
        print("\n🔍 S-ADD-STA-02: course_id exists in the system - SUCCESS.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        course_id = 'C123'
        subject_name = "Valid Subject"
        description = "Valid description for subject"

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
        print(f"  - Description: {description}")

        subject = None
        error_caught = False
        error_message = None

        try:
            subject = Subjects.objects.create(
                subject_name=subject_name,
                course_id=course,
                staff_id=self.staff_user
            )

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SUBJECT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Subject')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Subject creation phải thành công, số lượng tăng lên
        if (not error_caught and 
            post_creation_state['subjects_count'] == pre_creation_state['subjects_count'] + 1):
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Subject created successfully with existing course_id")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Subject creation failed despite valid existing course_id")
            self.fail("Subject creation should succeed for existing course_id")

    def S_ADD_STA_03_course_id_not_exists_ERROR(self):
        """S-ADD-STA-03: course_id does not exist in the system - ERROR."""
        print("\n" + "*"*100)
        print("\n🔍 S-ADD-STA-03: course_id does not exist in the system - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        course_id = 'inactive'  # course_id không tồn tại
        subject_name = "Test Subject"
        description = "Test description"

        pre_creation_state = self.get_db_state('Before Creating Subject')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating subject with:")
        print(f"  - Course ID: {course_id}")
        print(f"  - Name: {subject_name}")
        print(f"  - Description: {description}")

        subject = None
        error_caught = False
        error_message = None

        try:
            # Thử lấy course với course_id không tồn tại sẽ raise DoesNotExist exception
            course = Courses.objects.get(id=course_id)

            subject = Subjects.objects.create(
                subject_name=subject_name,
                course_id=course,
                staff_id=self.staff_user
            )

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SUBJECT: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Subject')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Subject creation phải fail, số lượng không tăng
        if error_caught or post_creation_state['subjects_count'] == pre_creation_state['subjects_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Subject creation failed as expected due to non-existent course_id")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Subject was created despite non-existent course_id")
            self.fail("Subject creation should fail for non-existent course_id")
