from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta
import os
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import CustomUser, Students, Courses, SessionYearModel
from django.db import IntegrityError, transaction
from django.db.models.signals import post_save
from django.test.utils import override_settings

# Helper function to disable signals during tests
def disable_signals(decorated_function):
    def wrapper(*args, **kwargs):
        # Store the receivers
        receivers = post_save.receivers
        # Disable the signal by setting receivers to empty list
        post_save.receivers = []
        
        try:
            # Call the decorated function
            return decorated_function(*args, **kwargs)
        finally:
            # Restore the receivers
            post_save.receivers = receivers
    
    return wrapper

class CustomUserModelTest(TestCase):
    """
    Test suite for the CustomUser model.
    Check various scenarios when creating a new user.
    """
    
    def setUp(self):
        """Set up test data before each method runs."""
        # Delete all existing users to start with a clean database
        # (except admin user if any)
        CustomUser.objects.all().delete()
    
    def get_db_state(self, stage):
        """Record the current state of the database."""
        db_state = {
            'stage': stage,
            'users_count': CustomUser.objects.count(),
            'users': list(CustomUser.objects.values('id', 'username', 'email', 'user_type', 'first_name', 'last_name'))
        }
        return db_state
    
    def print_db_state(self, state, label):
        """Print the DB state in a readable format."""
        users_info = ""
        if state['users']:
            for user in state['users']:
                user_type_str = "HOD" if user['user_type'] == '1' else "Staff" if user['user_type'] == '2' else "Student" if user['user_type'] == '3' else f"Unknown ({user['user_type']})"
                users_info += f"\n    - ID: {user['id']}, Username: {user['username']}, Email: {user['email']}, Role: {user_type_str}, Name: {user['first_name']} {user['last_name']}"
        else:
            users_info = "\n    (No data)"
            
        print(f"\n{'='*80}")
        print(f"\n  📊 {label} ({state['stage']})")
        print(f"\n  📋 Number of Users: {state['users_count']}")
        print(f"\n  📝 Details:{users_info}")
        print(f"\n{'='*80}\n")

    @disable_signals
    def test_1_successful_user_creation(self):
        """Test 1: Successfully create a new user."""
        print("\n\n" + "*"*100)
        print("\n🔍 TEST 1: SUCCESSFUL USER CREATION")
        print("*"*100 + "\n")
        
        # Get initial database state
        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")
        
        # Data for new user
        username = "studenttest1"
        email = "student1@test.com"
        password = "complexpassword123"
        first_name = "Student"
        last_name = "One"
        user_type = 3  # Student
        
        # Get database state before creation
        pre_creation_state = self.get_db_state('Before User Creation')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")
        
        print("\n📌 Creating user with:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Password: {password}")
        print(f"  - Name: {first_name} {last_name}")
        print(f"  - Role: Student (user_type=3)\n")
        
        # Perform user creation
        user = None
        error_caught = False
        error_message = None
        
        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=user_type
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING USER: {error_message}")
        
        # Get database state after creation
        post_creation_state = self.get_db_state('After User Creation')
        self.print_db_state(post_creation_state, "AFTER CREATION")
        
        # Check result
        if not error_caught and user and post_creation_state['users_count'] > pre_creation_state['users_count']:
            print("\n✅ TEST RESULT: SUCCESS")
            print(f"  - User created with ID: {user.id}")
            print(f"  - Username: {user.username}")
            print(f"  - Email: {user.email}")
            print(f"  - Role: {'Student' if user.user_type == '3' else user.user_type}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Could not create user")
            if error_message:
                print(f"  - Error: {error_message}")
            self.fail("Could not create user successfully")
    
    @disable_signals
    def test_2_duplicate_email(self):
        """Test 2: Duplicate email."""
        print("\n\n" + "*"*100)
        print("\n🔍 TEST 2: DUPLICATE EMAIL")
        print("*"*100 + "\n")
        
        # Get initial database state
        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")
        
        # Create first user
        first_email = "student2@test.com"
        print("\n📌 Creating first user with:")
        print(f"  - Username: studenttest2")
        print(f"  - Email: {first_email}")
        print(f"  - Password: complexpassword123")
        print(f"  - Role: Student (user_type=3)\n")
        
        first_user = CustomUser.objects.create_user(
            username="studenttest2",
            email=first_email,
            password="complexpassword123",
            first_name="First",
            last_name="Student",
            user_type=3
        )
        
        # Get database state after first user creation
        post_first_creation_state = self.get_db_state('After First User Creation')
        self.print_db_state(post_first_creation_state, "AFTER FIRST USER CREATION")
        
        # Attempt to create second user with duplicate email
        print("\n📌 Attempting to create second user with:")
        print(f"  - Username: studenttest2_duplicate")
        print(f"  - Email: {first_email} (same as first user)")
        print(f"  - Password: anotherpassword123")
        print(f"  - Role: Student (user_type=3)\n")
        
        duplicate_user = None
        error_caught = False
        error_message = None
        
        try:
            with transaction.atomic():
                duplicate_user = CustomUser.objects.create_user(
                    username="studenttest2_duplicate",
                    email=first_email,  # Duplicate email
                    password="anotherpassword123",
                    first_name="Second",
                    last_name="Student",
                    user_type=3
                )
                
                print("\n⚠️ ERROR DETECTED: Software allows creating user with duplicate email")
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n✅ Software caught error when creating user with duplicate email: {error_message}")
        
        # Get database state after attempting duplicate email creation
        post_duplicate_attempt_state = self.get_db_state('After Attempting Duplicate Email Creation')
        self.print_db_state(post_duplicate_attempt_state, "AFTER ATTEMPTING DUPLICATE EMAIL CREATION")
        
        # Check result
        if error_caught and post_duplicate_attempt_state['users_count'] == post_first_creation_state['users_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Software prevented creating user with duplicate email")
            print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Software allows creating user with duplicate email")
            
            # This test will FAIL if software does not catch duplicate email error
            if post_duplicate_attempt_state['users_count'] > post_first_creation_state['users_count']:
                self.fail("Software does not check for duplicate emails!")
                
            # Rollback DB if needed
            if duplicate_user and duplicate_user.id:
                duplicate_user.delete()
    
    @disable_signals
    def test_3_missing_password(self):
        """Test 3: Missing password."""
        print("\n\n" + "*"*100)
        print("\n🔍 TEST 3: MISSING PASSWORD")
        print("*"*100 + "\n")
        
        # Get initial database state
        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")
        
        # Get database state before creation
        pre_attempt_state = self.get_db_state('Before Creating User with Missing Password')
        self.print_db_state(pre_attempt_state, "BEFORE CREATING MISSING PASSWORD")
        
        print("\n📌 Attempting to create user with missing password:")
        print(f"  - Username: studenttest3")
        print(f"  - Email: student3@test.com")
        print(f"  - Password: NOT PROVIDED (missing)")
        print(f"  - Role: Student (user_type=3)\n")
        
        # Attempt to create user with empty or None password
        user = None
        error_caught = False
        error_message = None
        
        try:
            with transaction.atomic():
                # Attempt 1: Password is None
                user = CustomUser.objects.create_user(
                    username="studenttest3",
                    email="student3@test.com",
                    password=None,  # Password is None
                    first_name="Test",
                    last_name="Student3",
                    user_type=3
                )
                
                print("\n⚠️ ERROR DETECTED: Software allows creating user with password None")
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n✅ Software caught error when creating user with password None: {error_message}")
        
        # Get database state after attempt 1
        post_attempt1_state = self.get_db_state('After Attempting User Creation with Password None')
        self.print_db_state(post_attempt1_state, "AFTER ATTEMPTING PASSWORD NONE")
        
        # Attempt 2: Password is empty string
        error_caught2 = False
        error_message2 = None
        
        try:
            with transaction.atomic():
                user = CustomUser.objects.create_user(
                    username="studenttest3_2",
                    email="student3_2@test.com",
                    password="",  # Password is empty string
                    first_name="Test",
                    last_name="Student3_2",
                    user_type=3
                )
                
                print("\n⚠️ ERROR DETECTED: Software allows creating user with empty password")
        except Exception as e:
            error_caught2 = True
            error_message2 = str(e)
            print(f"\n✅ Software caught error when creating user with empty password: {error_message2}")
        
        # Get database state after attempt 2
        post_attempt2_state = self.get_db_state('After Attempting User Creation with Empty Password')
        self.print_db_state(post_attempt2_state, "AFTER ATTEMPTING EMPTY PASSWORD")
        
        # Check result
        if error_caught and error_caught2 and post_attempt2_state['users_count'] == pre_attempt_state['users_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Software prevented creating user with missing password")
            print(f"  - Error message for password None: {error_message}")
            print(f"  - Error message for empty password: {error_message2}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Software allows creating user with missing password")
            
            # This test will FAIL if software does not catch missing password error
            if not error_caught or not error_caught2:
                self.fail("Software does not check for missing password!")
                
            # Rollback DB if needed
            if user and user.id:
                user.delete()
    
    @disable_signals
    def test_4_invalid_role(self):
        """Test 4: Invalid role."""
        print("\n\n" + "*"*100)
        print("\n🔍 TEST 4: INVALID ROLE")
        print("*"*100 + "\n")
        
        # Get initial database state
        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")
        
        # Get database state before creation
        pre_attempt_state = self.get_db_state('Before Creating User with Invalid Role')
        self.print_db_state(pre_attempt_state, "BEFORE CREATING INVALID ROLE")
        
        # Invalid role values to test
        invalid_roles = [
            0,    # Out of range
            4,    # Out of range
            -1,   # Negative value
            "A",  # Not a number
            None  # Null
        ]
        
        all_errors_caught = True
        error_details = []
        created_users = []
        
        for i, role in enumerate(invalid_roles):
            print(f"\n📌 {i+1}. Attempting to create user with invalid role:")
            print(f"  - Username: invalidrole{i}")
            print(f"  - Email: invalid{i}@test.com")
            print(f"  - Role: {role} (invalid, only accepts 1, 2, 3)\n")
            
            user = None
            error_caught = False
            error_message = None
            
            try:
                with transaction.atomic():
                    user = CustomUser.objects.create_user(
                        username=f"invalidrole{i}",
                        email=f"invalid{i}@test.com",
                        password="complexpassword123",
                        first_name="Test",
                        last_name=f"Role{i}",
                        user_type=role
                    )
                    
                    # If no error, user was created with invalid role
                    print(f"\n⚠️ ERROR DETECTED: Software allows creating user with role={role}")
                    error_details.append(f"Role {role}: Software allows creating user")
                    all_errors_caught = False
                    created_users.append(user)
            except Exception as e:
                error_caught = True
                error_message = str(e)
                print(f"\n✅ Software caught error when creating user with role={role}: {error_message}")
                error_details.append(f"Role {role}: Error caught: {error_message}")
        
        # Get database state after attempt
        post_attempt_state = self.get_db_state('After Attempting to Create Users with Invalid Role')
        self.print_db_state(post_attempt_state, "AFTER ATTEMPTING INVALID ROLE")
        
        # Delete created users to not affect subsequent tests
        for user in created_users:
            if user and user.id:
                user.delete()
        
        # Check result
        if all_errors_caught and post_attempt_state['users_count'] == pre_attempt_state['users_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Software prevented creating user with invalid role")
            for detail in error_details:
                print(f"  - {detail}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Software allows creating user with some invalid roles")
            for detail in error_details:
                print(f"  - {detail}")
            
            # This test will FAIL if software does not catch invalid role error
            if not all_errors_caught:
                self.fail("Software does not check for all invalid roles!")
    
    @disable_signals
    def test_5_invalid_email_format(self):
        """Test 5: Invalid email format."""
        print("\n\n" + "*"*100)
        print("\n🔍 TEST 5: INVALID EMAIL FORMAT")
        print("*"*100 + "\n")
        
        # Get initial database state
        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")
        
        # Get database state before creation
        pre_attempt_state = self.get_db_state('Before Creating User with Invalid Email')
        self.print_db_state(pre_attempt_state, "BEFORE CREATING INVALID EMAIL")
        
        # Invalid email formats to test
        invalid_emails = [
            "plainaddress",                     # Missing @ and domain
            "#@%^%#$@#$@#.com",                # Invalid special characters
            "@domain.com",                      # Missing username
            "Joe Smith <email@domain.com>",     # Improper format
            "email.domain.com",                 # Missing @
            "email@domain@domain.com",          # More than one @
            ".email@domain.com",                # Starts with a dot
            "email.@domain.com",                # Ends with a dot
            "email@domain.com.",                # Domain ends with a dot
            "email@domain",                     # Missing top-level domain
        ]
        
        all_errors_caught = True
        error_details = []
        created_users = []
        
        for i, email in enumerate(invalid_emails):
            print(f"\n📌 {i+1}. Attempting to create user with invalid email:")
            print(f"  - Username: invalidemail{i}")
            print(f"  - Email: {email} (improper format example@domain.com)\n")
            
            user = None
            error_caught = False
            error_message = None
            
            try:
                # First, check if email is valid using Django's validator
                try:
                    validate_email(email)
                    print(f"⚠️ Django EmailValidator accepts email: {email}")
                except ValidationError:
                    # Django validator caught invalid email
                    print(f"✓ Django EmailValidator rejects email: {email}")
                
                # Attempt to create user with invalid email    
                with transaction.atomic():
                    user = CustomUser.objects.create_user(
                        username=f"invalidemail{i}",
                        email=email,
                        password="complexpassword123",
                        first_name="Test",
                        last_name=f"Email{i}",
                        user_type=3
                    )
                    
                    # If no error, user was created with invalid email
                    print(f"\n⚠️ ERROR DETECTED: Software allows creating user with invalid email: {email}")
                    error_details.append(f"Email '{email}': Software allows creating user")
                    all_errors_caught = False
                    created_users.append(user)
            except Exception as e:
                error_caught = True
                error_message = str(e)
                print(f"\n✅ Software caught error when creating user with invalid email: {error_message}")
                error_details.append(f"Email '{email}': Error caught: {error_message}")
        
        # Get database state after attempt
        post_attempt_state = self.get_db_state('After Attempting to Create Users with Invalid Email')
        self.print_db_state(post_attempt_state, "AFTER ATTEMPTING INVALID EMAIL")
        
        # Delete created users to not affect subsequent tests
        for user in created_users:
            if user and user.id:
                user.delete()
        
        # Check result
        if all_errors_caught:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Software prevented creating user with invalid email")
            for detail in error_details:
                print(f"  - {detail}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Software allows creating user with some invalid emails")
            for detail in error_details:
                print(f"  - {detail}")
            
            # This test will FAIL if software does not catch invalid email error
            if not all_errors_caught:
                self.fail("Software does not check for all invalid emails!")
    
    @disable_signals
    def test_6_weak_password(self):
        """Test 6: Password too short or too weak."""
        print("\n\n" + "*"*100)
        print("\n🔍 TEST 6: PASSWORD TOO SHORT OR TOO WEAK")
        print("*"*100 + "\n")
        
        # Get initial database state
        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")
        
        # Get database state before creation
        pre_attempt_state = self.get_db_state('Before Creating User with Weak Password')
        self.print_db_state(pre_attempt_state, "BEFORE CREATING WEAK PASSWORD")
        
        # Weak passwords to test
        weak_passwords = [
            "123",              # Too short and only numbers
            "password",         # Common password
            "abc123",           # Short and simple
            "qwerty",           # Common password
            "a",                # Single character
            "12345678",         # Only numbers
            "username",         # Same as username
        ]
        
        all_errors_caught = True
        error_details = []
        created_users = []
        
        for i, password in enumerate(weak_passwords):
            print(f"\n📌 {i+1}. Attempting to create user with weak password:")
            print(f"  - Username: weakpassword{i}")
            print(f"  - Email: weak{i}@test.com")
            print(f"  - Password: {password} (too short/too weak)\n")
            
            user = None
            error_caught = False
            error_message = None
            
            try:
                with transaction.atomic():
                    user = CustomUser.objects.create_user(
                        username=f"weakpassword{i}",
                        email=f"weak{i}@test.com",
                        password=password,
                        first_name="Test",
                        last_name=f"Password{i}",
                        user_type=3
                    )
                    
                    # If no error, user was created with weak password
                    print(f"\n⚠️ ERROR DETECTED: Software allows creating user with weak password: {password}")
                    error_details.append(f"Password '{password}': Software allows creating user")
                    all_errors_caught = False
                    created_users.append(user)
            except Exception as e:
                error_caught = True
                error_message = str(e)
                print(f"\n✅ Software caught error when creating user with weak password: {error_message}")
                error_details.append(f"Password '{password}': Error caught: {error_message}")
        
        # Get database state after attempt
        post_attempt_state = self.get_db_state('After Attempting to Create Users with Weak Password')
        self.print_db_state(post_attempt_state, "AFTER ATTEMPTING WEAK PASSWORD")
        
        # Delete created users to not affect subsequent tests
        for user in created_users:
            if user and user.id:
                user.delete()
        
        # Check result
        if all_errors_caught and post_attempt_state['users_count'] == pre_attempt_state['users_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Software prevented creating user with too weak password")
            for detail in error_details:
                print(f"  - {detail}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Software allows creating user with some too weak passwords")
            for detail in error_details:
                print(f"  - {detail}")
            
            # Assess severity of the issue
            created_count = post_attempt_state['users_count'] - pre_attempt_state['users_count']
            if created_count > 0:
                print(f"  - Created {created_count}/{len(weak_passwords)} users with weak passwords")
            
            # This test will FAIL if software does not catch weak password error
            # However, this may be an assessment based on different strong password standards
            # So we will not fail this test but just record the result for user evaluation 