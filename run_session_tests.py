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
            ('SM_ADD_SE_01_start_date_is_end_date_minus_2_day_SUCCESS', 'start date = end date -2 day - SUCCESS'),
            ('SM_ADD_SE_02_start_date_is_end_date_minus_1_day_SUCCESS','start date = end date -1 day - SUCCESS'),
            ('SM_ADD_SE_03_start_date_equal_end_date_ERROR','start date = end date - ERROR'),
            ('SM_ADD_SE_04_start_date_greater_than_end_date_ERROR','start date = end date + 1 day - ERROR'),
            ('SM_ADD_SE_05_start_date_greater_than_end_date_plus_2_days_ERROR','start date = end date + 2 days - ERROR'),
            ('SM_ADD_SE_06_empty_start_date_ERROR','Empty start date - ERROR'),
            ('SM_ADD_SE_07_empty_end_date_ERROR','Empty end date - ERROR'),
            ('SM_ADD_SE_08_wrong_format_with_slashes_ERROR','wrong format with slashes - ERROR'),
            ('SM_ADD_SE_09_wrong_format_with_dd_mm_yyyy_ERROR','wrong format with DD-MM-YYYY - ERROR'),
            ('SM_ADD_SE_10_start_and_end_date_are_duplicated_ERROR','start_date and end_date are duplicated - ERROR'),
            ('SM_ADD_ID_01_semester_id_empty_ERROR','semester_id has empty string - ERROR'),
            ('SM_ADD_ID_02_semester_id_no_digit_ERROR','semester_id has no digit – ERROR'),
            ('SM_ADD_ID_03_semester_id_two_digits_ERROR','semester_id has 2 digits – ERROR'),
            ('SM_ADD_ID_04_semester_id_three_digits_SUCCESS','semester_id has 3 digits - SUCCESS'),
            ('SM_ADD_ID_05_semester_id_four_digits_ERROR','semester_id has 4 digits - ERROR'),
            ('SM_ADD_ID_06_semester_id_has_non_digit_characters_ERROR','semester_id has non-digit characters'),
            ('SM_ADD_ID_07_semester_id_has_lowercase_letter_ERROR','semester_id has lowercase letter – ERROR'),
            ('SM_ADD_ID_08_semester_id_3_digits_are_zero_ERROR','semester_id has 3 digits are zero- ERROR'),
            ('SM_ADD_ID_09_semester_id_3_digits_are_9_SUCCESS','semester_id has 3 digits are 9 - SUCCESS'),
            ('SM_ADD_ID_10_semester_id_contains_whitespace_ERROR','semester_id contains whitespace – ERROR'),
            ('SM_ADD_ID_11_semester_id_not_start_with_Y_ERROR','semester_id does not start with SB - ERROR'),
            ('SM_ADD_ID_12_semester_id_is_duplicated_ERROR','semester_id is duplicated - ERROR')
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