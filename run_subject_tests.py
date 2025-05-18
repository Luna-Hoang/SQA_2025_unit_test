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
from student_management_app.tests_subject import SubjectModelTest

def run_and_capture_tests():
    """Run tests and capture the output."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_filename = f"subject_test_report_{timestamp}.txt"
    
    print(f"Running tests to detect errors in subject management and saving the report to {report_filename}...")
    
    # Use StringIO to capture output
    captured_output = io.StringIO()
    
    with redirect_stdout(captured_output):
        print(f"ERROR DETECTION TEST REPORT - SUBJECT - DATE: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"{'#'*100}\n")
        print("PURPOSE: These tests are designed to detect errors in the original software,")
        print("         NOT to add new validations. Each test will check the actual behavior")
        print("         of the software when faced with different input situations.")
        print(f"\n{'#'*100}\n")
        
        # Create and run each test individually to record complete results
        test_cases = [
            ('S_ADD_ID_01_subject_id_has_empty_string_ERROR', 'subject_id has empty string - ERROR'),
            ('S_ADD_ID_02_subject_id_has_no_digit_ERROR', 'subject_id has no digit - ERROR'),
            ('S_ADD_ID_03_subject_id_has_two_digits_ERROR', 'subject_id has 2 digits – ERROR'),
            ('S_ADD_ID_04_subject_id_has_three_digits_SUCCESS','subject_id has 3 digits - SUCCESS'),
            ('S_ADD_ID_05_subject_id_has_four_digits_ERROR','subject_id has 4 digits - ERROR'),
            ('S_ADD_ID_06_subject_id_has_nondigit_characters_ERROR','subject_id has non-digit characters'),
            ('S_ADD_ID_07_subject_id_has_lowercase_letter_ERROR','subject_id has lowercase letter – ERROR'),
            ('S_ADD_ID_08_subject_id_has_all_zeros_digits_ERROR','subject_id has 3 digits are zero- ERROR'),
            ('S_ADD_ID_09_subject_id_has_digits_999_SUCCESS','subject_id has 3 digits are 9 - SUCCESS'),
            ('S_ADD_ID_10_subject_id_contains_whitespace_ERROR','subject_id contains whitespace – ERROR'),
            ('S_ADD_ID_11_subject_id_not_start_SB_ERROR','subject_id does not start with SB - ERROR'),
            ('S_ADD_ID_12_subject_id_is_duplicated_ERROR','subject_id is duplicated - ERROR'),
            ('S_ADD_NA_01_subject_name_empty_string_ERROR','subject_name has empty string - ERROR'),
            ('S_ADD_NA_02_subject_name_one_char_ERROR','subject_name has 1 characters - ERROR'),
            ('S_ADD_NA_03_subject_name_two_chars_SUCCESS','subject_name has 2 characters - SUCCESS'),
            ('S_ADD_NA_04_subject_name_three_chars_SUCCESS','subject_name has 3 characters – SUCCESS'),
            ('S_ADD_NA_05_subject_name_49_chars_SUCCESS','subject_name has 49 characters - SUCCESS'),
            ('S_ADD_NA_06_subject_name_50_chars_SUCCESS','subject_name has 50 characters - SUCCESS'),
            ('S_ADD_NA_07_subject_name_51_chars_ERROR','subject_name has 51 characters - ERROR'),
            ('S_ADD_NA_08_subject_name_special_char_ERROR','subject_name contains special character - ERROR'),
            ('S_ADD_NA_09_subject_name_duplicated_ERROR','subject_name is duplicated - ERROR'),
            ('S_ADD_STA_01_course_id_empty_string_ERROR','course_id has empty string - ERROR'),
            ('S_ADD_STA_02_course_id_exists_SUCCESS','course_id is existed in the system - SUCCESS'),
            ('S_ADD_STA_03_course_id_not_exists_ERROR','course_id is not existed in the system - ERROR')
        ]
        
        test_results = []
        
        print(f"\n{'='*100}")
        print(f"LIST OF TESTS TO RUN:")
        for i, (test_method, test_name) in enumerate(test_cases, 1):
            print(f"🔍 {i}. {test_name}")
        print(f"{'='*100}\n")
        
        start_time = datetime.datetime.now()
        print(f"⏱️ STARTING TESTS: {start_time.strftime('%H:%M:%S')}")
        
        for i, (test_method, test_name) in enumerate(test_cases, 1):          
            # Create a separate instance of the test class with an isolated environment
            test_instance = SubjectModelTest(test_method)
            
            # Explicitly call setUp() before running the test
            test_instance.setUp()
            
            # Run the test method
            test_start_time = datetime.datetime.now()
            success = True
            error_message = None
            try:
                # Run a specific test
                getattr(test_instance, test_method)()
                test_end_time = datetime.datetime.now()
                test_duration = (test_end_time - test_start_time).total_seconds()
                test_results.append((test_name, True, None, test_duration))
            except Exception as e:
                test_end_time = datetime.datetime.now()
                test_duration = (test_end_time - test_start_time).total_seconds()
                success = False
                error_message = str(e)
                test_results.append((test_name, False, error_message, test_duration))
                print(f"\n❌ ERROR DURING TEST: {error_message}\n")
            finally:
                # Make sure to call tearDown() after the test to clean up
                try:
                    test_instance.tearDown()
                except Exception as cleanup_error:
                    print(f"\n⚠️ Warning: Error during test cleanup: {str(cleanup_error)}")
        
        end_time = datetime.datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        
        # Summary of results
        print(f"\n\n{'='*100}")
        print("📊 TEST RESULTS SUMMARY")
        print(f"{'='*100}\n")
        
        for i, (test_name, success, error, duration) in enumerate(test_results, 1):
            status = "✅ COMPLETED" if success else "❌ ERROR"
            error_info = f" - {error}" if error else ""
            print(f"{i}. {status}: {test_name} ({duration:.2f}s){error_info}")
        
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