import unittest
import json
from datetime import datetime, timedelta
from app import create_app, db
from config import TestConfig
from app.models.staff import Staff
from app.models.wfh_request import WFHRequest
from app.models.wfh_schedule import WFHSchedule
from unittest.mock import patch
from app.services.wfh_request_service import WFHRequestService



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

    def test_check_wfh_count(self):
        data = {"staff_id": self.staff.staff_id, "date": self.future_date, "duration" : "FULL_DAY"}
        response = self.client.post(
            "/api/check-wfh-count",
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), "done")


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

    def test_create_cancel_request_success(self):
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
        '/api/create-cancel-request',
        json={  # Use json= instead of data=
            'schedule_id': 1,
            'reason': "I inputed wrongly"
        }
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"message": "SUCCESS"})
        new_request = WFHRequest.query.filter_by(staff_id=self.staff.staff_id, reason_for_applying="I inputed wrongly").first()
        self.assertEqual(new_request.duration, "CANCEL REQUEST") 

    def test_create_cancel_request_non_existent_schedule(self):
        # Schedule does not exist
        response = self.client.post(
        '/api/create-cancel-request',
        json={  # Use json= instead of data=
            'schedule_id': 1,
            'reason': "I inputed wrongly"
        }
        )
        
    
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"message": "Schedule does not exist"})
        

    def test_create_cancel_request_out_of_date_range(self):
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
        '/api/create-cancel-request',
        json={  # Use json= instead of data=
            'schedule_id': 1,
            'reason': "I inputed wrongly"
        }
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"message": "Exceeded date range"})


    def test_create_cancel_request_create_fail(self):
        # Use patch as a context manager to mock the create_request method
        with patch.object(WFHRequestService, 'create_request', side_effect=ValueError("End date must be after start date.")):
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

            # Make a POST request to create-cancel-request
            response = self.client.post(
                '/api/create-cancel-request',
                json={
                    'schedule_id': 1,
                    'reason': "I made an error"
                }
            )
            
            # Assert the response status code and message
            self.assertEqual(response.status_code, 500)

    def test_create_cancel_request_boundary1(self):
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
        '/api/create-cancel-request',
        json={  # Use json= instead of data=
            'schedule_id': 1,
            'reason': "I inputed wrongly"
        }
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"message": "Exceeded date range"})
        
    def test_create_cancel_request_boundary2(self):
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
        '/api/create-cancel-request',
        json={  # Use json= instead of data=
            'schedule_id': 1,
            'reason': "I inputed wrongly"
        }
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"message": "SUCCESS"})

    def test_create_cancel_request_boundary3(self):
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
        '/api/create-cancel-request',
        json={  # Use json= instead of data=
            'schedule_id': 1,
            'reason': "I inputed wrongly"
        }
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"message": "SUCCESS"})

    def test_create_cancel_request_boundary4(self):
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
        '/api/create-cancel-request',
        json={  # Use json= instead of data=
            'schedule_id': 1,
            'reason': "I inputed wrongly"
        }
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"message": "Exceeded date range"})



if __name__ == "__main__":
    unittest.main()
