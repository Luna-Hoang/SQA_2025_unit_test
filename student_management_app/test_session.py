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

    def test_SM_ADD_SE_01_start_date_is_end_date_minus_2_day_SUCCESS(self):
        """SM-ADD-SE-01: start date = end date -2 day - SUCCESS."""
        with transaction.atomic():
            initial_state = self.get_db_state('Initial State')
            self.print_db_state(initial_state, "INITIAL STATE")

            start_date = date(2025, 3, 30)
            end_date = date(2025, 4, 1)

            pre_creation_state = self.get_db_state('Before Creating Semester')
            self.print_db_state(pre_creation_state, "BEFORE CREATION")

            error_caught = False
            try:
                session = SessionYearModel.objects.create(
                    session_start_year=start_date,
                    session_end_year=end_date
                )
            except Exception as e:
                error_caught = True
                error_message = str(e)
                print(f"\n❌ ERROR CREATING SEMESTER: {error_message}")
                # No need to manually rollback inside transaction.atomic context

            post_creation_state = self.get_db_state('After Creating Semester') if not error_caught else pre_creation_state
            self.print_db_state(post_creation_state, "AFTER CREATION")

            self.assertFalse(error_caught, "Không nên có lỗi khi start_date = end_date - 2 ngày")
            self.assertEqual(post_creation_state['sessions_count'], pre_creation_state['sessions_count'] + 1,
                             "Số lượng semester phải tăng lên 1")

    def test_SM_ADD_SE_02_start_date_is_end_date_minus_1_day_SUCCESS(self):
        """SM-ADD-SE-02: start date = end date -1 day - SUCCESS."""
        with transaction.atomic():
            initial_state = self.get_db_state('Initial State')
            self.print_db_state(initial_state, "INITIAL STATE")

            start_date = date(2025, 5, 2)
            end_date = date(2025, 5, 3)

            pre_creation_state = self.get_db_state('Before Creating Semester')
            self.print_db_state(pre_creation_state, "BEFORE CREATION")

            error_caught = False
            try:
                session = SessionYearModel.objects.create(
                    session_start_year=start_date,
                    session_end_year=end_date
                )
            except Exception as e:
                error_caught = True
                error_message = str(e)
                print(f"\n❌ ERROR CREATING SEMESTER: {error_message}")

            post_creation_state = self.get_db_state('After Creating Semester') if not error_caught else pre_creation_state
            self.print_db_state(post_creation_state, "AFTER CREATION")

            self.assertFalse(error_caught, "Không nên có lỗi khi start_date = end_date - 1 ngày")
            self.assertEqual(post_creation_state['sessions_count'], pre_creation_state['sessions_count'] + 1,
                             "Số lượng semester phải tăng lên 1")

    def test_SM_ADD_SE_03_start_date_equal_end_date_ERROR(self):
        """SM-ADD-SE-03: start date = end date - ERROR."""
        with transaction.atomic():
            initial_state = self.get_db_state('Initial State')
            self.print_db_state(initial_state, "INITIAL STATE")

            start_date = date(2025, 5, 2)
            end_date = date(2025, 5, 2)

            pre_creation_state = self.get_db_state('Before Creating Semester')
            self.print_db_state(pre_creation_state, "BEFORE CREATION")

            error_caught = False
            try:
                session = SessionYearModel.objects.create(
                    session_start_year=start_date,
                    session_end_year=end_date
                )
            except Exception as e:
                error_caught = True
                error_message = str(e)
                print(f"\n❌ ERROR CREATING SEMESTER: {error_message}")

            post_creation_state = self.get_db_state('After Creating Semester') if not error_caught else pre_creation_state
            self.print_db_state(post_creation_state, "AFTER CREATION")

            self.assertTrue(error_caught or post_creation_state['sessions_count'] == pre_creation_state['sessions_count'],
                            "Phải có lỗi hoặc số lượng semester không thay đổi khi start_date = end_date")

    def test_SM_ADD_SE_04_start_date_greater_than_end_date_ERROR(self):
        """SM-ADD-SE-04: start date = end date + 1 day - ERROR."""
        with transaction.atomic():
            initial_state = self.get_db_state('Initial State')
            self.print_db_state(initial_state, "INITIAL STATE")

            start_date = date(2025, 5, 3)
            end_date = date(2025, 5, 2)

            pre_creation_state = self.get_db_state('Before Creating Semester')
            self.print_db_state(pre_creation_state, "BEFORE CREATION")

            error_caught = False
            try:
                session = SessionYearModel.objects.create(
                    session_start_year=start_date,
                    session_end_year=end_date
                )
            except Exception as e:
                error_caught = True
                error_message = str(e)
                print(f"\n❌ ERROR CREATING SEMESTER: {error_message}")

            post_creation_state = self.get_db_state('After Creating Semester') if not error_caught else pre_creation_state
            self.print_db_state(post_creation_state, "AFTER CREATION")

            self.assertTrue(error_caught or post_creation_state['sessions_count'] == pre_creation_state['sessions_count'],
                            "Phải có lỗi hoặc số lượng semester không thay đổi khi start_date > end_date")

    def test_SM_ADD_SE_05_start_date_greater_than_end_date_plus_2_days_ERROR(self):
        """SM-ADD-SE-05: start date = end date + 2 days - ERROR."""
        with transaction.atomic():
            initial_state = self.get_db_state('Initial State')
            self.print_db_state(initial_state, "INITIAL STATE")

            start_date = date(2025, 5, 4)
            end_date = date(2025, 5, 2)

            pre_creation_state = self.get_db_state('Before Creating Semester')
            self.print_db_state(pre_creation_state, "BEFORE CREATION")

            error_caught = False
            try:
                session = SessionYearModel.objects.create(
                    session_start_year=start_date,
                    session_end_year=end_date
                )
            except Exception as e:
                error_caught = True
                error_message = str(e)
                print(f"\n❌ ERROR CREATING SEMESTER: {error_message}")

            post_creation_state = self.get_db_state('After Creating Semester') if not error_caught else pre_creation_state
            self.print_db_state(post_creation_state, "AFTER CREATION")

            self.assertTrue(error_caught or post_creation_state['sessions_count'] == pre_creation_state['sessions_count'],
                            "Phải có lỗi hoặc số lượng semester không thay đổi khi start_date > end_date + 2 ngày")

    def test_SM_ADD_SE_06_empty_start_date_ERROR(self):
        """SM-ADD-SE-06: Empty start date - ERROR."""
        with transaction.atomic():
            initial_state = self.get_db_state('Initial State')
            self.print_db_state(initial_state, "INITIAL STATE")

            start_date = None
            end_date = date(2025, 5, 2)

            pre_creation_state = self.get_db_state('Before Creating Semester')
            self.print_db_state(pre_creation_state, "BEFORE CREATION")

            error_caught = False
            try:
                session = SessionYearModel.objects.create(
                    session_start_year=start_date,
                    session_end_year=end_date
                )
            except Exception as e:
                error_caught = True
                error_message = str(e)
                print(f"\n❌ ERROR CREATING SEMESTER: {error_message}")

            post_creation_state = self.get_db_state('After Creating Semester') if not error_caught else pre_creation_state
            self.print_db_state(post_creation_state, "AFTER CREATION")

            self.assertTrue(error_caught or post_creation_state['sessions_count'] == pre_creation_state['sessions_count'],
                            "Phải có lỗi hoặc số lượng semester không thay đổi khi start_date rỗng (None)")

    def SM_ADD_SE_07_empty_end_date_ERROR(self):
        """SM-ADD-SE-07: Empty end date - ERROR."""
        print("\n" + "*"*100)
        print("🔍 SM-ADD-SE-07: Empty end date - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        start_date = date(2025, 5, 3)
        end_date = None  # Empty end date

        pre_creation_state = self.get_db_state('Before Creating Semester')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating semester with:")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")

        error_caught = False
        error_message = None

        with transaction.atomic():
            try:
                SessionYearModel.objects.create(
                    session_start_year=start_date,
                    session_end_year=end_date
                )
            except Exception as e:
                error_caught = True
                error_message = str(e)
                print(f"\n❌ ERROR CREATING SEMESTER: {error_message}")
                # Rollback transaction
                transaction.set_rollback(True)

        post_creation_state = self.get_db_state('After Creating Semester')
        self.print_db_state(post_creation_state, "AFTER CREATION")

        self.assertTrue(
            error_caught or post_creation_state['sessions_count'] == pre_creation_state['sessions_count'],
            "Semester creation should fail when end_date is empty"
        )
        if error_caught:
            print("\n🟢 TEST RESULT: PASSED")
            print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")
        
    def SM_ADD_SE_08_wrong_format_with_slashes_ERROR(self):
        """SM-ADD-SE-08: wrong format with slashes - ERROR."""
        print("\n" + "*"*100)
        print("🔍 SM-ADD-SE-08: wrong format with slashes - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        start_date_str = '2025/01/01'  # Incorrect format
        end_date_str = '2027/01/01'    # Incorrect format

        pre_creation_state = self.get_db_state('Before Creating Semester')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating semester with:")
        print(f"  - Start Date (string): {start_date_str}")
        print(f"  - End Date (string): {end_date_str}\n")

        error_caught = False
        error_message = None

        with transaction.atomic():
            try:
                # Will raise ValueError on wrong format
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

                SessionYearModel.objects.create(
                    session_start_year=start_date,
                    session_end_year=end_date
                )
            except ValueError as e:
                error_caught = True
                error_message = str(e)
                print(f"\n❌ ERROR PARSING DATES: {error_message}")
                transaction.set_rollback(True)
            except Exception as e:
                error_caught = True
                error_message = str(e)
                print(f"\n❌ ERROR CREATING SEMESTER: {error_message}")
                transaction.set_rollback(True)

        post_creation_state = self.get_db_state('After Creating Semester')
        self.print_db_state(post_creation_state, "AFTER CREATION")

        self.assertTrue(
            error_caught or post_creation_state['sessions_count'] == pre_creation_state['sessions_count'],
            "Semester creation should fail when date format is incorrect"
        )
        if error_caught:
            print("\n🟢 TEST RESULT: PASSED")
            print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")

    def SM_ADD_SE_09_wrong_format_with_dd_mm_yyyy_ERROR(self):
        """SM-ADD-SE-09: wrong format with DD-MM-YYYY - ERROR."""
        print("\n" + "*"*100)
        print("🔍 SM-ADD-SE-09: wrong format with DD-MM-YYYY - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        start_date_str = '31-08-2024'  # Incorrect format
        end_date_str = '01-07-2026'    # Incorrect format

        pre_creation_state = self.get_db_state('Before Creating Semester')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating semester with:")
        print(f"  - Start Date (string): {start_date_str}")
        print(f"  - End Date (string): {end_date_str}\n")

        error_caught = False
        error_message = None

        with transaction.atomic():
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

                SessionYearModel.objects.create(
                    session_start_year=start_date,
                    session_end_year=end_date
                )
            except ValueError as e:
                error_caught = True
                error_message = str(e)
                print(f"\n❌ ERROR PARSING DATES: {error_message}")
                transaction.set_rollback(True)
            except Exception as e:
                error_caught = True
                error_message = str(e)
                print(f"\n❌ ERROR CREATING SEMESTER: {error_message}")
                transaction.set_rollback(True)

        post_creation_state = self.get_db_state('After Creating Semester')
        self.print_db_state(post_creation_state, "AFTER CREATION")

        self.assertTrue(
            error_caught or post_creation_state['sessions_count'] == pre_creation_state['sessions_count'],
            "Semester creation should fail when date format is incorrect"
        )
        if error_caught:
            print("\n🟢 TEST RESULT: PASSED")
            print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")

    def SM_ADD_SE_10_start_and_end_date_are_duplicated_ERROR(self):
        """SM-ADD-SE-10: start_date and end_date are duplicated - ERROR."""
        print("\n" + "*"*100)
        print("🔍 SM-ADD-SE-10: start_date and end_date are duplicated - ERROR.")
        print("*"*100 + "\n")

        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")

        start_date = date(2025, 5, 1)
        end_date = date(2025, 5, 3)

        pre_creation_state = self.get_db_state('Before Creating Semester')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")

        print("\n📌 Creating semester with:")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")

        error_caught = False
        error_message = None

        # Nếu đã tồn tại thì không tạo mới
        if SessionYearModel.objects.filter(session_start_year=start_date, session_end_year=end_date).exists():
            error_caught = True
            error_message = "start_date and end_date are existed"
            print(f"\n❌ ERROR CREATING SEMESTER: {error_message}")
            post_creation_state = pre_creation_state
        else:
            with transaction.atomic():
                try:
                    SessionYearModel.objects.create(
                        session_start_year=start_date,
                        session_end_year=end_date
                    )
                except Exception as e:
                    error_caught = True
                    error_message = str(e)
                    print(f"\n❌ ERROR CREATING SEMESTER: {error_message}")
                    transaction.set_rollback(True)

                post_creation_state = self.get_db_state('After Creating Semester')
                self.print_db_state(post_creation_state, "AFTER CREATION")

        self.assertTrue(
            error_caught or post_creation_state['sessions_count'] == pre_creation_state['sessions_count'],
            "Semester creation should fail when start_date and end_date are already in use"
        )
        if error_caught:
            print("\n🟢 TEST RESULT: PASSED")
            print(f"  - Error message: {error_message}")
        else:
            print("\n🔴 TEST RESULT: FAILED")