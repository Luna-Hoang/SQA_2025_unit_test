from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta
import os
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.test.utils import override_settings
from .models import CustomUser, Staffs
from django.db import connection

class TeacherModelTest(TestCase):
    """
    Test suite for creating Teachers.
    Check various scenarios when creating a new teacher.
    """
    
    def setUp(self):
        """Set up test data before each method runs."""
        # Delete all existing students and users to start with a clean database
        Staffs.objects.all().delete()
        CustomUser.objects.filter(user_type='2').delete()
    
    def get_db_state(self, stage):
        """Record the current state of the database."""
        db_state = {
            'stage': stage,
            'staff_count': Staffs.objects.count(),
            'staffs': list(Staffs.objects.values('id', 'admin__username', 'admin__email'))
        }
        return db_state

    def print_db_state(self, state, label):
        """Print the DB state in a readable format."""
        staffs_info = ""
        if state['staffs']:
            for staff in state['staffs']:
                staffs_info += f"\n    - ID: {staff['id']}, Username: {staff['admin__username']}, Email: {staff['admin__email']}"
        else:
            staffs_info = "\n    (No data)"
            
        print(f"\n{'='*80}")
        print(f"\n  📊 {label} ({state['stage']})")
        print(f"\n  📋 Number of Staffs: {state['staff_count']}")
        print(f"\n  📝 Details:{staffs_info}")
        print(f"\n{'='*80}\n")
    
    def T_ADD_FN_01_first_name_has_empty_string_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-FN-01: first_name has empty string - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststaff1"
        email = "teststaff1@test.com"
        password = "Testpassword@123"
        first_name = ""  # Empty string to trigger error
        last_name = "Doe"
        specialization = "Python, Java"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: '{first_name}' {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"❌ User has linked staff object, but this should not happen for empty first_name")
                staff = user.staffs
            else:
                print(f"✅ User does not have linked staff object as expected due to empty first_name")

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

        # Đúng ra phải không tạo được teacher, staff_count không tăng
        if error_caught or post_creation_state['staff_count'] == pre_creation_state['staff_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Teacher creation failed as expected due to empty first_name")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Teacher was created despite empty first_name")
            self.fail("Teacher creation should fail for empty first_name")

    def T_ADD_FN_02_first_name_has_1_character_SUCCESS(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-FN-02: first_name has 1 character - SUCCESS")
        print("*"*100 + "\n")

        # Get initial state
        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        # Test data
        username = "teststaff2"
        email = "teststaff2@test.com"
        password = "Testpassword@123"
        first_name = "J"  # 1 character
        last_name = "Smith"
        specialization = "Java, Spring"
        status = "active"

        # Get state before creation
        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING TEACHER: {error_message}")
            connection.rollback()

        # Get state after creation
        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Teacher')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        # Evaluate test result
        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print(f"  - Teacher created with ID: {staff.id}")
            print(f"  - Username: {staff.admin.username}")
            print(f"  - Email: {staff.admin.email}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Could not create teacher")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Could not create teacher successfully")

    def T_ADD_FN_03_first_name_has_2_characters_SUCCESS(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-FN-03: first_name has 2 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststaff3"
        email = "teststaff3@test.com"
        password = "Testpassword@123"
        first_name = "Jo"  # Valid 2-character name
        last_name = "Smith"
        specialization = "C#, .NET"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")
                # Skip creating manually

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING TEACHER: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Teacher')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state  # fallback tránh lỗi

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print(f"  - Teacher created with ID: {staff.id}")
            print(f"  - Username: {staff.admin.username}")
            print(f"  - Email: {staff.admin.email}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Could not create teacher")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Could not create teacher successfully")

    def T_ADD_FN_04_first_name_has_49_characters_SUCCESS(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-FN-04: first_name has 49 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststaff4"
        email = "teststaff4@test.com"
        password = "Testpassword@123"
        first_name = "Johnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn"  # 49 characters
        last_name = "Smith"
        specialization = "HTML, CSS, JS"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

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

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print(f"  - Teacher created with ID: {staff.id}")
            print(f"  - Username: {staff.admin.username}")
            print(f"  - Email: {staff.admin.email}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Could not create teacher")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Could not create teacher successfully")

    def T_ADD_FN_05_first_name_has_50_characters_SUCCESS(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-FN-05: first_name has 50 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststaff5"
        email = "teststaff5@test.com"
        password = "Testpassword@123"
        first_name = "Johnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn"  # 50 characters
        last_name = "Brown"
        specialization = "Go, Rust"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

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

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print(f"  - Teacher created with ID: {staff.id}")
            print(f"  - Username: {staff.admin.username}")
            print(f"  - Email: {staff.admin.email}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Could not create teacher")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Could not create teacher successfully")

    def T_ADD_FN_06_first_name_has_51_characters_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-FN-06: first_name has 51 characters - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststaff6"
        email = "teststaff6@test.com"
        password = "Testpassword@123"
        first_name = "Johnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn"  # 51 characters
        last_name = "Doe"
        specialization = "Python, JavaScript"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"❌ User has linked staff object, but this should not happen for invalid first_name length")
                staff = user.staffs
            else:
                print(f"✅ User does not have linked staff object as expected due to invalid first_name length")

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

        # Đúng ra phải không tạo được teacher, số lượng staff không tăng
        if error_caught or post_creation_state['staff_count'] == pre_creation_state['staff_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Teacher creation failed as expected due to first_name length > 50")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Teacher was created despite invalid first_name length")
            self.fail("Teacher creation should fail for first_name length > 50 characters")

    def T_ADD_FN_07_first_name_contains_digits_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-FN-07: first_name contains digits - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststaff7"
        email = "teststaff7@test.com"
        password = "Testpassword@123"
        first_name = "John111"  # Contains digits, invalid
        last_name = "Doe"
        specialization = "Java, C#"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"❌ User has linked staff object, but this should not happen for invalid first_name with digits")
                staff = user.staffs
            else:
                print(f"✅ User does not have linked staff object as expected due to digits in first_name")

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

        # Đúng ra phải không tạo được teacher, số lượng staff không tăng
        if error_caught or post_creation_state['staff_count'] == pre_creation_state['staff_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Teacher creation failed as expected due to digits in first_name")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Teacher was created despite digits in first_name")
            self.fail("Teacher creation should fail for first_name containing digits")

    def T_ADD_FN_08_first_name_contains_special_characters_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-FN-08: first_name contains special characters - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststaff8"
        email = "teststaff8@test.com"
        password = "Testpassword@123"
        first_name = "John@"  # Contains special character '@', invalid
        last_name = "Doe"
        specialization = "Python, JavaScript"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"❌ User has linked staff object, but this should not happen for invalid first_name with special characters")
                staff = user.staffs
            else:
                print(f"✅ User does not have linked staff object as expected due to special characters in first_name")

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

        # Đúng ra phải không tạo được teacher, số lượng staff không tăng
        if error_caught or post_creation_state['staff_count'] == pre_creation_state['staff_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Teacher creation failed as expected due to special characters in first_name")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Teacher was created despite special characters in first_name")
            self.fail("Teacher creation should fail for first_name containing special characters")

    def T_ADD_LN_01_last_name_has_empty_string_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-LN-01: last_name has empty string - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststaff2"
        email = "teststaff2@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = ""  # Empty last name to trigger error
        specialization = "Python, Java"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} '{last_name}'")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"❌ User has linked staff object, but this should not happen for empty last_name")
                staff = user.staffs
            else:
                print(f"✅ User does not have linked staff object as expected due to empty last_name")

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

        # Đúng ra phải không tạo được teacher, staff_count không tăng
        if error_caught or post_creation_state['staff_count'] == pre_creation_state['staff_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Teacher creation failed as expected due to empty last_name")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Teacher was created despite empty last_name")
            self.fail("Teacher creation should fail for empty last_name")

    def T_ADD_LN_02_last_name_has_1_character_SUCCESS(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-LN-02: last_name has 1 character - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststaff3"
        email = "teststaff3@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "S"  # 1-character last_name, valid case
        specialization = "JavaScript, React"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

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

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print(f"  - Teacher created with ID: {staff.id}")
            print(f"  - Username: {staff.admin.username}")
            print(f"  - Email: {staff.admin.email}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Could not create teacher")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Could not create teacher successfully")

    def T_ADD_LN_03_last_name_has_2_characters_SUCCESS(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-LN-03: last_name has 2 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststaff4"
        email = "teststaff4@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "St"  # 2-character last_name, valid case
        specialization = "Python, Django"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

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

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print(f"  - Teacher created with ID: {staff.id}")
            print(f"  - Username: {staff.admin.username}")
            print(f"  - Email: {staff.admin.email}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Could not create teacher")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Could not create teacher successfully")

    def T_ADD_LN_04_last_name_has_49_characters_SUCCESS(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-LN-04: last_name has 49 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststaff5"
        email = "teststaff5@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Steveeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"  # 49 characters
        specialization = "Python, Django"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

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

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print(f"  - Teacher created with ID: {staff.id}")
            print(f"  - Username: {staff.admin.username}")
            print(f"  - Email: {staff.admin.email}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Could not create teacher")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Could not create teacher successfully")

    def T_ADD_LN_05_last_name_has_50_characters_SUCCESS(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-LN-05: last_name has 50 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststaff6"
        email = "teststaff6@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Steveeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"  # 50 characters
        specialization = "Python, Django"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

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

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print(f"  - Teacher created with ID: {staff.id}")
            print(f"  - Username: {staff.admin.username}")
            print(f"  - Email: {staff.admin.email}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Could not create teacher")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Could not create teacher successfully")

    def T_ADD_LN_06_last_name_has_51_characters_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-LN-06: last_name has 51 characters - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststaff7"
        email = "teststaff7@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Steveeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"  # 51 characters
        specialization = "Python, Django"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

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

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Teacher should NOT be created with invalid last_name length")
            self.fail("Teacher created despite invalid last_name length")
        else:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Creation blocked due to invalid last_name length")
            if error_message:
                print(f"  - Error: {error_message}")

    def T_ADD_LN_07_last_name_contains_digits_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-LN-07: last_name contains digits - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststaff8"
        email = "teststaff8@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Steve111"  # last_name chứa số
        specialization = "Java, Spring"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

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

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Teacher should NOT be created with invalid last_name containing digits")
            self.fail("Teacher created despite invalid last_name containing digits")
        else:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Creation blocked due to invalid last_name containing digits")
            if error_message:
                print(f"  - Error: {error_message}")

    def T_ADD_LN_08_last_name_contains_special_characters_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-LN-08: last_name contains special characters - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststaff9"
        email = "teststaff9@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Steve@"  # last_name chứa ký tự đặc biệt
        specialization = "Python, Django"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

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

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Teacher should NOT be created with invalid last_name containing special characters")
            self.fail("Teacher created despite invalid last_name containing special characters")
        else:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Creation blocked due to invalid last_name containing special characters")
            if error_message:
                print(f"  - Error: {error_message}")

    def T_ADD_UN_01_user_name_has_empty_string_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-UN-01: user_name has empty string - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = ""  # username rỗng gây lỗi
        email = "testuser1@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        specialization = "Java, Spring"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: '{username}'")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

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

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Teacher should NOT be created with empty username")
            self.fail("Teacher created despite empty username")
        else:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Creation blocked due to empty username")
            if error_message:
                print(f"  - Error: {error_message}")

    def T_ADD_UN_02_user_name_has_2_characters_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-UN-02: user_name has 2 characters - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "jo"  # 2 ký tự, gây lỗi do giới hạn 3-30
        email = "testuser2@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        specialization = "Java, Spring"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: '{username}'")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

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

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Teacher should NOT be created with username length < 3")
            self.fail("Teacher created despite username length < 3")
        else:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Creation blocked due to username length < 3")
            if error_message:
                print(f"  - Error: {error_message}")

    def T_ADD_UN_03_user_name_has_3_characters_SUCCESS(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-UN-03: user_name has 3 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "joh"  # 3 characters, valid
        email = "joh@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        specialization = "C, C++"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")
                # Skip manual creation if not linked

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING TEACHER: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Teacher')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state  # fallback avoid error

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print(f"  - Teacher created with ID: {staff.id}")
            print(f"  - Username: {staff.admin.username}")
            print(f"  - Email: {staff.admin.email}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Could not create teacher")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Could not create teacher successfully")

    def T_ADD_UN_04_user_name_has_4_characters_SUCCESS(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-UN-04: user_name has 4 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "john"  # 4 characters, valid
        email = "john@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        specialization = "C, C++"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")
                # Skip manual creation if not linked

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING TEACHER: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Teacher')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state  # fallback avoid error

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print(f"  - Teacher created with ID: {staff.id}")
            print(f"  - Username: {staff.admin.username}")
            print(f"  - Email: {staff.admin.email}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Could not create teacher")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Could not create teacher successfully")

    def T_ADD_UN_05_user_name_has_29_characters_SUCCESS(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-UN-05: user_name has 29 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "johnsteveeeeeeeeeeeeeeeeeeeee"  # 29 characters
        email = "john29@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        specialization = "Python, AI"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

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

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print(f"  - Teacher created with ID: {staff.id}")
            print(f"  - Username: {staff.admin.username}")
            print(f"  - Email: {staff.admin.email}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Could not create teacher")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Could not create teacher successfully")

    def T_ADD_UN_06_user_name_has_30_characters_SUCCESS(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-UN-06: user_name has 30 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "johnsteveeeeeeeeeeeeeeeeeeeeee"  # 30 characters
        email = "john30@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        specialization = "Python, AI"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

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

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print(f"  - Teacher created with ID: {staff.id}")
            print(f"  - Username: {staff.admin.username}")
            print(f"  - Email: {staff.admin.email}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Could not create teacher")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Could not create teacher successfully")

    def T_ADD_UN_07_user_name_has_31_characters_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-UN-07: user_name has 31 characters - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "johnsteveeeeeeeeeeeeeeeeeeeeeee"  # 31 characters
        email = "john31@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        specialization = "Python, AI"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

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

        if error_caught:
            print("\n🟢 TEST RESULT: PASSED")
            print(f"  - Expected error was caught: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Teacher creation should have failed due to invalid username length")
            self.fail("Teacher was created despite username exceeding 30 characters")

    def T_ADD_UN_08_user_name_starts_with_digit_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-UN-08: user_name starts with a digit - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "9johnsteve"  # Starts with digit
        email = "digitstart@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        specialization = "Python, AI"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

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

        if error_caught:
            print("\n🟢 TEST RESULT: PASSED")
            print(f"  - Expected error was caught: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Teacher creation should have failed due to username starting with digit")
            self.fail("Teacher was created despite username starting with a digit")

    def T_ADD_UN_09_user_name_contains_special_characters_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-UN-09: user_name contains special characters - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "johnsteve#"  # Contains special character
        email = "specialchar@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        specialization = "AI, Data"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

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

        if error_caught:
            print("\n🟢 TEST RESULT: PASSED")
            print(f"  - Expected error was caught: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Teacher creation should have failed due to special characters in username")
            self.fail("Teacher was created despite invalid username containing special characters")

    def T_ADD_UN_10_user_name_is_duplicated_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-UN-10: user_name is duplicated - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "john"  # Username đã tồn tại
        email_1 = "john@test.com"
        email_2 = "duplicatejohn@test.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        specialization = "Web Dev"
        status = "active"

        # Tạo user đầu tiên (hợp lệ)
        print("\n📌 Creating first teacher (should be successful)")
        try:
            user1 = CustomUser.objects.create_user(
                username=username,
                email=email_1,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )
            from time import sleep
            sleep(0.1)
            assert hasattr(user1, 'staffs')
            print("✅ First user created successfully.\n")
        except Exception as e:
            print(f"❌ Error creating first user: {e}")
            self.fail("Failed to create initial user for duplicate test")

        pre_creation_state = self.get_db_state('Before Creating Duplicate Teacher')
        self.print_db_state(pre_creation_state, "BEFORE DUPLICATE CREATION")

        print("\n📌 Attempting to create duplicate teacher with same username:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email_2}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        error_caught = False
        error_message = None

        try:
            user2 = CustomUser.objects.create_user(
                username=username,
                email=email_2,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )
            print("❌ Duplicate user was created - this is a bug.")
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n✅ Expected error was caught: {error_message}")
            connection.rollback()

        if error_caught:
            print("\n🟢 TEST RESULT: PASSED")
            print(f"  - System correctly prevented duplicate username: {username}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - System allowed creation of a duplicate username.")
            self.fail("Duplicate username was allowed but should have been rejected.")

    def T_ADD_EM_01_email_has_empty_string_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-EM-01: email has empty string - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "emptyemailstaff"
        email = ""  # Empty email to trigger error
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        specialization = "Python"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"❌ Unexpected success: User has staff object despite empty email")
                staff = user.staffs
            else:
                print(f"❌ Unexpected success: User created but has no linked staff object")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n✅ Expected error was caught: {error_message}")
            connection.rollback()

        if error_caught:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - System correctly rejected empty email.")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - System allowed creation with empty email.")
            self.fail("Empty email was allowed but should have been rejected.")

    def T_ADD_EM_02_email_has_7_characters_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-EM-02: email has 7 characters - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "shortemailstaff"
        email = "s@x.com"  # 7 characters
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        specialization = "Python"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email} (length={len(email)})")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"❌ Unexpected success: User has staff object despite short email")
                staff = user.staffs
            else:
                print(f"❌ Unexpected success: User created but has no linked staff object")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n✅ Expected error was caught: {error_message}")
            connection.rollback()

        if error_caught:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - System correctly rejected short email.")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - System allowed creation with invalid short email.")
            self.fail("Email with 7 characters was allowed but should have been rejected.")

    def T_ADD_EM_03_email_has_8_characters_SUCCESS(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-EM-03: email has 8 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "email8chars"
        email = "st@x.com"  # 8 characters
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        specialization = "JavaScript"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email} (length={len(email)})")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

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

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print(f"  - Teacher created with ID: {staff.id}")
            print(f"  - Username: {staff.admin.username}")
            print(f"  - Email: {staff.admin.email}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Could not create teacher")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Could not create teacher successfully")

    def T_ADD_EM_04_email_has_9_characters_SUCCESS(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-EM-04: email has 9 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "email9chars"
        email = "ste@x.com"  # 9 characters
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        specialization = "HTML/CSS"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email} (length={len(email)})")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

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

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print(f"  - Teacher created with ID: {staff.id}")
            print(f"  - Username: {staff.admin.username}")
            print(f"  - Email: {staff.admin.email}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Could not create teacher")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Could not create teacher successfully")

    def T_ADD_EM_05_email_has_49_characters_SUCCESS(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-EM-05: email has 49 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "email49chars"
        email = "steveeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee@gmail.com"  # 49 characters
        password = "Testpassword@123"
        first_name = "Steve"
        last_name = "Jobs"
        specialization = "Python"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email} (length={len(email)})")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

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

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print(f"  - Teacher created with ID: {staff.id}")
            print(f"  - Username: {staff.admin.username}")
            print(f"  - Email: {staff.admin.email}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Could not create teacher")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Could not create teacher successfully")

    def T_ADD_EM_06_email_has_50_characters_SUCCESS(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-EM-06: email has 50 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "email50chars"
        email = "steveeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee@gmail.com"  # 50 characters
        password = "Testpassword@123"
        first_name = "Steve"
        last_name = "Jobs"
        specialization = "Python"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email} (length={len(email)})")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

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

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print(f"  - Teacher created with ID: {staff.id}")
            print(f"  - Username: {staff.admin.username}")
            print(f"  - Email: {staff.admin.email}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Could not create teacher")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Could not create teacher successfully")

    def T_ADD_EM_07_email_has_51_characters_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-EM-07: email has 51 characters - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "email51chars"
        email = "steveeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee@gmail.com"  # 51 characters
        password = "Testpassword@123"
        first_name = "Steve"
        last_name = "Jobs"
        specialization = "Python"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email} (length={len(email)})")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

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

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Teacher should NOT have been created")
            self.fail("Teacher was created despite invalid email length")
        else:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Correctly failed to create teacher due to email length")
            if error_message:
                print(f"  - Error: {error_message}")

    def T_ADD_EM_08_email_missing_domain_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-EM-08: email missing domain - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "email_missing_domain"
        email = "steve@.com"  # invalid domain part
        password = "Testpassword@123"
        first_name = "Steve"
        last_name = "Jobs"
        specialization = "Python"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

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

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Teacher should NOT have been created")
            self.fail("Teacher was created despite invalid email format")
        else:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Correctly failed to create teacher due to invalid email format")
            if error_message:
                print(f"  - Error: {error_message}")

    def T_ADD_EM_09_email_missing_at_symbol_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-EM-09: email missing @ symbol - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "email_missing_at"
        email = "stevegmail.com"  # missing @ symbol
        password = "Testpassword@123"
        first_name = "Steve"
        last_name = "Jobs"
        specialization = "Python"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

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

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Teacher should NOT have been created")
            self.fail("Teacher was created despite invalid email format")
        else:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Correctly failed to create teacher due to invalid email format")
            if error_message:
                print(f"  - Error: {error_message}")

    def T_ADD_EM_10_email_contains_special_characters_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-EM-10: email contains special characters except '@' - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "email_special_char"
        email = "steve@gmail.com#"  # contains special character '#'
        password = "Testpassword@123"
        first_name = "Steve"
        last_name = "Jobs"
        specialization = "Python"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )

            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

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

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Teacher should NOT have been created")
            self.fail("Teacher was created despite invalid email containing special characters")
        else:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Correctly failed to create teacher due to invalid email special characters")
            if error_message:
                print(f"  - Error: {error_message}")

    def T_ADD_EM_11_email_is_duplicated_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-EM-11: email is duplicated - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username1 = "johnuser1"
        email = "john@example.com"
        password = "Testpassword@123"
        first_name = "John"
        last_name = "Doe"
        specialization = "Java"
        status = "active"

        # Step 1: Tạo user đầu tiên với email
        try:
            user1 = CustomUser.objects.create_user(
                username=username1,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )
            from time import sleep
            sleep(0.1)
        except Exception as e:
            print(f"❌ ERROR CREATING FIRST USER: {e}")
            connection.rollback()
            self.fail("Setup failed: cannot create initial user")

        pre_creation_state = self.get_db_state('Before Creating Duplicate Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        username2 = "johnuser2"  # username khác, nhưng email trùng
        error_caught = False
        error_message = None
        staff = None

        print("\n📌 Creating teacher with duplicated email:")
        print(f"  - Username: {username2}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        try:
            user2 = CustomUser.objects.create_user(
                username=username2,
                email=email,  # duplicate email
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )
            from time import sleep
            sleep(0.1)

            if hasattr(user2, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user2.staffs
            else:
                print(f"❌ User does not have linked staff object")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING TEACHER WITH DUPLICATE EMAIL: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Duplicate Teacher')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Teacher should NOT have been created with duplicated email")
            self.fail("Teacher was created despite duplicated email")
        else:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Correctly failed to create teacher due to duplicated email")
            if error_message:
                print(f"  - Error: {error_message}")

    def T_ADD_PW_01_password_has_empty_string_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-PW-01: password has empty string - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststaff_pw01"
        email = "teststaff_pw01@test.com"
        password = ""  # Empty password to trigger error
        first_name = "John"
        last_name = "Doe"
        specialization = "Python"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )
            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING TEACHER: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Teacher')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state  # fallback tránh lỗi

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Teacher should NOT have been created with empty password")
            self.fail("Teacher was created despite empty password")
        else:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Correctly failed to create teacher due to empty password")
            if error_message:
                print(f"  - Error: {error_message}")

    def T_ADD_PW_02_password_has_7_characters_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-PW-02: password has 7 characters - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststaff_pw02"
        email = "teststaff_pw02@test.com"
        password = "John@12"  # 7 characters - should fail
        first_name = "John"
        last_name = "Doe"
        specialization = "Python"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )
            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING TEACHER: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Teacher')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state  # fallback tránh lỗi

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Teacher should NOT have been created with password length 7")
            self.fail("Teacher was created despite password length 7")
        else:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Correctly failed to create teacher due to short password")
            if error_message:
                print(f"  - Error: {error_message}")

    def T_ADD_PW_03_password_has_8_characters_SUCCESS(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-PW-03: password has 8 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststaff_pw03"
        email = "teststaff_pw03@test.com"
        password = "John@123"  # 8 characters - valid
        first_name = "John"
        last_name = "Doe"
        specialization = "Python"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )
            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING TEACHER: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Teacher')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state  # fallback tránh lỗi

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print(f"  - Teacher created with ID: {staff.id}")
            print(f"  - Username: {staff.admin.username}")
            print(f"  - Email: {staff.admin.email}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Could not create teacher with valid password length 8")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Could not create teacher successfully")

    def T_ADD_PW_04_password_has_9_characters_SUCCESS(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-PW-04: password has 9 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststaff_pw04"
        email = "teststaff_pw04@test.com"
        password = "John@1234"  # 9 characters - valid
        first_name = "John"
        last_name = "Doe"
        specialization = "Python"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )
            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING TEACHER: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Teacher')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state  # fallback tránh lỗi

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print(f"  - Teacher created with ID: {staff.id}")
            print(f"  - Username: {staff.admin.username}")
            print(f"  - Email: {staff.admin.email}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Could not create teacher with valid password length 9")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Could not create teacher successfully")

    def T_ADD_PW_05_password_has_63_characters_SUCCESS(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-PW-05: password has 63 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststaff_pw05"
        email = "teststaff_pw05@test.com"
        password = "Johnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn@1234"  # 63 characters
        first_name = "John"
        last_name = "Doe"
        specialization = "Python"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )
            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING TEACHER: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Teacher')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state  # fallback tránh lỗi

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print(f"  - Teacher created with ID: {staff.id}")
            print(f"  - Username: {staff.admin.username}")
            print(f"  - Email: {staff.admin.email}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Could not create teacher with valid password length 63")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Could not create teacher successfully")

    def T_ADD_PW_06_password_has_64_characters_SUCCESS(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-PW-06: password has 64 characters - SUCCESS")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststaff_pw06"
        email = "teststaff_pw06@test.com"
        password = "Johnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn@1234"  # 64 characters
        first_name = "John"
        last_name = "Doe"
        specialization = "Python"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )
            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING TEACHER: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Teacher')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state  # fallback tránh lỗi

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print(f"  - Teacher created with ID: {staff.id}")
            print(f"  - Username: {staff.admin.username}")
            print(f"  - Email: {staff.admin.email}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Could not create teacher with valid password length 64")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Could not create teacher successfully")

    def T_ADD_PW_07_password_has_65_characters_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-PW-07: password has 65 characters - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststaff_pw07"
        email = "teststaff_pw07@test.com"
        password = "Johnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn@1234"  # 65 characters
        first_name = "John"
        last_name = "Doe"
        specialization = "Python"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )
            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING TEACHER: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Teacher')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state  # fallback tránh lỗi

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Teacher created but expected failure due to password length > 64")
            self.fail("Teacher creation should fail due to password length > 64")
        else:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Teacher creation failed as expected due to password length > 64")
            if error_message:
                print(f"  - Error: {error_message}")

    def T_ADD_PW_08_password_missing_uppercase_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-PW-08: password missing uppercase letter - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststaff_pw08"
        email = "teststaff_pw08@test.com"
        password = "john@1234"  # no uppercase letter
        first_name = "John"
        last_name = "Doe"
        specialization = "Python"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )
            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

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

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Teacher created but expected failure due to missing uppercase letter in password")
            self.fail("Teacher creation should fail due to missing uppercase letter in password")
        else:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Teacher creation failed as expected due to missing uppercase letter in password")
            if error_message:
                print(f"  - Error: {error_message}")

    def T_ADD_PW_09_password_missing_lowercase_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-PW-09: password missing lowercase letter - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststaff_pw09"
        email = "teststaff_pw09@test.com"
        password = "JOHN@1234"  # no lowercase letter
        first_name = "John"
        last_name = "Doe"
        specialization = "Python"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )
            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

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

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Teacher created but expected failure due to missing lowercase letter in password")
            self.fail("Teacher creation should fail due to missing lowercase letter in password")
        else:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Teacher creation failed as expected due to missing lowercase letter in password")
            if error_message:
                print(f"  - Error: {error_message}")

    def T_ADD_PW_10_password_missing_digit_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-PW-10: password missing digit - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststaff_pw10"
        email = "teststaff_pw10@test.com"
        password = "John@nnn"  # no digit
        first_name = "John"
        last_name = "Doe"
        specialization = "Python"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )
            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

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

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Teacher created but expected failure due to missing digit in password")
            self.fail("Teacher creation should fail due to missing digit in password")
        else:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Teacher creation failed as expected due to missing digit in password")
            if error_message:
                print(f"  - Error: {error_message}")
                
    def T_ADD_PW_11_password_missing_special_character_ERROR(self):
        print("\n\n" + "*"*100)
        print("\n🔍 T-ADD-PW-11: password missing special characters - ERROR")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        username = "teststaff_pw11"
        email = "teststaff_pw11@test.com"
        password = "John1234"  # no special character
        first_name = "John"
        last_name = "Doe"
        specialization = "Python"
        status = "active"

        pre_creation_state = self.get_db_state('Before Creating Teacher')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating teacher with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Specialization: {specialization}")
        print(f"  - Status: {status}\n")

        staff = None
        error_caught = False
        error_message = None

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )
            from time import sleep
            sleep(0.1)

            if hasattr(user, 'staffs'):
                print(f"✅ User has successfully linked staff object")
                staff = user.staffs
            else:
                print(f"❌ User does not have linked staff object")

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

        if not error_caught and staff and post_creation_state['staff_count'] > pre_creation_state['staff_count']:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Teacher created but expected failure due to missing special character in password")
            self.fail("Teacher creation should fail due to missing special character in password")
        else:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Teacher creation failed as expected due to missing special character in password")
            if error_message:
                print(f"  - Error: {error_message}")
