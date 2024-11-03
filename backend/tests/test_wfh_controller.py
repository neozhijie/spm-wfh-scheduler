import unittest
import json
from datetime import datetime, timedelta
from app import create_app, db
from config import TestConfig
from app.models.staff import Staff
from app.models.wfh_request import WFHRequest
from app.models.wfh_schedule import WFHSchedule
from unittest.mock import patch, Mock
from app.services.wfh_request_service import WFHRequestService
from app.services.wfh_schedule_service import WFHScheduleService


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
            reporting_manager=2,
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
            duration="FULL_DAY",
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

    def test_get_pending_requests_exception(self):
        with patch('app.services.wfh_request_service.WFHRequestService.get_pending_requests_for_manager', 
                side_effect=Exception("Database error")):
            response = self.client.get(f"/api/pending-requests/{self.manager.staff_id}")
            self.assertEqual(response.status_code, 500)
            self.assertIn("An error occurred", response.get_json()["message"])

    def test_update_wfh_request_approve(self):
        # Create a pending request
        wfh_request = WFHRequest(
            staff_id=self.staff.staff_id,
            manager_id=self.manager.staff_id,
            request_date=self.today,
            start_date=datetime.strptime(self.future_date, "%Y-%m-%d").date(),
            reason_for_applying="Pending request",
            duration="FULL_DAY",
        )
        db.session.add(wfh_request)
        db.session.commit()

        wfh_schedule = WFHSchedule(
            request_id = wfh_request.request_id,
            staff_id=self.staff.staff_id,
            manager_id=self.manager.staff_id,
            date= wfh_request.start_date,
            duration = "FULL_DAY",
            status = "PENDING",
            dept = self.staff.dept,
            position = self.staff.position
        )
        db.session.add(wfh_schedule)
        db.session.commit()

        data = {
            "request_id": wfh_request.request_id,
            "request_status": "APPROVED",
            "reason": "",
        }
        response = self.client.patch(
            "/api/update-request",
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Successfully updated request", response.get_data(as_text=True))

    def test_update_wfh_request_reject(self):
        # Create a pending request
        wfh_request = WFHRequest(
            staff_id=self.staff.staff_id,
            manager_id=self.manager.staff_id,
            request_date=self.today,
            start_date=datetime.strptime(self.future_date, "%Y-%m-%d").date(),
            reason_for_applying="Pending request",
            duration="FULL_DAY",
        )
        db.session.add(wfh_request)
        db.session.commit()

        wfh_schedule = WFHSchedule(
            request_id = wfh_request.request_id,
            staff_id=self.staff.staff_id,
            manager_id=self.manager.staff_id,
            date= wfh_request.start_date,
            duration = "FULL_DAY",
            status = "PENDING",
            dept = self.staff.dept,
            position = self.staff.position
        )
        db.session.add(wfh_schedule)
        db.session.commit()

        data = {
            "request_id": wfh_request.request_id,
            "request_status": "REJECTED",
            "reason": "Insufficient staffing available.",
        }
        response = self.client.patch(
            "/api/update-request",
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Successfully updated request", response.get_data(as_text=True))

    def test_update_wfh_request_approve_with_violations(self):
        # Create a recurring request
        wfh_request = WFHRequest(
            staff_id=self.staff.staff_id,
            manager_id=self.manager.staff_id,
            request_date=self.today,
            start_date=datetime.strptime(self.future_date, "%Y-%m-%d").date(),
            end_date=(datetime.strptime(self.future_date, "%Y-%m-%d") + timedelta(days=14)).date(),
            reason_for_applying="Recurring request",
            duration="FULL_DAY",
        )
        db.session.add(wfh_request)
        db.session.commit()

        with patch('app.services.wfh_check_service.WFHCheckService.check_team_count', 
                return_value='Policy violated'):
            data = {
                "request_id": wfh_request.request_id,
                "request_status": "APPROVED",
                "reason": "",
            }
            response = self.client.patch(
                "/api/update-request",
                data=json.dumps(data),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 400)
            self.assertIn("Cannot approve request due to policy violation", response.get_json()["message"])

    def test_update_wfh_request_general_exception_during_update(self):
        wfh_request = WFHRequest(
            staff_id=self.staff.staff_id,
            manager_id=self.manager.staff_id,
            request_date=self.today,
            start_date=datetime.strptime(self.future_date, "%Y-%m-%d").date(),
            reason_for_applying="Test request",
            duration="FULL_DAY",
        )
        db.session.add(wfh_request)
        db.session.commit()

        with patch('app.services.wfh_schedule_service.WFHScheduleService.update_schedule', 
                side_effect=Exception("Database error")):
            data = {
                "request_id": wfh_request.request_id,
                "request_status": "APPROVED",
                "reason": "",
            }
            response = self.client.patch(
                "/api/update-request",
                data=json.dumps(data),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 500)
            self.assertIn("An error occurred", response.get_json()["message"])

    def test_reject_expired_request(self):
        # Create an expired request
        expired_date = (self.today - timedelta(days=61)).strftime("%Y-%m-%d")
        expired_request = WFHRequest(
            staff_id=self.staff.staff_id,
            manager_id=self.manager.staff_id,
            request_date=self.today,
            start_date=datetime.strptime(expired_date, "%Y-%m-%d").date(),
            status="PENDING",
            reason_for_applying="Expired request",
            duration="FULL_DAY"
        )

        expired_schedule = WFHSchedule(
            request_id = 1,
            staff_id=self.staff.staff_id,
            manager_id=self.manager.staff_id,
            date=datetime.strptime(expired_date, "%Y-%m-%d").date() ,
            status="PENDING",
            dept="Finance",
            position="Finance Executive",
            duration="FULL_DAY"
            )

        db.session.add(expired_request)
        db.session.add(expired_schedule)
        db.session.commit()

        response = self.client.post("/api/reject-expired-request")
        resp_data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("Updated requests to 'EXPIRED'.", resp_data["message"])

    def test_reject_expired_request_exception(self):
        with patch('app.services.wfh_request_service.WFHRequestService.reject_expired', 
                side_effect=Exception("Database error")):
            response = self.client.post("/api/reject-expired-request")
            self.assertEqual(response.status_code, 500)
            self.assertIn("An error occurred", response.get_json()["message"])

    def test_check_wfh_count(self):
        data = {"staff_id": self.staff.staff_id, "date": self.future_date, "duration" : "FULL_DAY"}
        response = self.client.post(
            "/api/check-wfh-count",
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), "done")

    def test_check_wfh_count_exception(self):
        with patch('app.services.wfh_check_service.WFHCheckService.check_team_count', 
                side_effect=Exception("Check failed")):
            data = {
                "staff_id": self.staff.staff_id,
                "date": self.future_date,
                "duration": "FULL_DAY"
            }
            response = self.client.post(
                "/api/check-wfh-count",
                data=json.dumps(data),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 500)
            self.assertIn("An error occurred", response.get_json()["message"])


##For manager schedule related endpoints
    def test_manager_schedule_summary_no_subordinates(self):
        manager_id = 99  # Non-existent manager ID
        response = self.client.get(f'/api/manager-schedule-summary/{manager_id}')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {'dates': []})

    def test_manager_schedule_summary_no_schedules(self):
        manager_id = self.manager.staff_id  # Manager ID = 2
        response = self.client.get(f'/api/manager-schedule-summary/{manager_id}')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('dates', data)
        self.assertTrue(len(data['dates']) > 0)
        for date_data in data['dates']:
            self.assertEqual(date_data['total_staff'], 1)

    def test_manager_schedule_summary_with_schedules(self):
        manager_id = self.manager.staff_id
        today = datetime.now().date()
        schedule = WFHSchedule(
            request_id=1,
            staff_id=self.staff.staff_id,
            manager_id=manager_id,
            date=today,
            duration='FULL_DAY',
            status='APPROVED',
            dept=self.staff.dept,
            position=self.staff.position,
        )
        db.session.add(schedule)
        db.session.commit()
        response = self.client.get(f'/api/manager-schedule-summary/{manager_id}')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        date_str = today.isoformat()
        date_data = next((item for item in data['dates'] if item['date'] == date_str), None)
        self.assertIsNotNone(date_data)
        self.assertEqual(date_data['wfh_count_am'], 1)
        self.assertEqual(date_data['wfh_count_pm'], 1)
        self.assertEqual(date_data['office_count_am'], 0)
        self.assertEqual(date_data['office_count_pm'], 0)

    def test_manager_schedule_detail_no_subordinates(self):
        manager_id = 99  # Non-existent manager ID
        date_str = datetime.now().date().strftime('%Y-%m-%d')
        response = self.client.get(f'/api/manager-schedule-detail/{manager_id}/{date_str}')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {'date': date_str, 'staff': []})

    def test_manager_schedule_summary_with_end_date(self):
        end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        response = self.client.get(
            f'/api/manager-schedule-summary/{self.manager.staff_id}?end_date={end_date}'
        )
        self.assertEqual(response.status_code, 200)

    def test_manager_schedule_detail_no_schedules(self):
        manager_id = self.manager.staff_id
        date_str = datetime.now().date().strftime('%Y-%m-%d')
        response = self.client.get(f'/api/manager-schedule-detail/{manager_id}/{date_str}')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('staff', data)
        self.assertEqual(len(data['staff']), 1)
        staff_data = data['staff'][0]
        self.assertEqual(staff_data['staff_id'], self.staff.staff_id)
        self.assertEqual(staff_data['status_am'], 'OFFICE')
        self.assertEqual(staff_data['status_pm'], 'OFFICE')

    def test_manager_schedule_detail_with_schedules(self):
        manager_id = self.manager.staff_id
        date = datetime.now().date()
        date_str = date.strftime('%Y-%m-%d')
        schedule = WFHSchedule(
            request_id=1,
            staff_id=self.staff.staff_id,
            manager_id=manager_id,
            date=date,
            duration='HALF_DAY_PM',
            status='APPROVED',
            dept=self.staff.dept,
            position=self.staff.position,
        )
        db.session.add(schedule)
        db.session.commit()
        response = self.client.get(f'/api/manager-schedule-detail/{manager_id}/{date_str}')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        staff_data = data['staff'][0]
        self.assertEqual(staff_data['status_am'], 'OFFICE')
        self.assertEqual(staff_data['status_pm'], 'WFH')

    def test_manager_schedule_detail_invalid_date_format(self):
        manager_id = self.manager.staff_id
        invalid_date = 'invalid-date'
        response = self.client.get(f'/api/manager-schedule-detail/{manager_id}/{invalid_date}')
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn('message', data)
        self.assertIn('An error occurred', data['message'])

    def test_manager_schedule_summary_invalid_date_params(self):
        manager_id = self.manager.staff_id
        response = self.client.get(f'/api/manager-schedule-summary/{manager_id}?start_date=invalid&end_date=alsoinvalid')
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn('message', data)
        self.assertIn('An error occurred', data['message'])

    def test_personal_schedule_with_schedule(self):
        staff_id = self.staff.staff_id
        today = datetime.now().date()
        schedule = WFHSchedule(
            request_id=1,
            staff_id=staff_id,
            manager_id=self.manager.staff_id,
            date=today,
            duration='FULL_DAY',
            status='APPROVED',
            dept=self.staff.dept,
            position=self.staff.position,
        )
        db.session.add(schedule)
        db.session.commit()
        response = self.client.get(f'/api/personal-schedule/{staff_id}') 
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        date_str = today.isoformat()
        date_data = next((item for item in data['dates'] if item['date'] == date_str), None)
        self.assertIsNotNone(date_data)
        self.assertEqual(len(date_data), 2) 
        self.assertEqual(date_data["schedule"], "FullDay")

    def test_personal_schedule_with_no_schedule(self):
        staff_id = self.staff.staff_id
        response = self.client.get(f'/api/personal-schedule/{staff_id}') 
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(data['dates']) > 0)
        for date_data in data['dates']:
            self.assertEqual(len(date_data), 2) 
            self.assertEqual(date_data['schedule'], '')

    def test_personal_schedule_invalid_date_format(self):
        staff_id = self.staff.staff_id
        response = self.client.get(f'api/personal-schedule/{staff_id}?start_date=invalid&end_date=alsoinvalid')
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn('An error occurred', data['message'])

    def test_personal_schedule_with_end_date(self):
        end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        response = self.client.get(
            f'/api/personal-schedule/{self.staff.staff_id}?end_date={end_date}'
        )
        self.assertEqual(response.status_code, 200)

    def test_update_wfh_request_cancel(self):
        # Create a pending request
        wfh_request = WFHRequest(
            staff_id=self.staff.staff_id,
            manager_id=self.manager.staff_id,
            request_date=self.today,
            start_date=datetime.strptime(self.future_date, "%Y-%m-%d").date(),
            reason_for_applying="Pending request",
            duration="FULL_DAY",
        )
        db.session.add(wfh_request)
        db.session.commit()

        # Create associated schedule
        wfh_schedule = WFHSchedule(
            request_id=wfh_request.request_id,
            staff_id=self.staff.staff_id,
            manager_id=self.manager.staff_id,
            date=wfh_request.start_date,
            duration="FULL_DAY",
            status="PENDING",
            dept=self.staff.dept,
            position=self.staff.position
        )
        db.session.add(wfh_schedule)
        db.session.commit()

        data = {
            "request_id": wfh_request.request_id,
            "request_status": "CANCELLED",
            "reason": "",
        }
        response = self.client.patch(
            "/api/update-request",
            data=json.dumps(data),
            content_type="application/json",
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn("Successfully updated request", response.get_data(as_text=True))

        # Verify request status is updated
        updated_request = WFHRequest.query.get(wfh_request.request_id)
        self.assertEqual(updated_request.status, "CANCELLED")

        # Verify schedule status is updated
        updated_schedule = WFHSchedule.query.filter_by(request_id=wfh_request.request_id).first()
        self.assertEqual(updated_schedule.status, "CANCELLED")

    def test_create_withdraw_request_success(self):
        # Happy Path
        today = datetime.now().date()
        wfh_schedule = WFHSchedule(
            request_id=1,
            staff_id=self.staff.staff_id,
            manager_id=self.manager.staff_id,
            date=today,
            duration="FULL_DAY",
            status="APPROVED",
            dept=self.staff.dept,
            position=self.staff.position
        )
        db.session.add(wfh_schedule)
        db.session.commit()

        response = self.client.post(
        '/api/create-withdraw-request',
        json={  # Use json= instead of data=
            'schedule_id': 1,
            'reason': "I inputed wrongly"
        }
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"message": "SUCCESS"})
        new_request = WFHRequest.query.filter_by(staff_id=self.staff.staff_id, reason_for_applying="I inputed wrongly").first()
        self.assertEqual(new_request.duration, "WITHDRAWAL REQUEST") 

    def test_create_withdraw_request_non_existent_schedule(self):
        # Schedule does not exist
        response = self.client.post(
        '/api/create-withdraw-request',
        json={  # Use json= instead of data=
            'schedule_id': 1,
            'reason': "I inputed wrongly"
        }
        )
        
    
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"message": "Schedule does not exist"})
        

    def test_create_withdraw_request_out_of_date_range(self):
        # Schedule falls out of the required range of 2 weeks before and after
        test_date = "2024-10-13"
        start_date = datetime.strptime(test_date, "%Y-%m-%d").date()


        wfh_schedule = WFHSchedule(
            request_id=1,
            staff_id=self.staff.staff_id,
            manager_id=self.manager.staff_id,
            date=start_date,
            duration="FULL_DAY",
            status="APPROVED",
            dept=self.staff.dept,
            position=self.staff.position
        )
        db.session.add(wfh_schedule)
        db.session.commit()

        response = self.client.post(
        '/api/create-withdraw-request',
        json={  # Use json= instead of data=
            'schedule_id': 1,
            'reason': "I inputed wrongly"
        }
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"message": "Exceeded date range"})


    def test_create_withdraw_request_create_fail(self):
        # Use patch as a context manager to mock the create_request method
        with patch.object(WFHRequestService, 'create_request', side_effect=ValueError()):
            # Create a valid schedule in the database for the test
            today = datetime.now().date()
            wfh_schedule = WFHSchedule(
                request_id=1,
                staff_id=1,
                manager_id=2,
                date=today,
                duration="FULL_DAY",
                status="APPROVED",
                dept="Test Department",
                position="Test Position"
            )
            
            db.session.add(wfh_schedule)
            db.session.commit()

            # Make a POST request to create-withdraw-request
            response = self.client.post(
                '/api/create-withdraw-request',
                json={
                    'schedule_id': 1,
                    'reason': "I made an error"
                }
            )
            
            # Assert the response status code and message
            self.assertEqual(response.status_code, 500)

    def test_create_withdraw_request_boundary1(self):
        # a day before start accept
        start_date = datetime.today().date() - timedelta(days=15)

        wfh_schedule = WFHSchedule(
            request_id=1,
            staff_id=self.staff.staff_id,
            manager_id=self.manager.staff_id,
            date=start_date,
            duration="FULL_DAY",
            status="APPROVED",
            dept=self.staff.dept,
            position=self.staff.position
        )
        db.session.add(wfh_schedule)
        db.session.commit()

        response = self.client.post(
        '/api/create-withdraw-request',
        json={  # Use json= instead of data=
            'schedule_id': 1,
            'reason': "I inputed wrongly"
        }
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"message": "Exceeded date range"})
        
    def test_create_withdraw_request_boundary2(self):
        # the day start accept
        start_date = datetime.today().date() - timedelta(days=14)
        wfh_schedule = WFHSchedule(
            request_id=1,
            staff_id=self.staff.staff_id,
            manager_id=self.manager.staff_id,
            date=start_date,
            duration="FULL_DAY",
            status="APPROVED",
            dept=self.staff.dept,
            position=self.staff.position
        )
        db.session.add(wfh_schedule)
        db.session.commit()

        response = self.client.post(
        '/api/create-withdraw-request',
        json={  # Use json= instead of data=
            'schedule_id': 1,
            'reason': "I inputed wrongly"
        }
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"message": "SUCCESS"})

    def test_create_withdraw_request_boundary3(self):
        # the day last accept
        start_date = datetime.today().date() + timedelta(days=14)
        wfh_schedule = WFHSchedule(
            request_id=1,
            staff_id=self.staff.staff_id,
            manager_id=self.manager.staff_id,
            date=start_date,
            duration="FULL_DAY",
            status="APPROVED",
            dept=self.staff.dept,
            position=self.staff.position
        )
        db.session.add(wfh_schedule)
        db.session.commit()

        response = self.client.post(
        '/api/create-withdraw-request',
        json={  # Use json= instead of data=
            'schedule_id': 1,
            'reason': "I inputed wrongly"
        }
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"message": "SUCCESS"})

    def test_create_withdraw_request_boundary4(self):
        # the day after last accept
        start_date = datetime.today().date() + timedelta(days=15)
        wfh_schedule = WFHSchedule(
            request_id=1,
            staff_id=self.staff.staff_id,
            manager_id=self.manager.staff_id,
            date=start_date,
            duration="FULL_DAY",
            status="APPROVED",
            dept=self.staff.dept,
            position=self.staff.position
        )
        db.session.add(wfh_schedule)
        db.session.commit()

        response = self.client.post(
        '/api/create-withdraw-request',
        json={  # Use json= instead of data=
            'schedule_id': 1,
            'reason': "I inputed wrongly"
        }
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"message": "Exceeded date range"})

    def test_create_wfh_request_with_end_date(self):
        data = {
            "staff_id": self.staff.staff_id,
            "manager_id": self.manager.staff_id,
            "reason_for_applying": "Recurring WFH request",
            "date": self.future_date,
            "end_date": (datetime.strptime(self.future_date, "%Y-%m-%d") + timedelta(days=14)).strftime("%Y-%m-%d"),
            "duration": "FULL_DAY",
            "dept": self.staff.dept,
            "position": self.staff.position,
        }
        response = self.client.post(
            "/api/request", data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)

    def test_create_wfh_request_general_exception(self):
        with patch('app.services.wfh_request_service.WFHRequestService.create_request', 
                side_effect=Exception("Unexpected error")):
            data = {
                "staff_id": self.staff.staff_id,
                "manager_id": self.manager.staff_id,
                "reason_for_applying": "Test request",
                "date": self.future_date,
                "duration": "FULL_DAY",
                "dept": self.staff.dept,
                "position": self.staff.position,
            }
            response = self.client.post(
                "/api/request", data=json.dumps(data), content_type="application/json"
            )
            self.assertEqual(response.status_code, 500)
            self.assertIn("An error occurred", response.get_json()["message"])

    def test_update_wthdraw_request_success_approved(self):
    # happy path -> APPROVE WITHDRAWAL
        start_date = datetime.today().date() + timedelta(days=2)

        wfh_schedule = WFHSchedule(
            request_id=2,
            staff_id=self.staff.staff_id,
            manager_id=self.manager.staff_id,
            date=start_date,
            duration="FULL_DAY",
            status="APPROVED",
            dept=self.staff.dept,
            position=self.staff.position,
            reason_for_withdrawing=1
        )

        wfh_request = WFHRequest(
            staff_id=self.staff.staff_id,
            manager_id=self.manager.staff_id,
            request_date=self.today,
            start_date=start_date,
            reason_for_applying="I wana WFH",
            duration="FULL_DAY",
            status="APPROVED",
        )
        wfh_request_withdraw = WFHRequest(
            staff_id=self.staff.staff_id,
            manager_id=self.manager.staff_id,
            request_date=self.today,
            start_date=start_date,
            status="PENDING",
            reason_for_applying="wrong input!",
            duration="WITHDRAWAL REQUEST",
        )

        db.session.add(wfh_schedule)
        db.session.add(wfh_request)
        db.session.add(wfh_request_withdraw)
        db.session.commit()

        response = self.client.patch(
            '/api/update-request',
            json={
                'request_id': 2,
                'request_status': "APPROVED",
                'reason': ''
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(wfh_schedule.status, "WITHDRAWN")
        self.assertEqual(wfh_request.status, "WITHDRAWN")
        self.assertEqual(wfh_request_withdraw.status, "APPROVED")
        self.assertEqual(response.get_json(), "Successfully updated request 2 as WITHDRAWN")

    def test_update_wthdraw_request_success_rejected(self):
    # happy path -> APPROVE WITHDRAWAL
        start_date = datetime.today().date() + timedelta(days=2)

        wfh_schedule = WFHSchedule(
            request_id=2,
            staff_id=self.staff.staff_id,
            manager_id=self.manager.staff_id,
            date=start_date,
            duration="FULL_DAY",
            status="APPROVED",
            dept=self.staff.dept,
            position=self.staff.position,
            reason_for_withdrawing=1
        )

        wfh_request = WFHRequest(
            staff_id=self.staff.staff_id,
            manager_id=self.manager.staff_id,
            request_date=self.today,
            start_date=start_date,
            reason_for_applying="I wana WFH",
            duration="FULL_DAY",
            status="APPROVED",
        )
        wfh_request_withdraw = WFHRequest(
            staff_id=self.staff.staff_id,
            manager_id=self.manager.staff_id,
            request_date=self.today,
            start_date=start_date,
            status="PENDING",
            reason_for_applying="wrong input!",
            duration="WITHDRAWAL REQUEST",
        )

        db.session.add(wfh_schedule)
        db.session.add(wfh_request)
        db.session.add(wfh_request_withdraw)
        db.session.commit()

        response = self.client.patch(
            '/api/update-request',
            json={
                'request_id': 2,
                'request_status': "REJECTED",
                'reason': ''
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(wfh_schedule.status, "APPROVED")
        self.assertEqual(wfh_request.status, "APPROVED")
        self.assertEqual(wfh_request_withdraw.status, "REJECTED")
        self.assertEqual(response.get_json(), "Successfully updated request 2 as REJECTED")

    def test_update_wthdraw_request_fail_non_existent_request(self):
        # NEGATIVE TEST CASE - NO WITHDRAWAL REQUEST TO WITHDRAW
        response = self.client.patch(
        '/api/update-request',
        json={  # Use json= instead of data=
            'request_id': 1,
            'request_status': "REJECTED",
            'reason' : ''
        }
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json(), {"message": "Request does not exist"})

    def test_update_wthdraw_request_fail_non_existent_request(self):
        # NEGATIVE TEST CASE - NO WITHDRAWAL REQUEST TO WITHDRAW
        response = self.client.patch(
        '/api/update-request',
        json={  # Use json= instead of data=
            'request_id': 1,
            'request_status': "REJECTED",
            'reason' : ''
        }
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json(), {"message": "Request does not exist"})

    def test_update_wthdraw_request_fail_update_request_failed(self):
        # NEGATIVE TEST CASE - UPDATE REQUEST FAILED
        start_date = datetime.today().date() + timedelta(days=2)

        wfh_schedule = WFHSchedule(
            request_id=1,
            staff_id=self.staff.staff_id,
            manager_id=self.manager.staff_id,
            date=start_date,
            duration="FULL_DAY",
            status="APPROVED",
            dept=self.staff.dept,
            position=self.staff.position
        )

        wfh_request = WFHRequest(
            staff_id=self.staff.staff_id,
            manager_id=self.manager.staff_id,
            request_date=self.today,
            start_date=start_date,
            reason_for_applying="Applied wrongly",
            duration="WITHDRAWAL REQUEST",
        )

        db.session.add(wfh_schedule)
        db.session.add(wfh_request)
        db.session.commit()

        with patch.object(WFHRequestService, 'update_request', return_value = "False"):

            response = self.client.patch(
            '/api/update-request',
            json={  # Use json= instead of data=
                'request_id': 1,
                'request_status': "REJECTED",
                'reason' : ''
            }
            )

            self.assertEqual(response.status_code, 404)

    def test_update_wthdraw_request_fail_update_schedule_failed(self):
        # NEGATIVE TEST CASE - UPDATE SCHEDULE FAILED
        start_date = datetime.today().date() + timedelta(days=2)

        wfh_schedule = WFHSchedule(
            request_id=1,
            staff_id=self.staff.staff_id,
            manager_id=self.manager.staff_id,
            date=start_date,
            duration="FULL_DAY",
            status="APPROVED",
            dept=self.staff.dept,
            position=self.staff.position
        )

        wfh_request = WFHRequest(
            staff_id=self.staff.staff_id,
            manager_id=self.manager.staff_id,
            request_date=self.today,
            start_date=start_date,
            reason_for_applying="Applied wrongly",
            duration="WITHDRAWAL REQUEST",
        )

        db.session.add(wfh_schedule)
        db.session.add(wfh_request)
        db.session.commit()

        with patch.object(WFHScheduleService, 'update_schedule', return_value = "False"):

            response = self.client.patch(
            '/api/update-request',
            json={  # Use json= instead of data=
                'request_id': 1,
                'request_status': "REJECTED",
                'reason' : ''
            }
            )

            self.assertEqual(response.status_code, 404)

    def test_update_wthdraw_request_fail_update_schedule_failed(self):
    # Negative test case - update schedule failed
        start_date = datetime.today().date() + timedelta(days=2)

        # Create and add wfh_schedule
        wfh_schedule = WFHSchedule(
            request_id=2,
            staff_id=self.staff.staff_id,
            manager_id=self.manager.staff_id,
            date=start_date,
            duration="FULL_DAY",
            status="APPROVED",
            dept=self.staff.dept,
            position=self.staff.position,
            reason_for_withdrawing=1  # reference to the original request
        )
        
        # Create and add wfh_request and wfh_request_withdraw
        wfh_request = WFHRequest(
            staff_id=self.staff.staff_id,
            manager_id=self.manager.staff_id,
            request_date=self.today,
            start_date=start_date,
            reason_for_applying="I wana WFH",
            duration="FULL_DAY",
            status="APPROVED",
        )
        wfh_request_withdraw = WFHRequest(
            staff_id=self.staff.staff_id,
            manager_id=self.manager.staff_id,
            request_date=self.today,
            start_date=start_date,
            status="PENDING",
            reason_for_applying="wrong input!",
            duration="WITHDRAWAL REQUEST",
        )

        # Commit data to the database
        db.session.add(wfh_schedule)
        db.session.add(wfh_request)
        db.session.add(wfh_request_withdraw)
        db.session.commit()

        # Mock the method to simulate failure
        with patch.object(WFHScheduleService, 'orig_schedule_request_id', side_effect=Exception):
            # Make the patch request
            response = self.client.patch(
                '/api/update-request',
                json={
                    'request_id': 2,
                    'request_status': "REJECTED",
                    'reason': ''
                }
            )

            # Assert that a 404 status code is returned due to the failure
            self.assertEqual(response.status_code, 500)


    def test_staff_schedule_summary(self):
        response = self.client.get(
            f'/api/staff-schedule-summary/{self.manager.staff_id}?staff_id={self.staff.staff_id}'
        )
        self.assertEqual(response.status_code, 200)

    def test_staff_schedule_summary_with_dates(self):
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        response = self.client.get(
            f'/api/staff-schedule-summary/{self.manager.staff_id}?'
            f'start_date={start_date}&end_date={end_date}&staff_id={self.staff.staff_id}'
        )
        self.assertEqual(response.status_code, 200)

    def test_staff_schedule_summary_exception(self):
        with patch('app.services.wfh_schedule_service.WFHScheduleService.get_staff_schedule_summary', 
                side_effect=Exception("Database error")):
            response = self.client.get(
                f'/api/staff-schedule-summary/{self.manager.staff_id}?staff_id={self.staff.staff_id}'
            )
            self.assertEqual(response.status_code, 500)
            self.assertIn("An error occurred", response.get_json()["message"])

    def test_staff_schedule_detail_success(self):
        date = datetime.now().strftime('%Y-%m-%d')
        response = self.client.get(f'/api/staff-schedule-detail/{self.staff.staff_id}/{date}')
        self.assertEqual(response.status_code, 200)

    def test_staff_schedule_detail_exception(self):
        date = datetime.now().strftime('%Y-%m-%d')
        with patch('app.services.wfh_schedule_service.WFHScheduleService.get_staff_schedule_detail', 
                side_effect=Exception("Database error")):
            response = self.client.get(f'/api/staff-schedule-detail/{self.staff.staff_id}/{date}')
            self.assertEqual(response.status_code, 500)
            self.assertIn("An error occurred", response.get_json()["message"])

    def test_hr_schedule_summary(self):
        response = self.client.get('/api/hr-schedule-summary')
        self.assertEqual(response.status_code, 200)

    def test_hr_schedule_detail(self):
        date = datetime.now().strftime('%Y-%m-%d')
        response = self.client.get(f'/api/hr-schedule-detail/{date}')
        self.assertEqual(response.status_code, 200)

    def test_hr_schedule_detail_invalid_date(self):
        response = self.client.get('/api/hr-schedule-detail/invalid-date')
        self.assertEqual(response.status_code, 500)

    def test_hr_schedule_summary_with_dates(self):
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        response = self.client.get(
            f'/api/hr-schedule-summary?start_date={start_date}&end_date={end_date}'
        )
        self.assertEqual(response.status_code, 200)

    def test_hr_schedule_summary_exception(self):
        with patch('app.services.wfh_schedule_service.WFHScheduleService.get_hr_schedule_summary', 
                side_effect=Exception("Database error")):
            response = self.client.get('/api/hr-schedule-summary')
            self.assertEqual(response.status_code, 500)
            self.assertIn("An error occurred", response.get_json()["message"])

    def test_get_staff_requests(self):
        response = self.client.get(f'/api/staff-requests/{self.staff.staff_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn("staff_requests", response.get_json())

    def test_get_staff_requests_exception(self):
        with patch('app.services.wfh_request_service.WFHRequestService.get_staff_requests', 
                side_effect=Exception("Database error")):
            response = self.client.get(f'/api/staff-requests/{self.staff.staff_id}')
            self.assertEqual(response.status_code, 500)
            self.assertIn("An error occurred", response.get_json()["message"])

    def test_schedules_by_valid_request_id(self):
        today = datetime.now().date()
        wfh_schedule = WFHSchedule(
            request_id=1,
            staff_id=self.staff.staff_id,
            manager_id=self.manager.staff_id,
            date=today,
            duration="FULL_DAY",
            status="APPROVED",
            dept=self.staff.dept,
            position=self.staff.position
        )
        db.session.add(wfh_schedule)
        db.session.commit()

        response = self.client.get(f'/api/schedules-by-request-id/{wfh_schedule.request_id}')
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIn('schedules', response_data)
        self.assertIsInstance(response_data['schedules'], list) 

        if response_data['schedules']:
            schedule = response_data['schedules'][0]
            self.assertIn('schedule_id', schedule)
            self.assertIn('date', schedule)
            self.assertIn('duration', schedule)
            self.assertIn('status', schedule)

    def test_get_schedules_by_request_id_not_found(self):
        non_existent_request_id = '99999'  # Assuming this ID doesn't exist in the database
        
        # Mock the service to return None when querying for this ID
        with patch('app.services.wfh_schedule_service.WFHScheduleService.get_schedules_by_request_id', return_value=None):
            response = self.client.get(f'/api/schedules-by-request-id/{non_existent_request_id}')
            
            self.assertEqual(response.status_code, 404)
            data = response.get_json()
            self.assertIn('message', data)
            self.assertEqual(data['message'], 'Request not found')

    def test_get_schedules_by_request_id_invalid_format(self):
        invalid_request_id = 'abc'  # Not a digit, should trigger 400 error
        response = self.client.get(f'/api/schedules-by-request-id/{invalid_request_id}')
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Invalid request ID format')
   
    def test_get_schedules_by_request_id_server_error(self):
        invalid_request_id = 1  # Can be any valid ID
        with patch('app.services.wfh_schedule_service.WFHScheduleService.get_schedules_by_request_id', side_effect=Exception("Database error")):
            response = self.client.get(f'/api/schedules-by-request-id/{invalid_request_id}')
            
            self.assertEqual(response.status_code, 500)
            data = response.get_json()
            
            self.assertIn('message', data)
            self.assertEqual(data['message'], 'An error occurred: Database error')
    
    def test_get_schedules_by_request_id_no_schedules(self):
        valid_request_id = 2  # Ensure this ID has no associated schedules in the test database
        response = self.client.get(f'/api/schedules-by-request-id/{valid_request_id}')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertIn('schedules', data)
        self.assertIsInstance(data['schedules'], list)
        self.assertEqual(len(data['schedules']), 0)  # Check that the list is empty



    def test_check_withdrawal_success_with_withdrawal(self):
        request_id = 1
        mock_wfh_request = Mock(staff_id=1, start_date="2024-11-02")

        with patch('app.models.wfh_request.WFHRequest.query') as mock_query:
            with patch('app.services.wfh_request_service.WFHRequestService.check_withdrawal') as mock_check:
                # Setup the mocks
                mock_query.filter_by.return_value.first.return_value = mock_wfh_request
                mock_check.return_value = True

                # Make the request
                response = self.client.get(f'/api/check-withdrawal/{request_id}')
                data = response.get_json()

                # Assertions
                self.assertEqual(response.status_code, 200)
                self.assertTrue(data['withdrawn'])
                mock_check.assert_called_once_with(1, "2024-11-02")
    def test_check_withdrawal_success_without_withdrawal(self):
            request_id = 1
            mock_wfh_request = Mock(staff_id=1, start_date="2024-11-02")

            with patch('app.models.wfh_request.WFHRequest.query') as mock_query:
                with patch('app.services.wfh_request_service.WFHRequestService.check_withdrawal') as mock_check:
                    # Setup the mocks
                    mock_query.filter_by.return_value.first.return_value = mock_wfh_request
                    mock_check.return_value = False

                    # Make the request - Note the updated URL path
                    response = self.client.get(f'/api/check-withdrawal/{request_id}')
                    data = response.get_json()

                    # Assertions
                    self.assertEqual(response.status_code, 200)
                    self.assertFalse(data['withdrawn'])
                    mock_check.assert_called_once_with(1, "2024-11-02")

    def test_check_withdrawal_custom_schedule_date(self):
        request_id = 1
        mock_wfh_request = Mock(staff_id=1, start_date="2024-11-02")
        custom_date = "2024-11-03"

        with patch('app.models.wfh_request.WFHRequest.query') as mock_query:
            with patch('app.services.wfh_request_service.WFHRequestService.check_withdrawal') as mock_check:
                # Setup the mocks
                mock_query.filter_by.return_value.first.return_value = mock_wfh_request
                mock_check.return_value = True

                # Make the request - Note the updated URL path
                response = self.client.get(f'/api/check-withdrawal/{request_id}?schedule_date={custom_date}')
                data = response.get_json()

                # Assertions
                self.assertEqual(response.status_code, 200)
                self.assertTrue(data['withdrawn'])
                mock_check.assert_called_once_with(1, custom_date)

    def test_check_withdrawal_request_not_found(self):
        request_id = "INVALID_REQ"

        with patch('app.models.wfh_request.WFHRequest.query') as mock_query:
            # Setup the mock to return None
            mock_query.filter_by.return_value.first.return_value = None

            # Make the request - Note the updated URL path
            response = self.client.get(f'/api/check-withdrawal/{request_id}')
            data = response.get_json()

            # Assertions
            self.assertEqual(response.status_code, 404)
            self.assertEqual(data['message'], 'Request not found')

    def test_check_withdrawal_server_error(self):
        request_id = 1
        mock_wfh_request = Mock(staff_id=1, start_date="2024-11-02")

        with patch('app.models.wfh_request.WFHRequest.query') as mock_query:
            with patch('app.services.wfh_request_service.WFHRequestService.check_withdrawal', 
                    side_effect=Exception("Database error")) as mock_check:
                # Setup the mocks
                mock_query.filter_by.return_value.first.return_value = mock_wfh_request

                # Make the request - Note the updated URL path
                response = self.client.get(f'/api/check-withdrawal/{request_id}')
                data = response.get_json()

                # Assertions
                self.assertEqual(response.status_code, 500)
                self.assertIn('message', data)
                self.assertEqual(data['message'], 'An error occurred: Database error')

    def test_check_withdrawal_invalid_date_format(self):
        request_id = 1
        mock_wfh_request = Mock(staff_id=1, start_date="2024-11-02")
        invalid_date = "invalid-date"

        with patch('app.models.wfh_request.WFHRequest.query') as mock_query:
            with patch('app.services.wfh_request_service.WFHRequestService.check_withdrawal') as mock_check:
                # Setup the mocks
                mock_query.filter_by.return_value.first.return_value = mock_wfh_request
                mock_check.side_effect = ValueError("Invalid date format")

                # Make the request - Note the updated URL path
                response = self.client.get(f'/api/check-withdrawal/{request_id}?schedule_date={invalid_date}')
                data = response.get_json()

                # Assertions
                self.assertEqual(response.status_code, 400)
                self.assertIn('message', data)
                self.assertEqual(data['message'], 'Invalid date format')

    @patch('app.services.wfh_schedule_service.WFHScheduleService.get_schedules_by_ori_req_id')
    def test_get_schedules_by_ori_request_id_with_schedules(self, mock_get_schedules):
        request_id = 1
        # Mock response for schedules
        mock_data = {
            "schedules": [
                {
                    "duration": "8 hours",
                    "end_date": None,
                    "manager_id": 2,
                    "reason_for_applying": "Medical",
                    "reason_for_rejection": None,
                    "request_date": "2024-10-10",
                    "request_id": request_id,
                    "staff_id": 3,
                    "start_date": "2024-11-01",
                    "status": "approved"
                }
            ]
        }
        mock_get_schedules.return_value = mock_data
        
        # Act
        response = self.client.get(f'/api/schedules-by-ori-request-id/{request_id}')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data, mock_data)

    # # Test for valid request ID without schedules
    # @patch('app.services.wfh_schedule_service.WFHScheduleService.get_schedules_by_ori_req_id')
    # def test_get_schedules_by_ori_request_id_no_schedules(self, mock_get_schedules):
    #     request_id = 2
    #     mock_get_schedules.return_value = {"schedules": []}  # No schedules

    #     response = self.client.get(f'/api/schedules-by-ori-request-id/{request_id}')
        
    #     self.assertEqual(response.status_code, 404)


    # Test for invalid request ID (no records found)
    @patch('app.services.wfh_schedule_service.WFHScheduleService.get_schedules_by_ori_req_id')
    def test_get_schedules_by_ori_request_id_invalid_id(self, mock_get_schedules):
        request_id = 9999  # Assuming this ID doesn't exist
        mock_get_schedules.return_value = {"schedules": []}

        response = self.client.get(f'/api/schedules-by-ori-request-id/{request_id}')
        
        self.assertEqual(response.status_code, 404)


    # Test for server error
    @patch('app.services.wfh_schedule_service.WFHScheduleService.get_schedules_by_ori_req_id')
    def test_get_schedules_by_ori_request_id_server_error(self, mock_get_schedules):
        request_id = 1
        mock_get_schedules.side_effect = Exception("Database error")

        response = self.client.get(f'/api/schedules-by-ori-request-id/{request_id}')
        
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn('message', data)
        self.assertTrue("An error occurred: Database error" in data['message'])





if __name__ == "__main__":
    unittest.main()
