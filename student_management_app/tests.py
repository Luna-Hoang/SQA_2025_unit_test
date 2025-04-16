from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import os
import json
import matplotlib.pyplot as plt
from .models import CustomUser, Students, Courses, SessionYearModel
from django.db import transaction
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

class StudentModelTest(TransactionTestCase):
    """
    Test case for the Students model.
    Using TransactionTestCase to test database transactions and rollbacks.
    """
    
    def capture_db_state(self, stage):
        """Capture the current state of the database for visualization."""
        db_state = {
            'stage': stage,
            'students_count': Students.objects.count(),
            'students': list(Students.objects.values('id', 'gender', 'address')),
            'users_count': CustomUser.objects.filter(user_type=3).count(),
            'users': list(CustomUser.objects.filter(user_type=3).values('id', 'username'))
        }
        
        # Append to our DB state log
        if not hasattr(self, 'db_states'):
            self.db_states = []
        self.db_states.append(db_state)
        
        return db_state
    
    def visualize_db_states(self):
        """Create a visualization of the database states during the test."""
        if not hasattr(self, 'db_states'):
            return
        
        # Create the visualization directory if it doesn't exist
        os.makedirs('test_results', exist_ok=True)
        
        # Save the raw data
        with open('test_results/db_states.json', 'w') as f:
            json.dump(self.db_states, f, indent=2)
        
        # Create a simple visualization
        stages = [state['stage'] for state in self.db_states]
        student_counts = [state['students_count'] for state in self.db_states]
        
        plt.figure(figsize=(12, 6))
        plt.plot(stages, student_counts, marker='o', linestyle='-', linewidth=2, markersize=10)
        plt.title('Database State During Test Execution', fontsize=16)
        plt.xlabel('Test Stage', fontsize=14)
        plt.ylabel('Number of Student Records', fontsize=14)
        plt.grid(True)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Save the figure
        plt.savefig('test_results/db_state_visualization.png')
        
        # Create a more detailed table visualization
        fig, ax = plt.subplots(figsize=(14, 8))
        ax.axis('tight')
        ax.axis('off')
        
        # Create table data
        table_data = []
        headers = ['Stage', 'Students Count', 'Student IDs', 'Users Count', 'User IDs']
        
        for state in self.db_states:
            student_ids = ', '.join([str(s['id']) for s in state['students']])
            user_ids = ', '.join([str(u['id']) for u in state['users']])
            table_data.append([
                state['stage'],
                state['students_count'],
                student_ids if student_ids else 'None',
                state['users_count'],
                user_ids if user_ids else 'None'
            ])
        
        table = ax.table(cellText=table_data, colLabels=headers, loc='center', cellLoc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1, 1.5)
        
        plt.title('Detailed Database State During Test Execution', fontsize=16)
        plt.tight_layout()
        
        # Save the detailed figure
        plt.savefig('test_results/db_state_detailed.png')
    
    @disable_signals
    def setUp(self):
        """Set up test data before each test method runs."""
        # Capture initial DB state
        self.capture_db_state('Initial State')
        
        # Create a session year
        self.session_year = SessionYearModel.objects.create(
            session_start_year=timezone.now().date(),
            session_end_year=(timezone.now() + timedelta(days=365)).date()
        )
        
        # Create a course
        self.course = Courses.objects.create(
            course_name="Test Course"
        )
        
        # Create a custom user for the student without triggering signals
        self.user = CustomUser.objects.create_user(
            username="teststudent",
            email="test@student.com",
            password="testpassword",
            user_type=3  # Student type
        )
        
        # Capture DB state after setup
        self.capture_db_state('After Setup')
    
    def tearDown(self):
        """Clean up after tests and generate visualization."""
        # Capture final DB state
        self.capture_db_state('Final State')
        
        # Generate visualization
        self.visualize_db_states()
    
    @disable_signals
    def test_create_student(self):
        """Test creating a student record."""
        # Capture DB state before test
        self.capture_db_state('Before Create')
        
        # Create a student
        student = Students.objects.create(
            admin=self.user,
            gender="Male",
            profile_pic="",
            address="Test Address",
            course_id=self.course,
            session_year_id=self.session_year
        )
        
        # Capture DB state after creation
        self.capture_db_state('After Create')
        
        # Verify the student was created
        self.assertEqual(Students.objects.count(), 1)
        self.assertEqual(student.admin.username, "teststudent")
        self.assertEqual(student.gender, "Male")
        self.assertEqual(student.address, "Test Address")
        self.assertEqual(student.course_id, self.course)
        self.assertEqual(student.session_year_id, self.session_year)
    
    @disable_signals
    def test_update_student(self):
        """Test updating a student record."""
        # Capture DB state before test
        self.capture_db_state('Before Update Test')
        
        # Create a student
        student = Students.objects.create(
            admin=self.user,
            gender="Male",
            profile_pic="",
            address="Test Address",
            course_id=self.course,
            session_year_id=self.session_year
        )
        
        # Capture DB state after creation
        self.capture_db_state('After Student Creation')
        
        # Update the student
        student.gender = "Female"
        student.address = "Updated Address"
        student.save()
        
        # Capture DB state after update
        self.capture_db_state('After Student Update')
        
        # Refresh from database
        student.refresh_from_db()
        
        # Verify the update
        self.assertEqual(student.gender, "Female")
        self.assertEqual(student.address, "Updated Address")
    
    @disable_signals
    def test_delete_student(self):
        """Test deleting a student record."""
        # Capture DB state before test
        self.capture_db_state('Before Delete Test')
        
        # Create a student
        student = Students.objects.create(
            admin=self.user,
            gender="Male",
            profile_pic="",
            address="Test Address",
            course_id=self.course,
            session_year_id=self.session_year
        )
        
        # Capture DB state after creation
        self.capture_db_state('After Student Creation')
        
        # Verify the student was created
        self.assertEqual(Students.objects.count(), 1)
        
        # Delete the student
        student.delete()
        
        # Capture DB state after deletion
        self.capture_db_state('After Student Deletion')
        
        # Verify the student was deleted
        self.assertEqual(Students.objects.count(), 0)
    
    @disable_signals
    def test_transaction_rollback(self):
        """Test transaction rollback when an error occurs."""
        # Capture DB state before test
        self.capture_db_state('Before Transaction Test')
        
        # Initial count
        initial_count = Students.objects.count()
        
        # Create a second user for the test
        second_user = CustomUser.objects.create_user(
            username="teststudent2",
            email="test2@student.com",
            password="testpassword",
            user_type=3
        )
        
        # Capture DB state after user creation
        self.capture_db_state('After Second User Creation')
        
        # Try to create a student with an invalid transaction
        try:
            with transaction.atomic():
                # Create a valid student
                student = Students.objects.create(
                    admin=second_user,
                    gender="Male",
                    profile_pic="",
                    address="Test Address",
                    course_id=self.course,
                    session_year_id=self.session_year
                )
                
                # Capture DB state within transaction
                self.capture_db_state('Within Transaction (Before Error)')
                
                # Verify the student was created within the transaction
                self.assertEqual(Students.objects.count(), initial_count + 1)
                
                # Force an error to trigger rollback
                # Trying to create another student with the same user (which violates the OneToOne relationship)
                Students.objects.create(
                    admin=second_user,  # This will cause an integrity error
                    gender="Female",
                    profile_pic="",
                    address="Another Address",
                    course_id=self.course,
                    session_year_id=self.session_year
                )
        except Exception:
            # Exception should be raised due to integrity error
            pass
        
        # Capture DB state after transaction
        self.capture_db_state('After Transaction (After Rollback)')
        
        # Verify that the transaction was rolled back and no students were added
        self.assertEqual(Students.objects.count(), initial_count)
