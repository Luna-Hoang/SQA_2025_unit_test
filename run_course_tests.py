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
from student_management_app.tests_course import CoursesModelTest

def run_and_capture_tests():
    """Run tests and capture the output."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_filename = f"course_test_report_{timestamp}.txt"
    
    print(f"Running tests to detect errors in course management and saving the report to {report_filename}...")
    
    # Use StringIO to capture output
    captured_output = io.StringIO()
    
    with redirect_stdout(captured_output):
        print(f"ERROR DETECTION TEST REPORT - COURSE - DATE: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"{'#'*100}\n")
        print("PURPOSE: These tests are designed to detect errors in the original software,")
        print("         NOT to add new validations. Each test will check the actual behavior")
        print("         of the software when faced with different input situations.")
        print(f"\n{'#'*100}\n")
        
        # Create and run each test individually to record complete results
        test_cases = [
            ('test_C1_empty_course_name', 'ccourse_name is empty'),
            ('test_C2_course_name_1_char','course_name has 1 character'),
            ('test_C3_course_name_2_chars', 'course_name has 2 characters'),
            ('test_C4_course_name_3_chars', 'course_name has 3 characters'),
            ('test_C5_course_name_49_chars', 'course_name has 49 characters'),
            ('test_C6_course_name_50_chars', 'course_name has 50 characters'),
            ('test_C7_course_name_51_chars', 'course_name has 51 characters'),
            ('test_C8_course_name_with_special_char', 'course_name contains special character'),
            ('test_C9_course_name_duplicate', 'course_name is duplicated'),
        ]
        
        test_results = []
        
        for test_method, test_name in test_cases:            
            # Create a separate instance of the test class with an isolated environment
            test_instance = CoursesModelTest(test_method)

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