from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta
import os
import json
from .models import SessionYearModel
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError

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

    def test_E1_session_creation_lower_boundary_success(self):
        """E1: start date is exactly at lower boundary; follow other criteria -> expect success."""
        print("\n" + "*"*100)
        print("\n🔍 TEST E1: SUCCESSFUL SESSION CREATION WITH START DATE AT LOWER BOUNDARY")
        print("*"*100 + "\n")
        
        # Get initial database state
        initial_state = self.get_db_state('Initial State')
        self.print_db_state(initial_state, "INITIAL STATE")
        
        # Thiết lập đầu vào theo test case E1
        from datetime import date
        start_date = date(2025, 5, 1)   # Giá trị biên dưới
        end_date   = date(2027, 3, 1)
        
        # Get database state before creation
        pre_creation_state = self.get_db_state('Before Session Creation')
        self.print_db_state(pre_creation_state, "BEFORE CREATION")
        
        print("\n📌 Creating session with:")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")
        
        # Thực hiện tạo academic year (session)
        try:
            session = SessionYearModel.objects.create(
                session_start_year=start_date,
                session_end_year=end_date
            )
        except Exception as e:
            self.fail(f"❌ TEST RESULT: FAILURE — Unexpected error during session creation: {e}")
        
        # Get database state after creation
        post_creation_state = self.get_db_state('After Session Creation')
        self.print_db_state(post_creation_state, "AFTER CREATION")
        
        # Kiểm tra xem academic year đã được tạo đúng hay chưa
        self.assertEqual(SessionYearModel.objects.count(), pre_creation_state['students_count'] + 1 if 'students_count' in pre_creation_state else 1)
        self.assertEqual(session.session_start_year, start_date)
        self.assertEqual(session.session_end_year, end_date)
        
        print("\n✅ TEST RESULT: SUCCESS")
        print(f"  - Session created with ID: {session.id}")
        print(f"  - Start Date: {session.session_start_year}")
        print(f"  - End Date: {session.session_end_year}\n")

    # E2: start_date = lower boundary -1 day → expect error
    def test_E2_session_creation_start_date_below_lower_boundary(self):
        """E2: start date = lower boundary -1 day; follow other criteria -> expect error."""
        print("\n" + "*"*100)
        print("\n🔍 TEST E2: SESSION CREATION WITH START DATE BELOW LOWER BOUNDARY")
        print("*"*100 + "\n")
        
        initial_state = self.get_db_state("Initial State")
        self.print_db_state(initial_state, "INITIAL STATE")
        from datetime import date
        start_date = date(2025, 4, 30)  # one day before lower boundary
        end_date = date(2027, 3, 1)
        
        pre_creation_state = self.get_db_state("Before Session Creation")
        self.print_db_state(pre_creation_state, "BEFORE CREATION")
        
        print("\n📌 Attempting to create session with:")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")
        
        try:
            SessionYearModel.objects.create(
                session_start_year=start_date,
                session_end_year=end_date
            )
            self.fail("❌ TEST RESULT: FAILURE — Session should not be created with start date below lower boundary.\n")
        except Exception as e:
            print("✅ TEST RESULT: SUCCESS — Creation failed as expected.")
            print(f"  - Error: {str(e)}\n")
        
        post_creation_state = self.get_db_state("After Session Creation")
        self.print_db_state(post_creation_state, "AFTER CREATION")
    
    # E3: start_date = lower boundary +1 day → expect success
    def test_E3_session_creation_start_date_above_lower_boundary_success(self):
        """E3: start date = lower boundary +1 day; follow other criteria -> expect success."""
        print("\n" + "*"*100)
        print("\n🔍 TEST E3: SESSION CREATION WITH START DATE ABOVE LOWER BOUNDARY")
        print("*"*100 + "\n")
        
        initial_state = self.get_db_state("Initial State")
        self.print_db_state(initial_state, "INITIAL STATE")
        from datetime import date
        start_date = date(2025, 5, 2)
        end_date = date(2027, 3, 1)
        
        pre_creation_state = self.get_db_state("Before Session Creation")
        self.print_db_state(pre_creation_state, "BEFORE CREATION")
        
        print("\n📌 Creating session with:")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")
        
        try:
            session = SessionYearModel.objects.create(
                session_start_year=start_date,
                session_end_year=end_date
            )
        except Exception as e:
            self.fail(f"❌ TEST RESULT: FAILURE — Unexpected error: {e}")
        
        post_creation_state = self.get_db_state("After Session Creation")
        self.print_db_state(post_creation_state, "AFTER CREATION")
        
        self.assertEqual(session.session_start_year, start_date)
        self.assertEqual(session.session_end_year, end_date)
        print("\n✅ TEST RESULT: SUCCESS")
        print(f"  - Session created with ID: {session.id}")
        print(f"  - Start Date: {session.session_start_year}")
        print(f"  - End Date: {session.session_end_year}\n")
    
    # E4: end_date exactly at upper boundary → expect success
    def test_E4_session_creation_end_date_at_upper_boundary_success(self):
        """E4: end date is exactly at upper boundary; follow other criteria -> expect success."""
        print("\n" + "*"*100)
        print("\n🔍 TEST E4: SESSION CREATION WITH END DATE AT UPPER BOUNDARY")
        print("*"*100 + "\n")
        
        initial_state = self.get_db_state("Initial State")
        self.print_db_state(initial_state, "INITIAL STATE")
        from datetime import date
        start_date = date(2028, 12, 31)
        end_date = date(2030, 12, 31)  # upper boundary
       
        pre_creation_state = self.get_db_state("Before Session Creation")
        self.print_db_state(pre_creation_state, "BEFORE CREATION")
       
        print("\n📌 Creating session with:")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")
       
        try:
            session = SessionYearModel.objects.create(
                session_start_year=start_date,
                session_end_year=end_date
            )
        except Exception as e:
            self.fail(f"❌ TEST RESULT: FAILURE — Unexpected error: {e}")
       
        post_creation_state = self.get_db_state("After Session Creation")
        self.print_db_state(post_creation_state, "AFTER CREATION")
       
        self.assertEqual(session.session_start_year, start_date)
        self.assertEqual(session.session_end_year, end_date)
        print("\n✅ TEST RESULT: SUCCESS")
        print(f"  - Session created with ID: {session.id}")
        print(f"  - Start Date: {session.session_start_year}")
        print(f"  - End Date: {session.session_end_year}\n")
    
    # E5: end_date = upper boundary -1 day → expect success
    def test_E5_session_creation_end_date_just_below_upper_boundary_success(self):
        """E5: end date = upper boundary -1 day; follow other criteria -> expect success."""
        print("\n" + "*"*100)
        print("\n🔍 TEST E5: SESSION CREATION WITH END DATE JUST BELOW UPPER BOUNDARY")
        print("*"*100 + "\n")
        
        initial_state = self.get_db_state("Initial State")
        self.print_db_state(initial_state, "INITIAL STATE")
        from datetime import date
        start_date = date(2029, 5, 31)
        end_date = date(2030, 12, 30)  # one day less than upper boundary
        
        pre_creation_state = self.get_db_state("Before Session Creation")
        self.print_db_state(pre_creation_state, "BEFORE CREATION")
        
        print("\n📌 Creating session with:")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")
        
        try:
            session = SessionYearModel.objects.create(
                session_start_year=start_date,
                session_end_year=end_date
            )
        except Exception as e:
            self.fail(f"❌ TEST RESULT: FAILURE — Unexpected error: {e}")
        
        post_creation_state = self.get_db_state("After Session Creation")
        self.print_db_state(post_creation_state, "AFTER CREATION")
        
        self.assertEqual(session.session_start_year, start_date)
        self.assertEqual(session.session_end_year, end_date)
        print("\n✅ TEST RESULT: SUCCESS")
        print(f"  - Session created with ID: {session.id}")
        print(f"  - Start Date: {session.session_start_year}")
        print(f"  - End Date: {session.session_end_year}\n")
    
    # E6: end_date = upper boundary +1 day → expect error
    def test_E6_session_creation_end_date_above_upper_boundary_error(self):
        """E6: end date = upper boundary +1 day; follow other criteria -> expect error."""
        print("\n" + "*"*100)
        print("\n🔍 TEST E6: SESSION CREATION WITH END DATE ABOVE UPPER BOUNDARY")
        print("*"*100 + "\n")
        
        initial_state = self.get_db_state("Initial State")
        self.print_db_state(initial_state, "INITIAL STATE")
        from datetime import date
        start_date = date(2029, 5, 31)
        end_date = date(2031, 1, 1)  # one day beyond upper boundary
        
        pre_creation_state = self.get_db_state("Before Session Creation")
        self.print_db_state(pre_creation_state, "BEFORE CREATION")
        
        print("\n📌 Attempting to create session with:")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")
        
        try:
            SessionYearModel.objects.create(
                session_start_year=start_date,
                session_end_year=end_date
            )
            self.fail("❌ TEST RESULT: FAILURE — Session should not be created with end date above upper boundary.\n")
        except Exception as e:
            print("✅ TEST RESULT: SUCCESS — Creation failed as expected.")
            print(f"  - Error: {str(e)}\n")
        
        post_creation_state = self.get_db_state("After Session Creation")
        self.print_db_state(post_creation_state, "AFTER CREATION")
    
    # E7: end_date = start_date + 2 years → expect success
    def test_E7_session_creation_end_date_equals_start_plus_2_years_success(self):
        """E7: end date = start date + 2 years; follow other criteria -> expect success."""
        print("\n" + "*"*100)
        print("\n🔍 TEST E7: SESSION CREATION WITH END DATE = START DATE + 2 YEARS")
        print("*"*100 + "\n")
        
        initial_state = self.get_db_state("Initial State")
        self.print_db_state(initial_state, "INITIAL STATE")
        from datetime import date
        start_date = date(2025, 5, 1)
        end_date = date(2027, 5, 1)  # exactly 2 years later
        
        pre_creation_state = self.get_db_state("Before Session Creation")
        self.print_db_state(pre_creation_state, "BEFORE CREATION")
        
        print("\n📌 Creating session with:")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")
        
        try:
            session = SessionYearModel.objects.create(
                session_start_year=start_date,
                session_end_year=end_date
            )
        except Exception as e:
            self.fail(f"❌ TEST RESULT: FAILURE — Unexpected error: {e}")
        
        post_creation_state = self.get_db_state("After Session Creation")
        self.print_db_state(post_creation_state, "AFTER CREATION")
        
        self.assertEqual(session.session_start_year, start_date)
        self.assertEqual(session.session_end_year, end_date)
        print("\n✅ TEST RESULT: SUCCESS")
        print(f"  - Session created with ID: {session.id}")
        print(f"  - Start Date: {session.session_start_year}")
        print(f"  - End Date: {session.session_end_year}\n")
    
    # E8: end_date = start_date + 2 years +1 day → expect error
    def test_E8_session_creation_end_date_exceeds_2_years_error(self):
        """E8: end date = start date + 2 years +1 day; follow other criteria -> expect error."""
        print("\n" + "*"*100)
        print("\n🔍 TEST E8: SESSION CREATION WITH END DATE = START DATE + 2 YEARS + 1 DAY")
        print("*"*100 + "\n")
        
        initial_state = self.get_db_state("Initial State")
        self.print_db_state(initial_state, "INITIAL STATE")
        from datetime import date
        start_date = date(2025, 5, 1)
        end_date = date(2027, 5, 2)  # 2 years + 1 day
        
        pre_creation_state = self.get_db_state("Before Session Creation")
        self.print_db_state(pre_creation_state, "BEFORE CREATION")
        
        print("\n📌 Attempting to create session with:")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")
        
        try:
            SessionYearModel.objects.create(
                session_start_year=start_date,
                session_end_year=end_date
            )
            self.fail("❌ TEST RESULT: FAILURE — Session should not be created when end date exceeds 2 years from start.\n")
        except Exception as e:
            print("✅ TEST RESULT: SUCCESS — Creation failed as expected.")
            print(f"  - Error: {str(e)}\n")
        
        post_creation_state = self.get_db_state("After Session Creation")
        self.print_db_state(post_creation_state, "AFTER CREATION")

    def test_E9_session_creation_end_date_less_than_2_years_success(self):
        """E9: end date = start date + 2 years -1 day; follow other criteria -> expect success."""
        print("\n" + "*"*100)
        print("\n🔍 TEST E9: SESSION CREATION WITH END DATE = START DATE + 2 YEARS - 1 DAY")
        print("*"*100 + "\n")
        
        initial_state = self.get_db_state("Initial State")
        self.print_db_state(initial_state, "INITIAL STATE")
        from datetime import date
        start_date = date(2025, 5, 1)
        end_date = date(2027, 4, 30)  # 2 years - 1 day
        
        pre_creation_state = self.get_db_state("Before Session Creation")
        self.print_db_state(pre_creation_state, "BEFORE CREATION")
        
        print("\n📌 Creating session with:")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")
        
        try:
            session = SessionYearModel.objects.create(
                session_start_year=start_date,
                session_end_year=end_date
            )
        except Exception as e:
            self.fail(f"❌ TEST RESULT: FAILURE — Unexpected error during session creation: {e}")
        
        post_creation_state = self.get_db_state("After Session Creation")
        self.print_db_state(post_creation_state, "AFTER CREATION")
        
        self.assertEqual(session.session_start_year, start_date)
        self.assertEqual(session.session_end_year, end_date)
        print("\n✅ TEST RESULT: SUCCESS")
        print(f"  - Session created with ID: {session.id}")
        print(f"  - Start Date: {session.session_start_year}")
        print(f"  - End Date: {session.session_end_year}\n")


    # E10: end_date = start_date (at lower boundary) → expect error
    def test_E10_session_creation_end_date_equals_start_date_error(self):
        """E10: end date = start date at lower boundary; follow other criteria -> expect error."""
        print("\n" + "*"*100)
        print("\n🔍 TEST E10: SESSION CREATION WITH END DATE EQUAL TO START DATE (LOWER BOUNDARY)")
        print("*"*100 + "\n")
        
        initial_state = self.get_db_state("Initial State")
        self.print_db_state(initial_state, "INITIAL STATE")
        from datetime import date
        start_date = date(2025, 5, 1)
        end_date = date(2025, 5, 1)  # same as start date
        
        pre_creation_state = self.get_db_state("Before Session Creation")
        self.print_db_state(pre_creation_state, "BEFORE CREATION")
        
        print("\n📌 Attempting to create session with:")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")
        
        try:
            SessionYearModel.objects.create(
                session_start_year=start_date,
                session_end_year=end_date
            )
            self.fail("❌ TEST RESULT: FAILURE — Session should not be created when end date equals start date.\n")
        except Exception as e:
            print("✅ TEST RESULT: SUCCESS — Creation failed as expected.")
            print(f"  - Error: {str(e)}\n")
        
        post_creation_state = self.get_db_state("After Session Creation")
        self.print_db_state(post_creation_state, "AFTER CREATION")
    
    # E11: end_date = start_date at upper boundary → expect error
    def test_E11_session_creation_end_date_equals_start_date_at_upper_boundary_error(self):
        """E11: end date = start date at upper boundary; follow other criteria -> expect error."""
        print("\n" + "*"*100)
        print("\n🔍 TEST E11: SESSION CREATION WITH END DATE EQUAL TO START DATE (UPPER BOUNDARY)")
        print("*"*100 + "\n")
        
        initial_state = self.get_db_state("Initial State")
        self.print_db_state(initial_state, "INITIAL STATE")
        from datetime import date
        start_date = date(2030, 12, 31)
        end_date = date(2030, 12, 31)
        
        pre_creation_state = self.get_db_state("Before Session Creation")
        self.print_db_state(pre_creation_state, "BEFORE CREATION")
        
        print("\n📌 Attempting to create session with:")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")
        
        try:
            SessionYearModel.objects.create(
                session_start_year=start_date,
                session_end_year=end_date
            )
            self.fail("❌ TEST RESULT: FAILURE — Session should not be created when end date equals start date at upper boundary.\n")
        except Exception as e:
            print("✅ TEST RESULT: SUCCESS — Creation failed as expected.")
            print(f"  - Error: {str(e)}\n")
        
        post_creation_state = self.get_db_state("After Session Creation")
        self.print_db_state(post_creation_state, "AFTER CREATION")
    
    # E12: end_date = start_date - 1 day at lower boundary → expect error
    def test_E12_session_creation_end_date_before_start_date_error(self):
        """E12: end date = start date – 1 day at lower boundary; follow other criteria -> expect error."""
        print("\n" + "*"*100)
        print("\n🔍 TEST E12: SESSION CREATION WITH END DATE BEFORE START DATE (LOWER BOUNDARY)")
        print("*"*100 + "\n")
        
        initial_state = self.get_db_state("Initial State")
        self.print_db_state(initial_state, "INITIAL STATE")
        from datetime import date
        start_date = date(2025, 5, 1)
        end_date = date(2025, 4, 30)  # one day before start date
        
        pre_creation_state = self.get_db_state("Before Session Creation")
        self.print_db_state(pre_creation_state, "BEFORE CREATION")
        
        print("\n📌 Attempting to create session with:")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")
        
        try:
            SessionYearModel.objects.create(
                session_start_year=start_date,
                session_end_year=end_date
            )
            self.fail("❌ TEST RESULT: FAILURE — Session should not be created when end date is before start date.\n")
        except Exception as e:
            print("✅ TEST RESULT: SUCCESS — Creation failed as expected.")
            print(f"  - Error: {str(e)}\n")
        
        post_creation_state = self.get_db_state("After Session Creation")
        self.print_db_state(post_creation_state, "AFTER CREATION")

    # E13: end_date = start_date + 1 day at lower boundary → expect success
    def test_E13_session_creation_end_date_just_after_start_date_success(self):
        """E13: end date = start date + 1 day at lower boundary; follow other criteria -> expect success."""
        print("\n" + "*"*100)
        print("\n🔍 TEST E13: SESSION CREATION WITH END DATE = START DATE + 1 DAY (LOWER BOUNDARY)")
        print("*"*100 + "\n")
        
        initial_state = self.get_db_state("Initial State")
        self.print_db_state(initial_state, "INITIAL STATE")
        from datetime import date
        start_date = date(2025, 5, 1)
        end_date = date(2025, 5, 2)
        
        pre_creation_state = self.get_db_state("Before Session Creation")
        self.print_db_state(pre_creation_state, "BEFORE CREATION")
        
        print("\n📌 Creating session with:")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")
        
        try:
            session = SessionYearModel.objects.create(
                session_start_year=start_date,
                session_end_year=end_date
            )
        except Exception as e:
            self.fail(f"❌ TEST RESULT: FAILURE — Unexpected error: {e}")
        
        post_creation_state = self.get_db_state("After Session Creation")
        self.print_db_state(post_creation_state, "AFTER CREATION")
        
        self.assertEqual(session.session_start_year, start_date)
        self.assertEqual(session.session_end_year, end_date)
        print("\n✅ TEST RESULT: SUCCESS")
        print(f"  - Session created with ID: {session.id}")
        print(f"  - Start Date: {session.session_start_year}")
        print(f"  - End Date: {session.session_end_year}\n")
    
    # E14: end_date = start_date – 1 day at upper boundary → expect error
    def test_E14_session_creation_end_date_before_start_date_at_upper_boundary_error(self):
        """E14: end date = start date – 1 day at upper boundary; follow other criteria -> expect error."""
        print("\n" + "*"*100)
        print("\n🔍 TEST E14: SESSION CREATION WITH END DATE BEFORE START DATE (UPPER BOUNDARY)")
        print("*"*100 + "\n")
        
        initial_state = self.get_db_state("Initial State")
        self.print_db_state(initial_state, "INITIAL STATE")
        from datetime import date
        start_date = date(2030, 12, 31)
        end_date = date(2030, 12, 30)
        
        pre_creation_state = self.get_db_state("Before Session Creation")
        self.print_db_state(pre_creation_state, "BEFORE CREATION")
        
        print("\n📌 Attempting to create session with:")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")
        
        try:
            SessionYearModel.objects.create(
                session_start_year=start_date,
                session_end_year=end_date
            )
            self.fail("❌ TEST RESULT: FAILURE — Session should not be created when end date is before start date at upper boundary.\n")
        except Exception as e:
            print("✅ TEST RESULT: SUCCESS — Creation failed as expected.")
            print(f"  - Error: {str(e)}\n")
            
        post_creation_state = self.get_db_state("After Session Creation")
        self.print_db_state(post_creation_state, "AFTER CREATION")
    
    # E15: end_date = start_date + 1 day at upper boundary → expect error
    def test_E15_session_creation_end_date_just_after_upper_boundary_error(self):
        """E15: end date = start date + 1 day at upper boundary; follow other criteria -> expect error."""
        print("\n" + "*"*100)
        print("\n🔍 TEST E15: SESSION CREATION WITH END DATE = START DATE + 1 DAY AT UPPER BOUNDARY")
        print("*"*100 + "\n")
        
        initial_state = self.get_db_state("Initial State")
        self.print_db_state(initial_state, "INITIAL STATE")
        from datetime import date
        start_date = date(2030, 12, 31)
        end_date = date(2031, 1, 1)
        
        pre_creation_state = self.get_db_state("Before Session Creation")
        self.print_db_state(pre_creation_state, "BEFORE CREATION")
        
        print("\n📌 Attempting to create session with:")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")
        
        try:
            SessionYearModel.objects.create(
                session_start_year=start_date,
                session_end_year=end_date
            )
            self.fail("❌ TEST RESULT: FAILURE — Session should not be created when end date exceeds upper boundary by 1 day.\n")
        except Exception as e:
            print("✅ TEST RESULT: SUCCESS — Creation failed as expected.")
            print(f"  - Error: {str(e)}\n")
            
        post_creation_state = self.get_db_state("After Session Creation")
        self.print_db_state(post_creation_state, "AFTER CREATION")
    
    # E16: missing start_date → expect error
    def test_E16_session_creation_missing_start_date_error(self):
        """E16: missing start date; follow other criteria -> expect error."""
        print("\n" + "*"*100)
        print("\n🔍 TEST E16: SESSION CREATION WITH MISSING START DATE")
        print("*"*100 + "\n")
        
        initial_state = self.get_db_state("Initial State")
        self.print_db_state(initial_state, "INITIAL STATE")
        from datetime import date
        start_date = None
        end_date = date(2030, 12, 31)
        
        pre_creation_state = self.get_db_state("Before Session Creation")
        self.print_db_state(pre_creation_state, "BEFORE CREATION")
        
        print("\n📌 Attempting to create session with missing start date:")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")
        
        try:
            SessionYearModel.objects.create(
                session_start_year=start_date,
                session_end_year=end_date
            )
            self.fail("❌ TEST RESULT: FAILURE — Session should not be created with missing start date.\n")
        except Exception as e:
            print("✅ TEST RESULT: SUCCESS — Creation failed as expected.")
            print(f"  - Error: {str(e)}\n")
            
        post_creation_state = self.get_db_state("After Session Creation")
        self.print_db_state(post_creation_state, "AFTER CREATION")
    
    # E17: missing end_date → expect error
    def test_E17_session_creation_missing_end_date_error(self):
        """E17: missing end date; follow other criteria -> expect error."""
        print("\n" + "*"*100)
        print("\n🔍 TEST E17: SESSION CREATION WITH MISSING END DATE")
        print("*"*100 + "\n")
        
        initial_state = self.get_db_state("Initial State")
        self.print_db_state(initial_state, "INITIAL STATE")
        from datetime import date
        start_date = date(2025, 5, 1)
        end_date = None
        
        pre_creation_state = self.get_db_state("Before Session Creation")
        self.print_db_state(pre_creation_state, "BEFORE CREATION")
        
        print("\n📌 Attempting to create session with missing end date:")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")
        
        try:
            SessionYearModel.objects.create(
                session_start_year=start_date,
                session_end_year=end_date
            )
            self.fail("❌ TEST RESULT: FAILURE — Session should not be created with missing end date.\n")
        except Exception as e:
            print("✅ TEST RESULT: SUCCESS — Creation failed as expected.")
            print(f"  - Error: {str(e)}\n")
            
        post_creation_state = self.get_db_state("After Session Creation")
        self.print_db_state(post_creation_state, "AFTER CREATION")
    
    # E18: wrong format with slashes → expect error
    def test_E18_session_creation_wrong_format_slashes_error(self):
        """E18: wrong format with slashes; follow other criteria -> expect error."""
        print("\n" + "*"*100)
        print("\n🔍 TEST E18: SESSION CREATION WITH WRONG DATE FORMAT (SLASHES)")
        print("*"*100 + "\n")
        
        initial_state = self.get_db_state("Initial State")
        self.print_db_state(initial_state, "INITIAL STATE")
        start_date = "2025/01/01"
        end_date = "2027/01/01"
        
        pre_creation_state = self.get_db_state("Before Session Creation")
        self.print_db_state(pre_creation_state, "BEFORE CREATION")
        
        print("\n📌 Attempting to create session with wrong date format (slashes):")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")
        
        try:
            SessionYearModel.objects.create(
                session_start_year=start_date,
                session_end_year=end_date
            )
            self.fail("❌ TEST RESULT: FAILURE — Session should not be created with wrong date format (slashes).\n")
        except Exception as e:
            print("✅ TEST RESULT: SUCCESS — Creation failed as expected.")
            print(f"  - Error: {str(e)}\n")
            
        post_creation_state = self.get_db_state("After Session Creation")
        self.print_db_state(post_creation_state, "AFTER CREATION")
    
    # E19: wrong format with DD-MM-YYYY → expect error
    def test_E19_session_creation_wrong_format_dd_mm_yyyy_error(self):
        """E19: wrong format with DD-MM-YYYY; follow other criteria -> expect error."""
        print("\n" + "*"*100)
        print("\n🔍 TEST E19: SESSION CREATION WITH WRONG DATE FORMAT (DD-MM-YYYY)")
        print("*"*100 + "\n")
        
        initial_state = self.get_db_state("Initial State")
        self.print_db_state(initial_state, "INITIAL STATE")
        
        start_date = "31-08-2024"
        end_date = "01-07-2026"
        
        pre_creation_state = self.get_db_state("Before Session Creation")
        self.print_db_state(pre_creation_state, "BEFORE CREATION")
        
        print("\n📌 Attempting to create session with wrong date format (DD-MM-YYYY):")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")
        
        try:
            SessionYearModel.objects.create(
                session_start_year=start_date,
                session_end_year=end_date
            )
            self.fail("❌ TEST RESULT: FAILURE — Session should not be created with wrong date format (DD-MM-YYYY).\n")
        except Exception as e:
            print("✅ TEST RESULT: SUCCESS — Creation failed as expected.")
            print(f"  - Error: {str(e)}\n")
        
        post_creation_state = self.get_db_state("After Session Creation")
        self.print_db_state(post_creation_state, "AFTER CREATION")
    
    # E20: start_date and end_date are duplicated → expect error
    def test_E20_session_creation_duplicate_dates_error(self):
        """E20: start_date and end_date are duplicated; follow other criteria -> expect error."""
        print("\n" + "*"*100)
        print("\n🔍 TEST E20: DUPLICATE SESSION CREATION WITH SAME DATES")
        print("*"*100 + "\n")
        
        from datetime import date
        start_date = date(2025, 5, 1)
        end_date = date(2027, 3, 1)
        
        print("\n📌 Creating initial session with:")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")
        try:
            session1 = SessionYearModel.objects.create(
                session_start_year=start_date,
                session_end_year=end_date
            )
            print(f"✅ Initial session created with ID: {session1.id}\n")
        except Exception as e:
            self.fail(f"Initial session creation failed unexpectedly: {e}")
        
        # Cố gắng tạo session trùng lặp
        pre_creation_state = self.get_db_state("Before Duplicate Session Creation")
        self.print_db_state(pre_creation_state, "BEFORE CREATION")
        
        print("\n📌 Attempting to create duplicate session with same dates:")
        print(f"  - Start Date: {start_date}")
        print(f"  - End Date: {end_date}\n")
        try:
            SessionYearModel.objects.create(
                session_start_year=start_date,
                session_end_year=end_date
            )
            self.fail("❌ TEST RESULT: FAILURE — Duplicate session should not be created.\n")
        except Exception as e:
            print("✅ TEST RESULT: SUCCESS — Duplicate creation failed as expected.")
            print(f"  - Error: {str(e)}\n")
            
        post_creation_state = self.get_db_state("After Duplicate Session Creation")
        self.print_db_state(post_creation_state, "AFTER CREATION")