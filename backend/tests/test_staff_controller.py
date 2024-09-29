import unittest
import json
from app import create_app, db
from config import TestConfig
from app.models.staff import Staff


class StaffControllerTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

        db.create_all()

        # Create staff member
        self.staff = Staff(
            staff_id=1,
            staff_fname="John",
            staff_lname="Doe",
            dept="Engineering",
            position="Engineer",
            country="CountryA",
            email="john.doe@example.com",
            reporting_manager=None,
            role=2,
            password="password123",
        )
        db.session.add(self.staff)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_login_success(self):
        response = self.client.post(
            "/api/login",
            data=json.dumps(
                {"email": "john.doe@example.com", "password": "password123"}
            ),
            content_type="application/json",
        )
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["message"], "Login successful")
        self.assertEqual(data["staff_id"], self.staff.staff_id)

    def test_login_missing_fields(self):
        response = self.client.post(
            "/api/login",
            data=json.dumps(
                {
                    "email": "john.doe@example.com"
                    # Missing password
                }
            ),
            content_type="application/json",
        )
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["message"], "Missing email or password")

    def test_login_invalid_credentials(self):
        response = self.client.post(
            "/api/login",
            data=json.dumps(
                {"email": "john.doe@example.com", "password": "wrongpassword"}
            ),
            content_type="application/json",
        )
        data = response.get_json()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data["message"], "Invalid email or password")

    def test_get_staff_by_id_success(self):
        response = self.client.get(f"/api/staff/{self.staff.staff_id}")
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["staff_id"], self.staff.staff_id)
        self.assertEqual(data["email"], self.staff.email)

    def test_get_staff_by_id_not_found(self):
        with self.assertRaises(ValueError) as context:
            response = self.client.get("/api/staff/999")
            data = response.get_json()
        self.assertEqual(str(context.exception), "No staff found with id: 999")

    def test_get_staff_by_id_invalid_id(self):
        response = self.client.get("/api/staff/abc")  # Non-integer ID
        self.assertEqual(
            response.status_code, 404
        )  # Flask treats this as a 404 because the route expects an integer


if __name__ == "__main__":
    unittest.main()
