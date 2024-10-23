import unittest
from app import create_app, db
from config import TestConfig
from app.models.staff import Staff
from app.services.staff_service import StaffService


class StaffServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        staff1 = Staff(
            staff_id=1,
            staff_fname="Test",
            staff_lname="Director",
            dept="Test Department",
            position="Director",
            country="Test Country",
            email="director@test.com",
            reporting_manager=None,
            role=1,
            password="testpassword1",
        )
        staff2 = Staff(
            staff_id=2,
            staff_fname="Test",
            staff_lname="Manager",
            dept="Test Department",
            position="Manager",
            country="Test Country",
            email="manager@test.com",
            reporting_manager=1,
            role=3,
            password="testpassword3",
        )
        staff3 = Staff(
            staff_id=3,
            staff_fname="Test",
            staff_lname="Staff",
            dept="Test Department",
            position="Staff",
            country="Test Country",
            email="staff@test.com",
            reporting_manager=2,
            role=2,
            password="testpassword2",
        )
        staff4 = Staff(
            staff_id=4,
            staff_fname="Direct",
            staff_lname="StaffUnderDirector",
            dept="Test Department",
            position="Staff",
            country="Test Country",
            email="staffdirect@test.com",
            reporting_manager=1,  # Directly reporting to director
            role=2,
            password="testpassword4",
        )

        db.session.add_all([staff1, staff2, staff3, staff4])
        db.session.commit()

        self.staff1 = staff1
        self.staff2 = staff2
        self.staff3 = staff3
        self.staff4 = staff4

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_authenticate_staff_success(self):
        staff = StaffService.authenticate_staff("director@test.com", "testpassword1")
        self.assertIsNotNone(staff)
        self.assertEqual(staff.staff_id, 1)

    def test_authenticate_staff_wrong_password(self):
        staff = StaffService.authenticate_staff("director@test.com", "wrongpassword")
        self.assertIsNone(staff)

    def test_authenticate_staff_nonexistent_email(self):
        staff = StaffService.authenticate_staff("nonexistent@test.com", "somepassword")
        self.assertIsNone(staff)

    def test_get_staff_by_id_existing(self):
        staff = StaffService.get_staff_by_id(1)
        self.assertIsNotNone(staff)
        self.assertEqual(staff.staff_id, 1)

    def test_get_staff_by_id_nonexistent(self):
        with self.assertRaises(ValueError) as context:
            StaffService.get_staff_by_id(99)
        self.assertEqual(str(context.exception), "No staff found with id: 99")

    def test_get_staff_by_id_invalid(self):
        with self.assertRaises(ValueError) as context:
            StaffService.get_staff_by_id("invalid_id")
        self.assertEqual(str(context.exception), "No staff found with id: invalid_id")

    # Test cases for get_subordinates
    def test_get_subordinates_existing_subordinates(self):
        subordinates = StaffService.get_subordinates(self.staff2.staff_id)
        self.assertIsNotNone(subordinates)
        self.assertEqual(len(subordinates), 1)
        self.assertEqual(subordinates[0].staff_id, self.staff3.staff_id)

    def test_get_subordinates_no_subordinates(self):
        with self.assertRaises(ValueError) as context:
            StaffService.get_subordinates(self.staff3.staff_id)
        self.assertEqual(str(context.exception), f"No subordinates found for staff_id: {self.staff3.staff_id}")

    def test_get_subordinates_staff_not_found(self):
        with self.assertRaises(ValueError) as context:
            StaffService.get_subordinates(99)
        self.assertEqual(str(context.exception), "No subordinates found for staff_id: 99")

    # Test cases for get_all_subordinates
    def test_get_all_subordinates_director_with_direct_role2_subordinates(self):
        result = StaffService.get_all_subordinates(self.staff1.staff_id)
        self.assertEqual(result['type'], 'direct')
        self.assertIn('staff', result)
        staff_list = result['staff']
        self.assertIn(self.staff4, staff_list)
        self.assertEqual(len(staff_list), 1)

    def test_get_all_subordinates_director_with_role3_subordinates(self):
        # Remove staff4 to simulate director without direct role 2 subordinates
        db.session.delete(self.staff4)
        db.session.commit()

        result = StaffService.get_all_subordinates(self.staff1.staff_id)
        self.assertEqual(result['type'], 'manager')
        self.assertIn('managers', result)
        managers_with_staff = result['managers']
        self.assertEqual(len(managers_with_staff), 1)
        manager = list(managers_with_staff.keys())[0]
        self.assertEqual(manager.staff_id, self.staff2.staff_id)
        staff_list = managers_with_staff[manager]
        self.assertEqual(len(staff_list), 1)
        self.assertEqual(staff_list[0].staff_id, self.staff3.staff_id)

    def test_get_all_subordinates_director_with_no_subordinates(self):
        # Create a director with no subordinates
        staff5 = Staff(
            staff_id=5,
            staff_fname="DirectorNoSubs",
            staff_lname="NoSubs",
            dept="Test Department",
            position="Director",
            country="Test Country",
            email="director.nosubs@test.com",
            reporting_manager=None,
            role=1,
            password="testpassword5",
        )
        db.session.add(staff5)
        db.session.commit()

        result = StaffService.get_all_subordinates(staff5.staff_id)
        self.assertEqual(result['type'], 'none')
        self.assertIn('staff', result)
        self.assertEqual(len(result['staff']), 0)

    def test_get_all_subordinates_manager_with_subordinates(self):
        result = StaffService.get_all_subordinates(self.staff2.staff_id)
        self.assertEqual(result['type'], 'direct')
        self.assertIn('staff', result)
        staff_list = result['staff']
        self.assertEqual(len(staff_list), 1)
        self.assertEqual(staff_list[0].staff_id, self.staff3.staff_id)

    def test_get_all_subordinates_manager_no_subordinates(self):
        # Create a manager with no subordinates
        staff6 = Staff(
            staff_id=6,
            staff_fname="ManagerNoSubs",
            staff_lname="NoSubs",
            dept="Test Department",
            position="Manager",
            country="Test Country",
            email="manager.nosubs@test.com",
            reporting_manager=self.staff1.staff_id,
            role=3,
            password="testpassword6",
        )
        db.session.add(staff6)
        db.session.commit()

        result = StaffService.get_all_subordinates(staff6.staff_id)
        self.assertEqual(result['type'], 'direct')
        self.assertIn('staff', result)
        self.assertEqual(len(result['staff']), 0)

    def test_get_all_subordinates_staff_with_no_subordinates(self):
        result = StaffService.get_all_subordinates(self.staff3.staff_id)
        self.assertEqual(result['type'], 'none')
        self.assertIn('staff', result)
        self.assertEqual(len(result['staff']), 0)

    def test_get_all_subordinates_invalid_staff_id(self):
        with self.assertRaises(ValueError) as context:
            StaffService.get_all_subordinates(99)
        self.assertEqual(str(context.exception), "No staff found with id: 99")


if __name__ == "__main__":
    unittest.main()
