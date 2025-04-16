import os
import sys
import io
import datetime
from contextlib import redirect_stdout

# Django environment setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')
import django
django.setup()

# Import necessary Django modules
from django.test.runner import DiscoverRunner
from student_management_app.tests_session import SessionYearModelTest

def run_and_capture_tests():
    """Run tests and capture the output."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_filename = f"session_test_report_{timestamp}.txt"
    
    print(f"Running tests to detect errors in session management and saving the report to {report_filename}...")
    
    # Use StringIO to capture output
    captured_output = io.StringIO()
    
    with redirect_stdout(captured_output):
        print(f"ERROR DETECTION TEST REPORT - SESSION - DATE: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"{'#'*100}\n")
        print("PURPOSE: These tests are designed to detect errors in the original software,")
        print("         NOT to add new validations. Each test will check the actual behavior")
        print("         of the software when faced with different input situations.")
        print(f"\n{'#'*100}\n")
        
        # Create and run each test individually to record complete results
        test_cases = [
            ('test_E1_session_creation_lower_boundary_success', 'start date is exactly at lower boundary'),
            ('test_E2_session_creation_start_date_below_lower_boundary', 'start date = lower boundary -1 day'),
            ('test_E3_session_creation_start_date_above_lower_boundary_success', 'start date = lower boundary +1 day'),
            ('test_E4_session_creation_end_date_at_upper_boundary_success', 'end date is exactly at upper boundary'),
            ('test_E5_session_creation_end_date_just_below_upper_boundary_success', 'end date = upper boundary -1 day'),
            ('test_E6_session_creation_end_date_above_upper_boundary_error', 'end date = upper boundary +1 day'),
            ('test_E7_session_creation_end_date_equals_start_plus_2_years_success', 'end date = start date + 2 years'),
            ('test_E8_session_creation_end_date_exceeds_2_years_error', 'end date = start date + 2 years +1 day'),
            ('test_E9_session_creation_end_date_less_than_2_years_success', 'end date = start date + 2 years -1 day'),
            ('test_E10_session_creation_end_date_equals_start_date_error', 'end date = start date at lower boundary'),
            ('test_E11_session_creation_end_date_equals_start_date_at_upper_boundary_error', 'end date = start date at upper boundary'),
            ('test_E12_session_creation_end_date_before_start_date_error', 'end date = start date – 1 day at lower boundary'),
            ('test_E13_session_creation_end_date_just_after_start_date_success', 'end date = start date + 1 day at lower boundary'),
            ('test_E14_session_creation_end_date_before_start_date_at_upper_boundary_error', 'end date = start date – 1 day at upper boundary'),
            ('test_E15_session_creation_end_date_just_after_upper_boundary_error', 'end date = start date + 1 day at upper boundary'),
            ('test_E16_session_creation_missing_start_date_error', 'missing start date'),
            ('test_E17_session_creation_missing_end_date_error', 'missing end date'),
            ('test_E18_session_creation_wrong_format_slashes_error', 'wrong format with slashes'),
            ('test_E19_session_creation_wrong_format_dd_mm_yyyy_error', 'wrong format with DD-MM-YYYY'),
            ('test_E20_session_creation_duplicate_dates_error', 'start_date and end_date are duplicated')
        ]
        
        test_results = []
        
        for test_method, test_name in test_cases:            
            # Create a separate instance of the test class with an isolated environment
            test_instance = SessionYearModelTest(test_method)

            test_instance.setUp()
            
            # Run the test method
            success = True
            error_message = None
            try:
                # Run a specific test
                getattr(test_instance, test_method)()
                test_results.append((test_name, True, None))
            except Exception as e:
                success = False
                error_message = str(e)
                test_results.append((test_name, False, error_message))
                print(f"\n❌ ERROR DURING TEST: {error_message}\n")
        
        # Summary of results
        print(f"\n\n{'='*100}")
        print("TEST RESULTS SUMMARY")
        print(f"{'='*100}\n")
        
        for test_name, success, error in test_results:
            status = "✅ COMPLETED" if success else "❌ ERROR"
            error_info = f" - {error}" if error else ""
            print(f"{status}: {test_name}{error_info}")
        
        print(f"\n{'='*100}")
        print("END OF TEST REPORT")
    
    # Save the captured output to a file
    with open(report_filename, 'w', encoding='utf-8') as report_file:
        report_file.write(captured_output.getvalue())
    
    # Print a message to the screen
    print(f"Test report has been saved to {os.path.abspath(report_filename)}")
    
    # Return the report content
    return captured_output.getvalue()

if __name__ == "__main__":
    run_and_capture_tests() 