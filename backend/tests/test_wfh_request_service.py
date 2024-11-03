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
            duration="FULL_DAY",
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
                duration="FULL_DAY",
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
                duration="FULL_DAY",
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
            duration="FULL_DAY",
        )
        with self.assertRaises(ValueError) as context:
            WFHRequestService.create_request(
                staff_id=self.staff3.staff_id,
                manager_id=self.staff2.staff_id,
                request_date=today,
                start_date=start_date,
                end_date=None,
                reason_for_applying="Second request",
                duration="FULL_DAY",
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
            duration="FULL_DAY",
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
            duration="FULL_DAY",
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
            duration="FULL_DAY",
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
            status = "PENDING",
            reason_for_applying="Valid request",
            duration="FULL_DAY",
        )
        expired_request = WFHRequest(
            staff_id=self.staff3.staff_id,
            manager_id=self.staff2.staff_id,
            request_date=today,
            start_date=expired_start_date,
            end_date=None,
            status = "PENDING",
            reason_for_applying="Expired request",
            duration="FULL_DAY",
        )
        db.session.add_all([valid_request, expired_request])
        db.session.commit()

        two_months_ago = today - timedelta(days=60)
        request_list = WFHRequestService.reject_expired(two_months_ago)
        self.assertEqual(len(request_list), 1)
        expired_request = WFHRequest.query.filter_by(
            reason_for_applying="Expired request"
        ).first()
        self.assertEqual(expired_request.status, "EXPIRED")
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
                duration="FULL_DAY",
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
                duration="FULL_DAY",
            )
        self.assertEqual(str(context.exception), "End date must be after start date.")

    def test_get_requests_no_requests_for_staff(self):
        # Assuming staff1 has no requests created in the setup
        no_requests = WFHRequestService.get_staff_requests(staff_id=self.staff1.staff_id)

        # Verify that the returned list is empty
        self.assertEqual(len(no_requests), 0)
        self.assertEqual(no_requests, [])

    def test_create_wfh_request_success(self):
        today = datetime.now().date()
        start_date = (today + timedelta(days=5)).strftime("%Y-%m-%d")

        # Create a WFH request for staff3
        wfh_request = WFHRequestService.create_request(
            staff_id=self.staff3.staff_id,
            manager_id=self.staff2.staff_id,
            request_date=today,
            start_date=start_date,
            end_date=None,
            reason_for_applying="Personal reasons",
            duration="FULL_DAY",
        )

        # Verify the request was created successfully
        requests = WFHRequestService.get_staff_requests(staff_id=self.staff3.staff_id)
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0].status, "PENDING")

    def test_cancel_request_success(self):
        # Create a pending request
        today = datetime.now().date()
        start_date = (today + timedelta(days=5)).strftime("%Y-%m-%d")
        wfh_request = WFHRequestService.create_request(
            staff_id=self.staff3.staff_id,
            manager_id=self.staff2.staff_id,
            request_date=today,
            start_date=start_date,
            end_date=None,
            reason_for_applying="Need to work from home",
            duration="FULL_DAY",
        )

        # Cancel the request
        two_months_ago = today - timedelta(days=60)
        response = WFHRequestService.update_request(
            request_id=wfh_request.request_id,
            new_request_status="CANCELLED",
            two_months_ago=two_months_ago,
            reason=None,
        )

        # Verify cancellation
        self.assertTrue(response)
        cancelled_request = WFHRequest.query.get(wfh_request.request_id)
        self.assertEqual(cancelled_request.status, "CANCELLED")

    def test_get_requests_with_invalid_staff_id(self):
        # Try to retrieve requests for a non-existent staff ID
        invalid_staff_id = 999  # Assuming this ID does not exist in the database
        requests = WFHRequestService.get_staff_requests(staff_id=invalid_staff_id)

        # Verify that the returned list is empty
        self.assertEqual(len(requests), 0)
        self.assertEqual(requests, [])

    def test_check_withdrawal_1(self):
        today = datetime.now().date()
        start_date = today + timedelta(days=5)
        end_date = None

        # Create a WFH request
        work_from_home_request = WFHRequest(
            staff_id=self.staff3.staff_id,
            manager_id=self.staff2.staff_id,
            request_date=today,
            start_date=start_date, 
            end_date=end_date,
            reason_for_applying="Need to work from home",
            duration="FULL_DAY",
            status="APPROVED"
        ) 

        # Create a withdrawal request
        withdrawal_request = WFHRequest(
            staff_id=self.staff3.staff_id,
            manager_id=self.staff2.staff_id,
            request_date=today,
            start_date=start_date, 
            end_date=end_date,
            reason_for_applying="Withdraw WFH",
            duration="WITHDRAWAL_REQUEST",
            status="PENDING"
        )

        db.session.add(work_from_home_request)
        db.session.commit()
        db.session.add(withdrawal_request)
        db.session.commit()

        result = WFHRequestService.check_withdrawal(self.staff3.staff_id, start_date)

        self.assertEqual(result, True)

    def test_check_withdrawal_2(self):
        today = datetime.now().date()
        start_date = today + timedelta(days=5)
        end_date = None

        # Create a WFH request
        work_from_home_request = WFHRequest(
            staff_id=self.staff3.staff_id,
            manager_id=self.staff2.staff_id,
            request_date=today,
            start_date=start_date, 
            end_date=end_date,
            reason_for_applying="Need to work from home",
            duration="FULL_DAY",
            status="APPROVED"

        ) 

        db.session.add(work_from_home_request)
        db.session.commit()

        result = WFHRequestService.check_withdrawal(self.staff3.staff_id, start_date)

        self.assertEqual(result, False)

    def test_check_withdrawal_3(self):
        today = datetime.now().date()
        start_date = today + timedelta(days=5)
        end_date = None

        work_from_home_request_1 = WFHRequest(
            staff_id=self.staff3.staff_id,
            manager_id=self.staff2.staff_id,
            request_date=today,
            start_date=start_date, 
            end_date=end_date,
            reason_for_applying="Need to work from home",
            duration="FULL_DAY",
            status="APPROVED"
        ) 

        work_from_home_request_2 = WFHRequest(
            staff_id=self.staff3.staff_id,
            manager_id=self.staff2.staff_id,
            request_date=today,
            start_date=start_date + timedelta(days=1), 
            end_date=end_date,
            reason_for_applying="Need to work from home",
            duration="FULL_DAY",
            status="APPROVED"
        )

        db.session.add(work_from_home_request_1)
        db.session.commit()
        db.session.add(work_from_home_request_2)
        db.session.commit()

        result = WFHRequestService.check_withdrawal(self.staff3.staff_id, start_date)

        self.assertEqual(result, False)

if __name__ == "__main__":
    unittest.main()
