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
        db.session.add_all([staff1, staff2, staff3])
        db.session.commit()

        self.staff1 = staff1
        self.staff2 = staff2
        self.staff3 = staff3

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


if __name__ == "__main__":
    unittest.main()
