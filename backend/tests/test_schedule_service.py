import unittest
from datetime import datetime, timedelta
from app import create_app, db
from config import TestConfig
from app.models.staff import Staff
from app.models.wfh_request import WFHRequest
from app.models.wfh_schedule import WFHSchedule
from app.services.wfh_schedule_service import WFHScheduleService


class WFHScheduleServiceTestCase(unittest.TestCase):
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

    def test_create_schedule_single_date(self):
        today = datetime.now().date()
        start_date = today + timedelta(days=5)
        wfh_request = WFHRequest(
            request_id=1,
            staff_id=self.staff3.staff_id,
            manager_id=self.staff2.staff_id,
            request_date=today,
            start_date=start_date,
            end_date=None,
            reason_for_applying="Test schedule",
        )
        db.session.add(wfh_request)
        db.session.commit()

        schedules = WFHScheduleService.create_schedule(
            request_id=wfh_request.request_id,
            staff_id=self.staff3.staff_id,
            manager_id=self.staff2.staff_id,
            start_date=start_date,
            end_date=None,
            duration="FULL_DAY",
            dept=self.staff3.dept,
            position=self.staff3.position,
        )
        self.assertEqual(len(schedules), 1)
        self.assertEqual(schedules[0].date, start_date)
        self.assertEqual(schedules[0].duration, "FULL_DAY")

    def test_create_schedule_recurring(self):
        today = datetime.now().date()
        start_date = today + timedelta(days=5)
        end_date = start_date + timedelta(days=21)  # 3 weeks
        wfh_request = WFHRequest(
            request_id=1,
            staff_id=self.staff3.staff_id,
            manager_id=self.staff2.staff_id,
            request_date=today,
            start_date=start_date,
            end_date=end_date,
            reason_for_applying="Test recurring schedule",
        )
        db.session.add(wfh_request)
        db.session.commit()

        schedules = WFHScheduleService.create_schedule(
            request_id=wfh_request.request_id,
            staff_id=self.staff3.staff_id,
            manager_id=self.staff2.staff_id,
            start_date=start_date,
            end_date=end_date,
            duration="FULL_DAY",
            dept=self.staff3.dept,
            position=self.staff3.position,
        )
        expected_dates = [start_date + timedelta(days=7 * i) for i in range(4)]
        self.assertEqual(len(schedules), len(expected_dates))
        schedule_dates = [schedule.date for schedule in schedules]
        self.assertEqual(schedule_dates, expected_dates)

    def test_create_schedule_existing_schedule(self):
        today = datetime.now().date()
        start_date = today + timedelta(days=5)
        wfh_request = WFHRequest(
            request_id=1,
            staff_id=self.staff3.staff_id,
            manager_id=self.staff2.staff_id,
            request_date=today,
            start_date=start_date,
            end_date=None,
            reason_for_applying="Test schedule",
        )
        db.session.add(wfh_request)
        db.session.commit()

        existing_schedule = WFHSchedule(
            request_id=wfh_request.request_id,
            staff_id=self.staff3.staff_id,
            manager_id=self.staff2.staff_id,
            date=start_date,
            duration="FULL_DAY",
            dept=self.staff3.dept,
            position=self.staff3.position,
        )
        db.session.add(existing_schedule)
        db.session.commit()

        with self.assertRaises(ValueError) as context:
            WFHScheduleService.create_schedule(
                request_id=wfh_request.request_id,
                staff_id=self.staff3.staff_id,
                manager_id=self.staff2.staff_id,
                start_date=start_date,
                end_date=None,
                duration="FULL_DAY",
                dept=self.staff3.dept,
                position=self.staff3.position,
            )
        self.assertEqual(str(context.exception), "No schedules were created")
        deleted_request = WFHRequest.query.get(wfh_request.request_id)
        self.assertIsNone(deleted_request)

    def test_create_schedule_no_schedules_created(self):
        today = datetime.now().date()
        start_date = today + timedelta(days=5)
        end_date = start_date + timedelta(days=21)  # 3 weeks
        wfh_request = WFHRequest(
            request_id=1,
            staff_id=self.staff3.staff_id,
            manager_id=self.staff2.staff_id,
            request_date=today,
            start_date=start_date,
            end_date=end_date,
            reason_for_applying="Test schedule",
        )
        db.session.add(wfh_request)
        db.session.commit()

        current_date = start_date
        while current_date <= end_date:
            existing_schedule = WFHSchedule(
                request_id=wfh_request.request_id,
                staff_id=self.staff3.staff_id,
                manager_id=self.staff2.staff_id,
                date=current_date,
                duration="FULL_DAY",
                dept=self.staff3.dept,
                position=self.staff3.position,
            )
            db.session.add(existing_schedule)
            current_date += timedelta(days=7)
        db.session.commit()

        with self.assertRaises(ValueError) as context:
            WFHScheduleService.create_schedule(
                request_id=wfh_request.request_id,
                staff_id=self.staff3.staff_id,
                manager_id=self.staff2.staff_id,
                start_date=start_date,
                end_date=end_date,
                duration="FULL_DAY",
                dept=self.staff3.dept,
                position=self.staff3.position,
            )
        self.assertEqual(str(context.exception), "No schedules were created")
        deleted_request = WFHRequest.query.get(wfh_request.request_id)
        self.assertIsNone(deleted_request)


if __name__ == "__main__":
    unittest.main()
