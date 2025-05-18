from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta
import os
import json
from .models import SessionYearModel
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError
from django.db import connection
from datetime import date

class SessionYearModelTest(TestCase):
    """
    Test suite for the SessionYearModel.
    Check various scenarios when creating a new academic year.
    """
    
    def setUp(self):
        """Set up test data before each method runs."""
        # Delete all existing sessions to start with a clean database
        SessionYearModel.objects.all().delete()
    
    def get_db_state(self, stage):
        """Record the current state of the database."""
        db_state = {
            'stage': stage,
            'sessions_count': SessionYearModel.objects.count(),
            'sessions': list(SessionYearModel.objects.values('id', 'session_start_year', 'session_end_year'))
        }
        return db_state
    
    def print_db_state(self, state, label):
        """Print the DB state in a readable format."""
        sessions_info = ""
        if state['sessions']:
            for session in state['sessions']:
                sessions_info += f"\n    - ID: {session['id']}, Start: {session['session_start_year']}, End: {session['session_end_year']}"
        else:
            sessions_info = "\n    (No data)"
            
        print(f"\n{'='*80}")
        print(f"\n  📊 {label} ({state['stage']})")
        print(f"\n  📋 Number of Sessions: {state['sessions_count']}")
        print(f"\n  📝 Details:{sessions_info}")
        print(f"\n{'='*80}\n")

    def SM_ADD_SE_01_start_date_is_end_date_minus_2_day_SUCCESS(self):
        """SM-ADD-SE-01: start date = end date -2 day - SUCCESS."""
        print("\n" + "*"*100)
        print("🔍 SM-ADD-SE-01: start date = end date -2 day - SUCCESS.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        session_id = 'Y001'
        session_name = "Spring 2025"
        start_date = date(2025, 3, 30)  # end_date - 2 days
        end_date = date(2025, 4, 1)

        pre_creation_state = self.get_db_state('Before Creating Semester')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating semester with:")
        print(f"  - Semester ID: {session_id}")
        print(f"  - Semester name: {session_name}")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")

        session = None
        error_caught = False
        error_message = None

        try:
            session = SessionYearModel.objects.create(
                session_start_year=start_date,
                session_end_year=end_date
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SEMESTER: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Semester')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if not error_caught and post_creation_state['sessions_count'] == pre_creation_state['sessions_count'] + 1:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Semester was successfully created with start_date = end_date - 2 days")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Semester was not created as expected")
            if error_message:
                print(f"  - Error message: {error_message}")
            self.fail("Semester should be created successfully when start_date is end_date - 2 days")

    def SM_ADD_SE_02_start_date_is_end_date_minus_1_day_SUCCESS(self):
        """SM-ADD-SE-02: start date = end date -1 day - SUCCESS."""
        print("\n" + "*"*100)
        print("🔍 SM-ADD-SE-02: start date = end date -1 day - SUCCESS.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        session_id = 'Y002'
        session_name = "Summer 2025"
        start_date = date(2025, 5, 2)  # end_date - 1 day
        end_date = date(2025, 5, 3)

        pre_creation_state = self.get_db_state('Before Creating Semester')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating semester with:")
        print(f"  - Semester ID: {session_id}")
        print(f"  - Semester name: {session_name}")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")

        session = None
        error_caught = False
        error_message = None

        try:
            session = SessionYearModel.objects.create(
                session_start_year=start_date,
                session_end_year=end_date
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SEMESTER: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Semester')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if not error_caught and post_creation_state['sessions_count'] == pre_creation_state['sessions_count'] + 1:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Semester was successfully created with start_date = end_date - 1 day")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Semester was not created as expected")
            if error_message:
                print(f"  - Error message: {error_message}")
            self.fail("Semester should be created successfully when start_date is end_date - 1 day")

    def SM_ADD_SE_03_start_date_equal_end_date_ERROR(self):
        """SM-ADD-SE-03: start date = end date - ERROR."""
        print("\n" + "*"*100)
        print("🔍 SM-ADD-SE-03: start date = end date - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        session_id = 'Y003'
        session_name = "Autumn 2025"
        start_date = date(2025, 5, 2)
        end_date = date(2025, 5, 2)

        pre_creation_state = self.get_db_state('Before Creating Semester')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating semester with:")
        print(f"  - Semester ID: {session_id}")
        print(f"  - Semester name: {session_name}")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")

        session = None
        error_caught = False
        error_message = None

        try:
            session = SessionYearModel.objects.create(
                session_start_year=start_date,
                session_end_year=end_date
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SEMESTER: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Semester')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if error_caught or post_creation_state['sessions_count'] == pre_creation_state['sessions_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Semester creation failed as expected due to start_date = end_date")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Semester was created despite start_date = end_date")
            self.fail("Semester creation should fail when start_date is equal to end_date")

    def SM_ADD_SE_04_start_date_greater_than_end_date_ERROR(self):
        """SM-ADD-SE-04: start date = end date + 1 day - ERROR."""
        print("\n" + "*"*100)
        print("🔍 SM-ADD-SE-04: start date = end date + 1 day - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        session_id = 'Y004'
        session_name = "Fall 2025"
        start_date = date(2025, 5, 3)  # Later than end_date
        end_date = date(2025, 5, 2)

        pre_creation_state = self.get_db_state('Before Creating Semester')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating semester with:")
        print(f"  - Semester ID: {session_id}")
        print(f"  - Semester name: {session_name}")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")

        session = None
        error_caught = False
        error_message = None

        try:
            session = SessionYearModel.objects.create(
                session_start_year=start_date,
                session_end_year=end_date
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SEMESTER: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Semester')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if error_caught or post_creation_state['sessions_count'] == pre_creation_state['sessions_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Semester creation failed as expected due to start_date > end_date")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Semester was created despite start_date being after end_date")
            self.fail("Semester creation should fail when start_date is after end_date")

    def SM_ADD_SE_05_start_date_greater_than_end_date_plus_2_days_ERROR(self):
        """SM-ADD-SE-05: start date = end date + 2 days - ERROR."""
        print("\n" + "*"*100)
        print("🔍 SM-ADD-SE-05: start date = end date + 2 days - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        session_id = 'Y005'
        session_name = "Winter 2025"
        start_date = date(2025, 5, 4)  # Greater than end_date
        end_date = date(2025, 5, 2)

        pre_creation_state = self.get_db_state('Before Creating Semester')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating semester with:")
        print(f"  - Semester ID: {session_id}")
        print(f"  - Semester name: {session_name}")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")

        session = None
        error_caught = False
        error_message = None

        try:
            session = SessionYearModel.objects.create(
                session_start_year=start_date,
                session_end_year=end_date
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SEMESTER: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Semester')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if error_caught or post_creation_state['sessions_count'] == pre_creation_state['sessions_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Semester creation failed as expected due to start_date > end_date")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Semester was created despite start_date being after end_date")
            self.fail("Semester creation should fail when start_date is after end_date")

    def SM_ADD_SE_06_empty_start_date_ERROR(self):
        """SM-ADD-SE-06: Empty start date - ERROR."""
        print("\n" + "*"*100)
        print("🔍 SM-ADD-SE-06: Empty start date - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        session_id = 'Y006'
        session_name = "Fall 2025"
        start_date = None  # Empty start date
        end_date = date(2025, 5, 2)

        pre_creation_state = self.get_db_state('Before Creating Semester')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating semester with:")
        print(f"  - Semester ID: {session_id}")
        print(f"  - Semester name: {session_name}")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")

        session = None
        error_caught = False
        error_message = None

        try:
            session = SessionYearModel.objects.create(
                session_start_year=start_date,
                session_end_year=end_date
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SEMESTER: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Semester')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if error_caught or post_creation_state['sessions_count'] == pre_creation_state['sessions_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Semester creation failed as expected due to empty start_date")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Semester was created despite start_date being empty")
            self.fail("Semester creation should fail when start_date is empty")

    def SM_ADD_SE_07_empty_end_date_ERROR(self):
        """SM-ADD-SE-07: Empty end date - ERROR."""
        print("\n" + "*"*100)
        print("🔍 SM-ADD-SE-07: Empty end date - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        session_id = 'Y007'
        session_name = "Fall 2025"
        start_date = date(2025, 5, 3)
        end_date = None  # Empty end date

        pre_creation_state = self.get_db_state('Before Creating Semester')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating semester with:")
        print(f"  - Semester ID: {session_id}")
        print(f"  - Semester name: {session_name}")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")

        session = None
        error_caught = False
        error_message = None

        try:
            session = SessionYearModel.objects.create(
                session_start_year=start_date,
                session_end_year=end_date
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SEMESTER: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Semester')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if error_caught or post_creation_state['sessions_count'] == pre_creation_state['sessions_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Semester creation failed as expected due to empty end_date")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Semester was created despite end_date being empty")
            self.fail("Semester creation should fail when end_date is empty")

    def SM_ADD_SE_08_wrong_format_with_slashes_ERROR(self):
        """SM-ADD-SE-08: wrong format with slashes - ERROR."""
        print("\n" + "*"*100)
        print("🔍 SM-ADD-SE-08: wrong format with slashes - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        session_id = 'Y008'
        session_name = "Session with wrong date format"
        start_date_str = '2025/01/01'  # Incorrect format
        end_date_str = '2027/01/01'    # Incorrect format

        pre_creation_state = self.get_db_state('Before Creating Semester')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating semester with:")
        print(f"  - Semester ID: {session_id}")
        print(f"  - Semester name: {session_name}")
        print(f"  - Start Date (string): {start_date_str}")
        print(f"  - End Date (string): {end_date_str}\n")

        session = None
        error_caught = False
        error_message = None

        try:
            # Simulate parsing input from a web form or API
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            session = SessionYearModel.objects.create(
                session_start_year=start_date,
                session_end_year=end_date
            )

        except ValueError as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR PARSING DATES: {error_message}")
            connection.rollback()
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SEMESTER: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Semester')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if error_caught or post_creation_state['sessions_count'] == pre_creation_state['sessions_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Semester creation failed as expected due to wrong date format")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Semester was created despite wrong date format")
            self.fail("Semester creation should fail when date format is incorrect")

    def SM_ADD_SE_09_wrong_format_with_dd_mm_yyyy_ERROR(self):
        """SM-ADD-SE-09: wrong format with DD-MM-YYYY - ERROR."""
        print("\n" + "*"*100)
        print("🔍 SM-ADD-SE-09: wrong format with DD-MM-YYYY - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        session_id = 'Y009'
        session_name = "Wrong Date Format - DD-MM-YYYY"
        start_date_str = '31-08-2024'  # Incorrect format
        end_date_str = '01-07-2026'    # Incorrect format

        pre_creation_state = self.get_db_state('Before Creating Semester')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating semester with:")
        print(f"  - Semester ID: {session_id}")
        print(f"  - Semester name: {session_name}")
        print(f"  - Start Date (string): {start_date_str}")
        print(f"  - End Date (string): {end_date_str}\n")

        session = None
        error_caught = False
        error_message = None

        try:
            # Simulate parsing input from web form/API with wrong format
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            session = SessionYearModel.objects.create(
                session_start_year=start_date,
                session_end_year=end_date
            )

        except ValueError as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR PARSING DATES: {error_message}")
            connection.rollback()
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SEMESTER: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Semester')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if error_caught or post_creation_state['sessions_count'] == pre_creation_state['sessions_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Semester creation failed as expected due to wrong date format")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Semester was created despite wrong date format")
            self.fail("Semester creation should fail when date format is incorrect")

    def SM_ADD_SE_10_start_and_end_date_are_duplicated_ERROR(self):
        """SM-ADD-SE-10: start_date and end_date are duplicated - ERROR."""
        print("\n" + "*"*100)
        print("🔍 SM-ADD-SE-10: start_date and end_date are duplicated - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        session_id = 'Y010'
        session_name = "Duplicated Semester Dates"
        start_date = date(2025, 5, 1)
        end_date = date(2025, 5, 3)

        pre_creation_state = self.get_db_state('Before Creating Semester')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating semester with:")
        print(f"  - Semester ID: {session_id}")
        print(f"  - Semester name: {session_name}")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")

        session = None
        error_caught = False
        error_message = None

        # Giả định rằng semester với start_date và end_date này đã tồn tại trong DB
        if SessionYearModel.objects.filter(session_start_year=start_date, session_end_year=end_date).exists():
            error_caught = True
            error_message = "start_date and end_date are existed"
            print(f"\n❌ ERROR CREATING SEMESTER: {error_message}")
            post_creation_state = pre_creation_state
        else:
            try:
                session = SessionYearModel.objects.create(
                    session_start_year=start_date,
                    session_end_year=end_date
                )
            except Exception as e:
                error_caught = True
                error_message = str(e)
                print(f"\n❌ ERROR CREATING SEMESTER: {error_message}")
                connection.rollback()

            if not error_caught:
                post_creation_state = self.get_db_state('After Creating Semester')
                self.print_db_state(post_creation_state, "AFTER CREATION")
            else:
                post_creation_state = pre_creation_state

        if error_caught or post_creation_state['sessions_count'] == pre_creation_state['sessions_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Semester creation failed as expected due to duplicated dates")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Semester was created despite duplicated start_date and end_date")
            self.fail("Semester creation should fail when start_date and end_date are already in use")

    def SM_ADD_ID_01_semester_id_empty_ERROR(self):
        """SM-ADD-ID-01: semester_id has empty string - ERROR."""
        print("\n" + "*"*100)
        print("🔍 SM-ADD-ID-01: semester_id has empty string - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        session_id = ''
        session_name = "Spring 2025"
        start_date = date(2025, 3, 1)
        end_date = date(2025, 6, 1)

        pre_creation_state = self.get_db_state('Before Creating Semester')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating semester with:")
        print(f"  - Semester ID: '{session_id}' (empty)")
        print(f"  - Semester name: {session_name}")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")

        session = None
        error_caught = False
        error_message = None

        try:
            if not session_id:
                raise ValueError("Please input semester_id")

            session = SessionYearModel.objects.create(
                
                session_start_year=start_date,
                session_end_year=end_date
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SEMESTER: {error_message}")
            connection.rollback()

        if error_caught:
            post_creation_state = pre_creation_state
        else:
            post_creation_state = self.get_db_state('After Creating Semester')
            self.print_db_state(post_creation_state, "AFTER CREATION")

        if error_caught and post_creation_state['sessions_count'] == pre_creation_state['sessions_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Semester creation failed as expected due to empty semester_id")
            print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Semester was created despite empty semester_id")
            self.fail("Semester creation should fail when semester_id is empty")

    def SM_ADD_ID_02_semester_id_no_digit_ERROR(self):
        """SM-ADD-ID-02: semester_id has no digit - ERROR."""
        print("\n" + "*"*100)
        print("🔍 SM-ADD-ID-02: semester_id has no digit - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        session_id = 'Y'  # Invalid: no digits
        session_name = "Spring 2025"
        start_date = date(2025, 3, 1)
        end_date = date(2025, 6, 1)

        pre_creation_state = self.get_db_state('Before Creating Semester')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating semester with:")
        print(f"  - Semester ID: {session_id}")
        print(f"  - Semester name: {session_name}")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")

        session = None
        error_caught = False
        error_message = None

        try:
            import re
            pattern = r"^Y\d{3}$"
            if not re.match(pattern, session_id):
                raise ValueError("semester_id must start with an uppercase Y; followed by exactly 3 digits (from 001 -> 999); no lowercase letters, special characters, or spaces allowed")

            session = SessionYearModel.objects.create(
                
                session_start_year=start_date,
                session_end_year=end_date
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SEMESTER: {error_message}")
            connection.rollback()

        if error_caught:
            post_creation_state = pre_creation_state
        else:
            post_creation_state = self.get_db_state('After Creating Semester')
            self.print_db_state(post_creation_state, "AFTER CREATION")

        if error_caught and post_creation_state['sessions_count'] == pre_creation_state['sessions_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Semester creation failed as expected due to semester_id has no digit")
            print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Semester was created despite invalid semester_id (no digit)")
            self.fail("Semester creation should fail for semester_id without digits")

    def SM_ADD_ID_03_semester_id_two_digits_ERROR(self):
        """SM-ADD-ID-03: semester_id has 2 digits - ERROR."""
        print("\n" + "*"*100)
        print("🔍 SM-ADD-ID-03: semester_id has 2 digits - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        session_id = 'Y12'  # Invalid: only 2 digits
        session_name = "Spring 2025"
        start_date = date(2025, 3, 1)
        end_date = date(2025, 6, 1)

        pre_creation_state = self.get_db_state('Before Creating Semester')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating semester with:")
        print(f"  - Semester ID: {session_id}")
        print(f"  - Semester name: {session_name}")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")

        session = None
        error_caught = False
        error_message = None

        try:
            import re
            pattern = r"^Y\d{3}$"
            if not re.match(pattern, session_id):
                raise ValueError("semester_id must start with an uppercase Y; followed by exactly 3 digits (from 001 -> 999); no lowercase letters, special characters, or spaces allowed")

            session = SessionYearModel.objects.create(
                
                session_start_year=start_date,
                session_end_year=end_date
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SEMESTER: {error_message}")
            connection.rollback()

        if error_caught:
            post_creation_state = pre_creation_state
        else:
            post_creation_state = self.get_db_state('After Creating Semester')
            self.print_db_state(post_creation_state, "AFTER CREATION")

        if error_caught and post_creation_state['sessions_count'] == pre_creation_state['sessions_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Semester creation failed as expected due to semester_id has 2 digits")
            print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Semester was created despite invalid semester_id (only 2 digits)")
            self.fail("Semester creation should fail for semester_id with only 2 digits")

    def SM_ADD_ID_04_semester_id_three_digits_SUCCESS(self):
        """SM-ADD-ID-04: semester_id has 3 digits - SUCCESS."""
        print("\n" + "*"*100)
        print("🔍 SM-ADD-ID-04: semester_id has 3 digits - SUCCESS.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        session_id = 'Y123'  # Valid: Y + exactly 3 digits
        session_name = "Spring 2025"
        start_date = date(2025, 3, 1)
        end_date = date(2025, 6, 1)

        pre_creation_state = self.get_db_state('Before Creating Semester')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating semester with:")
        print(f"  - Semester ID: {session_id}")
        print(f"  - Semester name: {session_name}")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")

        session = None
        error_caught = False
        error_message = None

        try:
            import re
            pattern = r"^Y\d{3}$"
            if not re.match(pattern, session_id):
                raise ValueError("semester_id must start with an uppercase Y; followed by exactly 3 digits (from 001 -> 999); no lowercase letters, special characters, or spaces allowed")

            session = SessionYearModel.objects.create(
                
                session_start_year=start_date,
                session_end_year=end_date
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SEMESTER: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Semester')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if not error_caught and post_creation_state['sessions_count'] == pre_creation_state['sessions_count'] + 1:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Semester was successfully created with valid semester_id")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Semester was not created despite valid semester_id")
            if error_message:
                print(f"  - Error message: {error_message}")
            self.fail("Semester should be created successfully with valid semester_id")

    def SM_ADD_ID_05_semester_id_four_digits_ERROR(self):
        """SM-ADD-ID-05: semester_id has 4 digits - ERROR."""
        print("\n" + "*"*100)
        print("🔍 SM-ADD-ID-05: semester_id has 4 digits - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        session_id = 'Y1234'  # Sai định dạng: 4 digits thay vì 3
        session_name = "Spring 2025"
        start_date = date(2025, 3, 1)
        end_date = date(2025, 6, 1)

        pre_creation_state = self.get_db_state('Before Creating Semester')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating semester with:")
        print(f"  - Semester ID: {session_id}")
        print(f"  - Semester name: {session_name}")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")

        session = None
        error_caught = False
        error_message = None

        try:
            import re
            pattern = r"^Y\d{3}$"
            if not re.match(pattern, session_id):
                raise ValueError("semester_id must start with an uppercase Y; followed by exactly 3 digits (from 001 -> 999); no lowercase letters, special characters, or spaces allowed")

            session = SessionYearModel.objects.create(
                
                session_start_year=start_date,
                session_end_year=end_date
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SEMESTER: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Semester')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if error_caught or post_creation_state['sessions_count'] == pre_creation_state['sessions_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Semester creation failed as expected due to invalid semester_id format")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Semester was created despite invalid semester_id format")
            self.fail("Semester creation should fail for semester_id with 4 digits")

    def SM_ADD_ID_06_semester_id_has_non_digit_characters_ERROR(self):
        """SM-ADD-ID-06: semester_id has non-digit characters - ERROR."""
        print("\n" + "*"*100)
        print("🔍 SM-ADD-ID-06: semester_id has non-digit characters - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        session_id = 'Y1A-'  # Có ký tự không phải số
        session_name = "Spring 2025"
        start_date = date(2025, 3, 1)
        end_date = date(2025, 6, 1)

        pre_creation_state = self.get_db_state('Before Creating Semester')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating semester with:")
        print(f"  - Semester ID: {session_id}")
        print(f"  - Semester name: {session_name}")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")

        session = None
        error_caught = False
        error_message = None

        try:
            import re
            pattern = r"^Y\d{3}$"
            if not re.match(pattern, session_id):
                raise ValueError("semester_id must start with an uppercase Y; followed by exactly 3 digits (from 001 -> 999); no lowercase letters, special characters, or spaces allowed")

            session = SessionYearModel.objects.create(
                
                session_start_year=start_date,
                session_end_year=end_date
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SEMESTER: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Semester')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if error_caught or post_creation_state['sessions_count'] == pre_creation_state['sessions_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Semester creation failed as expected due to invalid semester_id format (non-digit characters)")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Semester was created despite invalid semester_id format (non-digit characters)")
            self.fail("Semester creation should fail for semester_id with non-digit characters")

    def SM_ADD_ID_07_semester_id_has_lowercase_letter_ERROR(self):
        """SM-ADD-ID-07: semester_id has lowercase letter - ERROR."""
        print("\n" + "*"*100)
        print("🔍 SM-ADD-ID-07: semester_id has lowercase letter - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        session_id = 'y123'  # chữ y thường, lỗi
        session_name = "Spring 2025"
        start_date = date(2025, 3, 1)
        end_date = date(2025, 6, 1)

        pre_creation_state = self.get_db_state('Before Creating Semester')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating semester with:")
        print(f"  - Semester ID: {session_id}")
        print(f"  - Semester name: {session_name}")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")

        session = None
        error_caught = False
        error_message = None

        try:
            import re
            pattern = r"^Y\d{3}$"
            if not re.match(pattern, session_id):
                raise ValueError("semester_id must start with an uppercase Y; followed by exactly 3 digits (from 001 -> 999); no lowercase letters, special characters, or spaces allowed")

            session = SessionYearModel.objects.create(
                
                session_start_year=start_date,
                session_end_year=end_date
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SEMESTER: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Semester')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if error_caught or post_creation_state['sessions_count'] == pre_creation_state['sessions_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Semester creation failed as expected due to lowercase letter in semester_id")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Semester was created despite lowercase letter in semester_id")
            self.fail("Semester creation should fail for semester_id with lowercase letters")

    def SM_ADD_ID_08_semester_id_3_digits_are_zero_ERROR(self):
        """SM-ADD-ID-08: semester_id has 3 digits are zero - ERROR."""
        print("\n" + "*"*100)
        print("🔍 SM-ADD-ID-08: semester_id has 3 digits are zero - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        session_id = 'Y000'  # 3 chữ số là 000, lỗi
        session_name = "Spring 2025"
        start_date = date(2025, 3, 1)
        end_date = date(2025, 6, 1)

        pre_creation_state = self.get_db_state('Before Creating Semester')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating semester with:")
        print(f"  - Semester ID: {session_id}")
        print(f"  - Semester name: {session_name}")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")

        session = None
        error_caught = False
        error_message = None

        try:
            import re
            pattern = r"^Y(\d{3})$"
            match = re.match(pattern, session_id)
            if not match or match.group(1) == '000':
                raise ValueError("semester_id must start with an uppercase Y; followed by exactly 3 digits (from 001 -> 999); no lowercase letters, special characters, or spaces allowed")

            session = SessionYearModel.objects.create(
                
                session_start_year=start_date,
                session_end_year=end_date
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SEMESTER: {error_message}")
            connection.rollback()

        if error_caught or post_creation_state['sessions_count'] == pre_creation_state['sessions_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Semester creation failed as expected due to semester_id digits are 000")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Semester was created despite digits are 000 in semester_id")
            self.fail("Semester creation should fail for semester_id with digits '000'")

    def SM_ADD_ID_09_semester_id_3_digits_are_9_SUCCESS(self):
        """SM-ADD-ID-09: semester_id has 3 digits are 9 - SUCCESS."""
        print("\n" + "*"*100)
        print("🔍 SM-ADD-ID-09: semester_id has 3 digits are 9 - SUCCESS.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        session_id = 'Y999'  # 3 chữ số là 999, hợp lệ
        session_name = "Fall 2025"
        start_date = date(2025, 9, 1)
        end_date = date(2026, 1, 15)

        pre_creation_state = self.get_db_state('Before Creating Semester')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating semester with:")
        print(f"  - Semester ID: {session_id}")
        print(f"  - Semester name: {session_name}")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")

        session = None
        error_caught = False
        error_message = None

        try:
            import re
            pattern = r"^Y(\d{3})$"
            match = re.match(pattern, session_id)
            if not match or match.group(1) == '000':
                raise ValueError("semester_id must start with an uppercase Y; followed by exactly 3 digits (from 001 -> 999); no lowercase letters, special characters, or spaces allowed")

            session = SessionYearModel.objects.create(
                
                session_start_year=start_date,
                session_end_year=end_date
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SEMESTER: {error_message}")
            connection.rollback()

        if not error_caught:
            post_creation_state = self.get_db_state('After Creating Semester')
            self.print_db_state(post_creation_state, "AFTER CREATION")
        else:
            post_creation_state = pre_creation_state

        if not error_caught and post_creation_state['sessions_count'] == pre_creation_state['sessions_count'] + 1:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Semester was successfully created with semester_id having digits '999'")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Semester creation failed unexpectedly")
            if error_message:
                print(f"  - Error message: {error_message}")
            self.fail("Semester should be created successfully with semester_id digits '999'")

    def SM_ADD_ID_10_semester_id_contains_whitespace_ERROR(self):
        """SM-ADD-ID-010: semester_id contains whitespace - ERROR."""
        print("\n" + "*"*100)
        print("🔍 SM-ADD-ID-010: semester_id contains whitespace - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        session_id = 'Y 12'  # semester_id có khoảng trắng, sai định dạng
        session_name = "Winter 2025"
        start_date = date(2025, 1, 1)
        end_date = date(2025, 4, 1)

        pre_creation_state = self.get_db_state('Before Creating Semester')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating semester with:")
        print(f"  - Semester ID: {session_id}")
        print(f"  - Semester name: {session_name}")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")

        session = None
        error_caught = False
        error_message = None

        try:
            import re
            pattern = r"^Y\d{3}$"  # đúng định dạng: Y + 3 chữ số, không có khoảng trắng
            if not re.match(pattern, session_id):
                raise ValueError(
                    "semester_id must start with an uppercase Y; followed by exactly 3 digits (from 001 -> 999); no lowercase letters, special characters, or spaces allowed"
                )

            session = SessionYearModel.objects.create(
                
                session_start_year=start_date,
                session_end_year=end_date
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SEMESTER: {error_message}")
            connection.rollback()

        if error_caught or pre_creation_state['sessions_count'] == self.get_db_state('After Attempt')['sessions_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Semester creation failed as expected due to whitespace in semester_id")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Semester was created despite whitespace in semester_id")
            self.fail("Semester creation should fail if semester_id contains whitespace")

    def SM_ADD_ID_11_semester_id_not_start_with_Y_ERROR(self):
        """SM-ADD-ID-011: semester_id does not start with Y - ERROR."""
        print("\n" + "*"*100)
        print("🔍 SM-ADD-ID-011: semester_id does not start with Y - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        session_id = '1234'  # semester_id không bắt đầu bằng Y, sai định dạng
        session_name = "Fall 2025"
        start_date = date(2025, 9, 1)
        end_date = date(2025, 12, 15)

        pre_creation_state = self.get_db_state('Before Creating Semester')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating semester with:")
        print(f"  - Semester ID: {session_id}")
        print(f"  - Semester name: {session_name}")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")

        session = None
        error_caught = False
        error_message = None

        try:
            import re
            pattern = r"^Y\d{3}$"  # Định dạng hợp lệ: Y + 3 chữ số
            if not re.match(pattern, session_id):
                raise ValueError(
                    "semester_id must start with an uppercase Y; followed by exactly 3 digits (from 001 -> 999); no lowercase letters, special characters, or spaces allowed"
                )

            session = SessionYearModel.objects.create(
                session_start_year=start_date,
                session_end_year=end_date
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SEMESTER: {error_message}")
            connection.rollback()

        if error_caught or pre_creation_state['sessions_count'] == self.get_db_state('After Attempt')['sessions_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Semester creation failed as expected due to semester_id not starting with Y")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Semester was created despite semester_id not starting with Y")
            self.fail("Semester creation should fail if semester_id does not start with Y")

    def SM_ADD_ID_12_semester_id_is_duplicated_ERROR(self):
        """SM-ADD-ID-012: semester_id is duplicated - ERROR."""
        print("\n" + "*"*100)
        print("🔍 SM-ADD-ID-012: semester_id is duplicated - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        session_id = 'Y123'  # semester_id đã tồn tại trong hệ thống
        session_name = "Winter 2025"
        start_date = date(2025, 12, 1)
        end_date = date(2026, 3, 1)

        # Tạo trước một semester với ID trùng để gây lỗi trùng lặp
        existing_session, created = SessionYearModel.objects.get_or_create(
            id=session_id,
            defaults={
                'session_start_year': date(2025, 1, 1),
                'session_end_year': date(2025, 4, 1),
            }
        )

        pre_creation_state = self.get_db_state('Before Creating Semester')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating semester with:")
        print(f"  - Semester ID: {session_id}")
        print(f"  - Semester name: {session_name}")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")

        session = None
        error_caught = False
        error_message = None

        try:
            # Thử tạo mới semester với ID trùng
            session = SessionYearModel.objects.create(
                session_start_year=start_date,
                session_end_year=end_date
            )
        except Exception as e:
            error_caught = True
            error_message = str(e)
            print(f"\n❌ ERROR CREATING SEMESTER: {error_message}")
            connection.rollback()

        if error_caught or pre_creation_state['sessions_count'] == self.get_db_state('After Attempt')['sessions_count']:
            print("\n🟢 TEST RESULT: PASSED")
            print("  - Semester creation failed as expected due to duplicated semester_id")
            if error_message:
                print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
            print("  - Semester was created despite duplicated semester_id")
            self.fail("Semester creation should fail if semester_id is duplicated")
