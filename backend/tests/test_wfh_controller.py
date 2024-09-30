import unittest
import json
from datetime import datetime, timedelta
from app import create_app, db
from config import TestConfig
from app.models.staff import Staff
from app.models.wfh_request import WFHRequest
from app.models.wfh_schedule import WFHSchedule


class WFHControllerTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

        db.create_all()

        # Create staff members
        self.staff = Staff(
            staff_id=1,
            staff_fname="John",
            staff_lname="Doe",
            dept="Engineering",
            position="Engineer",
            country="CountryA",
            email="john.doe@example.com",
            reporting_manager=2,
            role=2,
            password="password123",
        )
        self.manager = Staff(
            staff_id=2,
            staff_fname="Jane",
            staff_lname="Smith",
            dept="Engineering",
            position="Manager",
            country="CountryA",
            email="jane.smith@example.com",
            reporting_manager=None,
            role=3,
            password="password456",
        )
        db.session.add_all([self.staff, self.manager])
        db.session.commit()

        self.today = datetime.now().date()
        self.future_date = (self.today + timedelta(days=5)).strftime("%Y-%m-%d")

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_create_wfh_request_success(self):
        data = {
            "staff_id": self.staff.staff_id,
            "manager_id": self.manager.staff_id,
            "reason_for_applying": "Working from home for personal reasons.",
            "date": self.future_date,
            "duration": "FULL_DAY",
            "dept": self.staff.dept,
            "position": self.staff.position,
        }
        response = self.client.post(
            "/api/request", data=json.dumps(data), content_type="application/json"
        )
        resp_data = response.get_json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            resp_data["message"], "WFH request and schedules created successfully"
        )

    def test_create_wfh_request_missing_fields(self):
        data = {
            "staff_id": self.staff.staff_id,
            # Missing required fields
        }
        response = self.client.post(
            "/api/request", data=json.dumps(data), content_type="application/json"
        )
        resp_data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing required field", resp_data["message"])

    def test_create_wfh_request_invalid_date(self):
        invalid_date = (self.today - timedelta(days=61)).strftime("%Y-%m-%d")
        data = {
            "staff_id": self.staff.staff_id,
            "manager_id": self.manager.staff_id,
            "reason_for_applying": "Working from home for personal reasons.",
            "date": invalid_date,
            "duration": "FULL_DAY",
            "dept": self.staff.dept,
            "position": self.staff.position,
        }
        response = self.client.post(
            "/api/request", data=json.dumps(data), content_type="application/json"
        )
        resp_data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            resp_data["message"],
            "Start date must be between 2 months ago and 3 months from now.",
        )

    def test_get_pending_requests(self):
        # Create a pending request
        wfh_request = WFHRequest(
            staff_id=self.staff.staff_id,
            manager_id=self.manager.staff_id,
            request_date=self.today,
            start_date=datetime.strptime(self.future_date, "%Y-%m-%d").date(),
            reason_for_applying="Pending request",
        )
        db.session.add(wfh_request)
        db.session.commit()

        response = self.client.get(f"/api/pending-requests/{self.manager.staff_id}")
        resp_data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(resp_data), 1)
        self.assertEqual(resp_data[0]["staff_id"], self.staff.staff_id)

    def test_get_pending_requests_no_requests(self):
        response = self.client.get(f"/api/pending-requests/{self.manager.staff_id}")
        resp_data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(resp_data), 0)

    def test_update_wfh_request_approve(self):
        # Create a pending request
        wfh_request = WFHRequest(
            staff_id=self.staff.staff_id,
            manager_id=self.manager.staff_id,
            request_date=self.today,
            start_date=datetime.strptime(self.future_date, "%Y-%m-%d").date(),
            reason_for_applying="Pending request",
        )
        db.session.add(wfh_request)
        db.session.commit()

        data = {
            "request_id": wfh_request.request_id,
            "request_status": "APPROVED",
            "reason": "",
        }
        response = self.client.patch(
            "/api/pending-requests",
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 500)
        self.assertIn("Successfully updated request", response.get_data(as_text=True))

    def test_update_wfh_request_reject(self):
        # Create a pending request
        wfh_request = WFHRequest(
            staff_id=self.staff.staff_id,
            manager_id=self.manager.staff_id,
            request_date=self.today,
            start_date=datetime.strptime(self.future_date, "%Y-%m-%d").date(),
            reason_for_applying="Pending request",
        )
        db.session.add(wfh_request)
        db.session.commit()

        data = {
            "request_id": wfh_request.request_id,
            "request_status": "REJECTED",
            "reason": "Insufficient staffing available.",
        }
        response = self.client.patch(
            "/api/pending-requests",
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Successfully updated request", response.get_data(as_text=True))

    def test_reject_expired_request(self):
        # Create an expired request
        expired_date = (self.today - timedelta(days=61)).strftime("%Y-%m-%d")
        expired_request = WFHRequest(
            staff_id=self.staff.staff_id,
            manager_id=self.manager.staff_id,
            request_date=self.today,
            start_date=datetime.strptime(expired_date, "%Y-%m-%d").date(),
            reason_for_applying="Expired request",
        )
        db.session.add(expired_request)
        db.session.commit()

        response = self.client.post("/api/reject-expired-request")
        resp_data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("Updated 1 requests to 'REJECTED'.", resp_data["message"])

    def test_check_wfh_count(self):
        data = {"staff_id": self.staff.staff_id, "date": self.future_date}
        response = self.client.post(
            "/api/check-wfh-count",
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), "done")


if __name__ == "__main__":
    unittest.main()
