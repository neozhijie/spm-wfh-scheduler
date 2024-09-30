import unittest
from datetime import datetime, timedelta
from app import create_app, db
from config import TestConfig
from app.models.staff import Staff
from app.models.wfh_request import WFHRequest
from app.services.wfh_request_service import WFHRequestService


class WFHRequestServiceTestCase(unittest.TestCase):
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

    def test_create_request_success(self):
        today = datetime.now().date()
        start_date = (today + timedelta(days=5)).strftime("%Y-%m-%d")
        end_date = None
        wfh_request = WFHRequestService.create_request(
            staff_id=self.staff3.staff_id,
            manager_id=self.staff2.staff_id,
            request_date=today,
            start_date=start_date,
            end_date=end_date,
            reason_for_applying="Need to work from home",
        )
        self.assertIsNotNone(wfh_request)
        self.assertEqual(wfh_request.staff_id, self.staff3.staff_id)

    def test_create_request_invalid_start_date(self):
        today = datetime.now().date()
        invalid_start_date = (today - timedelta(days=61)).strftime("%Y-%m-%d")
        with self.assertRaises(ValueError) as context:
            WFHRequestService.create_request(
                staff_id=self.staff3.staff_id,
                manager_id=self.staff2.staff_id,
                request_date=today,
                start_date=invalid_start_date,
                end_date=None,
                reason_for_applying="Need to work from home",
            )
        self.assertEqual(
            str(context.exception),
            "Start date must be between 2 months ago and 3 months from now.",
        )

    def test_create_request_invalid_end_date(self):
        today = datetime.now().date()
        start_date = (today + timedelta(days=5)).strftime("%Y-%m-%d")
        end_date = (today + timedelta(days=4)).strftime("%Y-%m-%d")
        with self.assertRaises(ValueError) as context:
            WFHRequestService.create_request(
                staff_id=self.staff3.staff_id,
                manager_id=self.staff2.staff_id,
                request_date=today,
                start_date=start_date,
                end_date=end_date,
                reason_for_applying="Need to work from home",
            )
        self.assertEqual(str(context.exception), "End date must be after start date.")

    def test_create_request_existing_request(self):
        today = datetime.now().date()
        start_date = (today + timedelta(days=5)).strftime("%Y-%m-%d")
        WFHRequestService.create_request(
            staff_id=self.staff3.staff_id,
            manager_id=self.staff2.staff_id,
            request_date=today,
            start_date=start_date,
            end_date=None,
            reason_for_applying="First request",
        )
        with self.assertRaises(ValueError) as context:
            WFHRequestService.create_request(
                staff_id=self.staff3.staff_id,
                manager_id=self.staff2.staff_id,
                request_date=today,
                start_date=start_date,
                end_date=None,
                reason_for_applying="Second request",
            )
        self.assertEqual(
            str(context.exception), "A request for this date already exists."
        )

    def test_get_pending_requests_for_manager(self):
        today = datetime.now().date()
        start_date = (today + timedelta(days=5)).strftime("%Y-%m-%d")
        WFHRequestService.create_request(
            staff_id=self.staff3.staff_id,
            manager_id=self.staff2.staff_id,
            request_date=today,
            start_date=start_date,
            end_date=None,
            reason_for_applying="Need to work from home",
        )
        pending_requests = WFHRequestService.get_pending_requests_for_manager(
            self.staff2.staff_id
        )
        self.assertEqual(len(pending_requests), 1)
        self.assertEqual(pending_requests[0].staff_id, self.staff3.staff_id)

    def test_update_request_success(self):
        today = datetime.now().date()
        start_date = (today + timedelta(days=5)).strftime("%Y-%m-%d")
        wfh_request = WFHRequestService.create_request(
            staff_id=self.staff3.staff_id,
            manager_id=self.staff2.staff_id,
            request_date=today,
            start_date=start_date,
            end_date=None,
            reason_for_applying="Need to work from home",
        )
        two_months_ago = today - timedelta(days=60)
        response = WFHRequestService.update_request(
            request_id=wfh_request.request_id,
            new_request_status="APPROVED",
            two_months_ago=two_months_ago,
            reason=None,
        )
        self.assertTrue(response)
        updated_request = WFHRequest.query.get(wfh_request.request_id)
        print(updated_request)
        self.assertEqual(updated_request.status, "APPROVED")

    def test_update_request_invalid_date(self):
        today = datetime.now().date()
        invalid_start_date = today - timedelta(days=61)
        wfh_request = WFHRequest(
            staff_id=self.staff3.staff_id,
            manager_id=self.staff2.staff_id,
            request_date=today,
            start_date=invalid_start_date,
            end_date=None,
            reason_for_applying="Need to work from home",
        )
        db.session.add(wfh_request)
        db.session.commit()

        two_months_ago = today - timedelta(days=60)
        response = WFHRequestService.update_request(
            request_id=wfh_request.request_id,
            new_request_status="APPROVED",
            two_months_ago=two_months_ago,
            reason=None,
        )
        self.assertEqual(response, "The date is invalid to be approved")
        updated_request = WFHRequest.query.get(wfh_request.request_id)
        self.assertEqual(updated_request.status, "PENDING")

    def test_update_request_nonexistent(self):
        two_months_ago = datetime.now().date() - timedelta(days=60)
        response = WFHRequestService.update_request(
            request_id=999,
            new_request_status="APPROVED",
            two_months_ago=two_months_ago,
            reason=None,
        )
        self.assertEqual(response, "Request Does not Exist!")

    def test_reject_expired(self):
        today = datetime.now().date()
        valid_start_date = today - timedelta(days=30)
        expired_start_date = today - timedelta(days=61)
        valid_request = WFHRequest(
            staff_id=self.staff3.staff_id,
            manager_id=self.staff2.staff_id,
            request_date=today,
            start_date=valid_start_date,
            end_date=None,
            reason_for_applying="Valid request",
        )
        expired_request = WFHRequest(
            staff_id=self.staff3.staff_id,
            manager_id=self.staff2.staff_id,
            request_date=today,
            start_date=expired_start_date,
            end_date=None,
            reason_for_applying="Expired request",
        )
        db.session.add_all([valid_request, expired_request])
        db.session.commit()

        two_months_ago = today - timedelta(days=60)
        updated_count = WFHRequestService.reject_expired(two_months_ago)
        self.assertEqual(updated_count, 1)
        expired_request = WFHRequest.query.filter_by(
            reason_for_applying="Expired request"
        ).first()
        self.assertEqual(expired_request.status, "REJECTED")
        valid_request = WFHRequest.query.filter_by(
            reason_for_applying="Valid request"
        ).first()
        self.assertEqual(valid_request.status, "PENDING")

    def test_check_date(self):
        two_months_ago = datetime.now().date() - timedelta(days=60)
        date_within_range = datetime.now().date() - timedelta(days=30)
        date_out_of_range = datetime.now().date() - timedelta(days=61)
        self.assertTrue(WFHRequestService.check_date(date_within_range, two_months_ago))
        self.assertFalse(
            WFHRequestService.check_date(date_out_of_range, two_months_ago)
        )

    def test_create_request_start_date_too_far(self):
        today = datetime.now().date()
        start_date = (today + timedelta(days=91)).strftime("%Y-%m-%d")  # Beyond 90 days
        with self.assertRaises(ValueError) as context:
            WFHRequestService.create_request(
                staff_id=self.staff3.staff_id,
                manager_id=self.staff2.staff_id,
                request_date=today,
                start_date=start_date,
                end_date=None,
                reason_for_applying="Need to work from home",
            )
        self.assertEqual(
            str(context.exception),
            "Start date must be between 2 months ago and 3 months from now.",
        )

    def test_create_request_end_date_before_start_date(self):
        today = datetime.now().date()
        start_date = (today + timedelta(days=5)).strftime("%Y-%m-%d")
        end_date = (today + timedelta(days=4)).strftime("%Y-%m-%d")
        with self.assertRaises(ValueError) as context:
            WFHRequestService.create_request(
                staff_id=self.staff3.staff_id,
                manager_id=self.staff2.staff_id,
                request_date=today,
                start_date=start_date,
                end_date=end_date,
                reason_for_applying="Need to work from home",
            )
        self.assertEqual(str(context.exception), "End date must be after start date.")


if __name__ == "__main__":
    unittest.main()
