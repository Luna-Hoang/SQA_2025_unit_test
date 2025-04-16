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
            ('test_1_successful_subject_creation', 'Successfully create a new subject'),
            ('test_2_duplicate_subject_name', 'Create subject with duplicate name'),
            ('test_3_missing_required_values', 'Create subject with missing required values'),
            ('test_4_subject_name_length', 'Create subject with name too long'),
            ('test_5_invalid_course_id', 'Create subject with invalid courseID'),
            ('test_6_invalid_subject_name_characters', 'Create subject with invalid characters in name')
        ]
        
        test_results = []
        
        print(f"\n\n{'='*100}")
        print(f"LIST OF TESTS TO RUN:")
        for i, (test_method, test_name) in enumerate(test_cases, 1):
            print(f"🔍 {i}. {test_name}")
        print(f"{'='*100}\n")
        
        start_time = datetime.datetime.now()
        print(f"⏱️ STARTING TESTS: {start_time.strftime('%H:%M:%S')}")
        
        for i, (test_method, test_name) in enumerate(test_cases, 1):
            print(f"\n\n{'#'*100}")
            print(f"### TEST {i}: {test_name}")
            print(f"{'#'*100}\n")
            
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