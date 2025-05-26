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
from student_management_app.test_teacher import TeacherModelTest

def run_and_capture_tests():
    """Run tests and capture the output."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_filename = f"teacher_test_report_{timestamp}.txt"
    
    print(f"Running tests to detect errors in student management and saving the report to {report_filename}...")
    
    # Use StringIO to capture output
    captured_output = io.StringIO()
    
    with redirect_stdout(captured_output):
        print(f"ERROR DETECTION TEST REPORT - TEACHER - DATE: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"{'#'*100}\n")
        print("PURPOSE: These tests are designed to detect errors in the original software,")
        print("         NOT to add new validations. Each test will check the actual behavior")
        print("         of the software when faced with different input situations.")
        print(f"\n{'#'*100}\n")
        
        # Create and run each test individually to record complete results
        test_cases = [
            ('T_ADD_FN_01_first_name_has_empty_string_ERROR', 'first_name has empty string - ERROR'),
            ('T_ADD_FN_02_first_name_has_1_character_SUCCESS', 'first_name has 1 character - SUCCESS'),
            ('T_ADD_FN_03_first_name_has_2_characters_SUCCESS', 'first_name has 2 characters - SUCCESS'),
            ('T_ADD_FN_04_first_name_has_49_characters_SUCCESS', 'first_name has 49 characters - SUCCESS'),
            ('T_ADD_FN_05_first_name_has_50_characters_SUCCESS', 'first_name has 50 characters - SUCCESS'),
            ('T_ADD_FN_06_first_name_has_51_characters_ERROR', 'first_name has 51 characters - ERROR'),
            ('T_ADD_FN_07_first_name_contains_digits_ERROR', 'first_name contains digits - ERROR'),
            ('T_ADD_FN_08_first_name_contains_special_characters_ERROR', 'first_name contains special characters - ERROR'),
            ('T_ADD_LN_01_last_name_has_empty_string_ERROR','last_name has empty string - ERROR'),
            ('T_ADD_LN_02_last_name_has_1_character_SUCCESS','last_name has 1 character - SUCCESS'),
            ('T_ADD_LN_03_last_name_has_2_characters_SUCCESS','last_name has 2 characters - SUCCESS'),
            ('T_ADD_LN_04_last_name_has_49_characters_SUCCESS','last_name has 49 characters - SUCCESS'),
            ('T_ADD_LN_05_last_name_has_50_characters_SUCCESS','last_name has 50 characters - SUCCESS'),
            ('T_ADD_LN_06_last_name_has_51_characters_ERROR','last_name has 51 characters - ERROR'),
            ('T_ADD_LN_07_last_name_contains_digits_ERROR','last_name contains digits - ERROR'),
            ('T_ADD_LN_08_last_name_contains_special_characters_ERROR','last_name contains special characters - ERROR'),
            ('T_ADD_UN_01_user_name_has_empty_string_ERROR','user_name has empty string - ERROR'),
            ('T_ADD_UN_02_user_name_has_2_characters_ERROR','user_name has 2 character – ERROR'),
            ('T_ADD_UN_03_user_name_has_3_characters_SUCCESS','user_name has 3 characters – SUCCESS'),
            ('T_ADD_UN_04_user_name_has_4_characters_SUCCESS','user_name has 4 characters – SUCCESS'),
            ('T_ADD_UN_05_user_name_has_29_characters_SUCCESS','user_name has 29 characters – SUCCESS'),
            ('T_ADD_UN_06_user_name_has_30_characters_SUCCESS','user_name has 30 characters - SUCCESS'),
            ('T_ADD_UN_07_user_name_has_31_characters_ERROR','user_name has 31 characters - ERROR'),
            ('T_ADD_UN_08_user_name_starts_with_digit_ERROR','user_name starts with a digit - ERROR'),
            ('T_ADD_UN_09_user_name_contains_special_characters_ERROR','user_name contains special characters - ERROR'),
            ('T_ADD_UN_10_user_name_is_duplicated_ERROR','user_name is duplicated - ERROR'),
            ('T_ADD_EM_01_email_has_empty_string_ERROR','email has empty string - ERROR'),
            ('T_ADD_EM_02_email_has_7_characters_ERROR','email has 7 character – ERROR'),
            ('T_ADD_EM_03_email_has_8_characters_SUCCESS','email has 8 characters – SUCCESS'),
            ('T_ADD_EM_04_email_has_9_characters_SUCCESS','email has 9 characters – SUCCESS'),
            ('T_ADD_EM_05_email_has_49_characters_SUCCESS','email has 49 characters – SUCCESS'),
            ('T_ADD_EM_06_email_has_50_characters_SUCCESS','email has 50 characters – SUCCESS'),
            ('T_ADD_EM_07_email_has_51_characters_ERROR','email has 51 characters – SUCCESS'),
            ('T_ADD_EM_08_email_missing_domain_ERROR','email missing domain - ERROR'),
            ('T_ADD_EM_09_email_missing_at_symbol_ERROR','email missing @ symbol - ERROR'),
            ('T_ADD_EM_10_email_contains_special_characters_ERROR','email contains special characters, except “@” - ERROR'),
            ('T_ADD_EM_11_email_is_duplicated_ERROR','email is duplicated - ERROR'),
            ('T_ADD_PW_01_password_has_empty_string_ERROR','password has empty string - ERROR'),
            ('T_ADD_PW_02_password_has_7_characters_ERROR','password has 7 character – ERROR'),
            ('T_ADD_PW_03_password_has_8_characters_SUCCESS','password has 8 characters – SUCCESS'),
            ('T_ADD_PW_04_password_has_9_characters_SUCCESS','password has 9 characters – SUCCESS'),
            ('T_ADD_PW_05_password_has_63_characters_SUCCESS','password has 63 characters – SUCCESS'),
            ('T_ADD_PW_06_password_has_64_characters_SUCCESS','password has 64 characters – SUCCESS'),
            ('T_ADD_PW_07_password_has_65_characters_ERROR','password has 65 characters - ERROR'),
            ('T_ADD_PW_08_password_missing_uppercase_ERROR','password missing uppercase letter - ERROR'),
            ('T_ADD_PW_09_password_missing_lowercase_ERROR','password missing lowercase letter - ERROR'),
            ('T_ADD_PW_10_password_missing_digit_ERROR','password missing digit - ERROR'),
            ('T_ADD_PW_11_password_missing_special_character_ERROR','password missing special characters - ERROR')
        ]
        
        test_results = []
        
        for test_method, test_name in test_cases:            
            # Create a separate instance of the test class with an isolated environment
            test_instance = TeacherModelTest(test_method)

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