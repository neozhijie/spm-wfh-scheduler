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
        staff4 = Staff(
            staff_id=4,
            staff_fname="Manager2",
            staff_lname="Test",
            dept="Test Department",
            position="Manager",
            country="Test Country",
            email="manager2@test.com",
            reporting_manager=staff1.staff_id,
            role=3,
            password="testpassword4",
        )
        staff5 = Staff(
            staff_id=5,
            staff_fname="Staff2",
            staff_lname="Test",
            dept="Test Department",
            position="Staff",
            country="Test Country",
            email="staff2@test.com",
            reporting_manager=staff4.staff_id,
            role=2,
            password="testpassword5",
        )
        db.session.add_all([staff1, staff2, staff3, staff4, staff5])
        db.session.commit()

        self.staff1 = staff1
        self.staff2 = staff2
        self.staff3 = staff3
        self.staff4 = staff4
        self.staff5 = staff5

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
            duration="FULL_DAY",
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
            duration="FULL_DAY",
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
            duration="FULL_DAY",
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
            duration="FULL_DAY",
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
    


    ############## LIST OF TEST FOR UPDATE_SCHEDULE ##############
    def test_update_schedule_single_date(self):
        today = datetime.now().date()
        start_date = today + timedelta(days=5)
        existing_schedule = WFHSchedule(
            request_id= 1,
            staff_id=self.staff3.staff_id,
            manager_id=self.staff2.staff_id,
            date= start_date,
            duration="FULL_DAY",
            dept=self.staff3.dept,
            position=self.staff3.position,
        )
        db.session.add(existing_schedule)
        db.session.commit()

        updated_schedule = WFHScheduleService.update_schedule(
            request_id=1, status="APPROVED"
        )

        self.assertEqual(updated_schedule, True)
        self.assertEqual(existing_schedule.status, "APPROVED")
    
    def test_update_schedule_rejected(self):
        today = datetime.now().date()
        start_date = today + timedelta(days=5)
        existing_schedule = WFHSchedule(
            request_id= 1,
            staff_id=self.staff3.staff_id,
            manager_id=self.staff2.staff_id,
            date= start_date,
            duration="FULL_DAY",
            dept=self.staff3.dept,
            position=self.staff3.position,
        )
        db.session.add(existing_schedule)
        db.session.commit()

        updated_schedule = WFHScheduleService.update_schedule(
            request_id=1, status="REJECTED"
        )

        self.assertEqual(updated_schedule, True)
        self.assertEqual(existing_schedule.status, "REJECTED")
        

    def test_update_schedule_recurring(self):
        today = datetime.now().date()

        for i in range(3):
            start_date = today + timedelta(days=5)
            existing_schedule1 = WFHSchedule(
            request_id= 1,
            staff_id=self.staff3.staff_id,
            manager_id=self.staff2.staff_id,
            date= start_date,
            duration="FULL_DAY",
            dept=self.staff3.dept,
            position=self.staff3.position,
        )
        existing_schedule2 = WFHSchedule(
            request_id= 1,
            staff_id=self.staff3.staff_id,
            manager_id=self.staff2.staff_id,
            date= start_date + timedelta(days=7),
            duration="FULL_DAY",
            dept=self.staff3.dept,
            position=self.staff3.position,
        )
        existing_schedule3 = WFHSchedule(
            request_id= 1,
            staff_id=self.staff3.staff_id,
            manager_id=self.staff2.staff_id,
            date= start_date + + timedelta(days=14),
            duration="FULL_DAY",
            dept=self.staff3.dept,
            position=self.staff3.position,
        )
        db.session.add_all([existing_schedule1, existing_schedule2, existing_schedule3])
        db.session.commit()

        updated_schedule = WFHScheduleService.update_schedule(
            request_id=1, status="APPROVED")

        self.assertEqual(updated_schedule, True)
        self.assertEqual(existing_schedule1.status, "APPROVED")
        self.assertEqual(existing_schedule2.status, "APPROVED")
        self.assertEqual(existing_schedule3.status, "APPROVED")

    def test_update_schedule_schedule_not_exist(self):
        with self.assertRaises(ValueError) as context:
            WFHScheduleService.update_schedule(request_id=1, status="APPROVED")
    
        # Check if the error message is as expected
        self.assertEqual(str(context.exception), "No schedules found for request_id: 1")

    def test_get_manager_schedule_summary_no_subordinates(self):
        # Manager with no subordinates
        manager_id = 99  # Non-existent manager ID
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=5)
        result = WFHScheduleService.get_manager_schedule_summary(manager_id, start_date, end_date)
        self.assertEqual(result, {'dates': []})

    def test_get_manager_schedule_summary_no_schedules(self):
        # Manager with subordinates but no schedules in the given date range
        manager_id = self.staff2.staff_id  # Manager ID = 2
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=5)
        result = WFHScheduleService.get_manager_schedule_summary(manager_id, start_date, end_date)
        self.assertEqual(len(result['dates']), 6)  # Including start_date and end_date
        for date_data in result['dates']:
            self.assertEqual(date_data['total_staff'], 1)  # Only staff3 is subordinate
            self.assertEqual(date_data['wfh_count_am'], 0)
            self.assertEqual(date_data['wfh_count_pm'], 0)
            self.assertEqual(date_data['office_count_am'], 1)
            self.assertEqual(date_data['office_count_pm'], 1)

    def test_get_manager_schedule_summary_with_schedules(self):
        # Create approved schedules for staff3
        manager_id = self.staff2.staff_id
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=5)
        # Create schedules with different durations
        schedule1 = WFHSchedule(
            request_id=1,
            staff_id=self.staff3.staff_id,
            manager_id=manager_id,
            date=start_date,
            duration='FULL_DAY',
            status='APPROVED',
            dept=self.staff3.dept,
            position=self.staff3.position,
        )
        schedule2 = WFHSchedule(
            request_id=2,
            staff_id=self.staff3.staff_id,
            manager_id=manager_id,
            date=start_date + timedelta(days=2),
            duration='HALF_DAY_AM',
            status='APPROVED',
            dept=self.staff3.dept,
            position=self.staff3.position,
        )
        schedule3 = WFHSchedule(
            request_id=3,
            staff_id=self.staff3.staff_id,
            manager_id=manager_id,
            date=start_date + timedelta(days=4),
            duration='HALF_DAY_PM',
            status='APPROVED',
            dept=self.staff3.dept,
            position=self.staff3.position,
        )
        db.session.add_all([schedule1, schedule2, schedule3])
        db.session.commit()
        result = WFHScheduleService.get_manager_schedule_summary(manager_id, start_date, end_date)
        self.assertEqual(len(result['dates']), 6)
        for date_data in result['dates']:
            date = datetime.strptime(date_data['date'], '%Y-%m-%d').date()
            if date == start_date:
                self.assertEqual(date_data['wfh_count_am'], 1)
                self.assertEqual(date_data['wfh_count_pm'], 1)
            elif date == start_date + timedelta(days=2):
                self.assertEqual(date_data['wfh_count_am'], 1)
                self.assertEqual(date_data['wfh_count_pm'], 0)
            elif date == start_date + timedelta(days=4):
                self.assertEqual(date_data['wfh_count_am'], 0)
                self.assertEqual(date_data['wfh_count_pm'], 1)
            else:
                self.assertEqual(date_data['wfh_count_am'], 0)
                self.assertEqual(date_data['wfh_count_pm'], 0)

    def test_get_manager_schedule_detail_no_subordinates(self):
        manager_id = 99  # Non-existent manager ID
        date = datetime.now().date()
        result = WFHScheduleService.get_manager_schedule_detail(manager_id, date)
        self.assertEqual(result, {'date': date.isoformat(), 'staff': []})

    def test_get_manager_schedule_detail_no_schedules(self):
        manager_id = self.staff2.staff_id
        date = datetime.now().date()
        result = WFHScheduleService.get_manager_schedule_detail(manager_id, date)
        self.assertEqual(len(result['staff']), 1)
        staff_data = result['staff'][0]
        self.assertEqual(staff_data['staff_id'], self.staff3.staff_id)
        self.assertEqual(staff_data['status_am'], 'OFFICE')
        self.assertEqual(staff_data['status_pm'], 'OFFICE')

    def test_get_manager_schedule_detail_with_schedules(self):
        manager_id = self.staff2.staff_id
        date = datetime.now().date()
        # Create a schedule with 'FULL_DAY' duration
        schedule = WFHSchedule(
            request_id=1,
            staff_id=self.staff3.staff_id,
            manager_id=manager_id,
            date=date,
            duration='FULL_DAY',
            status='APPROVED',
            dept=self.staff3.dept,
            position=self.staff3.position,
        )
        db.session.add(schedule)
        db.session.commit()
        result = WFHScheduleService.get_manager_schedule_detail(manager_id, date)
        staff_data = result['staff'][0]
        self.assertEqual(staff_data['status_am'], 'WFH')
        self.assertEqual(staff_data['status_pm'], 'WFH')

    def test_get_manager_schedule_detail_with_half_day_am(self):
        manager_id = self.staff2.staff_id
        date = datetime.now().date()
        # Create a schedule with 'HALF_DAY_AM' duration
        schedule = WFHSchedule(
            request_id=2,
            staff_id=self.staff3.staff_id,
            manager_id=manager_id,
            date=date,
            duration='HALF_DAY_AM',
            status='APPROVED',
            dept=self.staff3.dept,
            position=self.staff3.position,
        )
        db.session.add(schedule)
        db.session.commit()
        result = WFHScheduleService.get_manager_schedule_detail(manager_id, date)
        staff_data = result['staff'][0]
        self.assertEqual(staff_data['status_am'], 'WFH')
        self.assertEqual(staff_data['status_pm'], 'OFFICE')

    def test_get_manager_schedule_detail_with_half_day_pm(self):
        manager_id = self.staff2.staff_id
        date = datetime.now().date()
        # Create a schedule with 'HALF_DAY_PM' duration
        schedule = WFHSchedule(
            request_id=3,
            staff_id=self.staff3.staff_id,
            manager_id=manager_id,
            date=date,
            duration='HALF_DAY_PM',
            status='APPROVED',
            dept=self.staff3.dept,
            position=self.staff3.position,
        )
        db.session.add(schedule)
        db.session.commit()
        result = WFHScheduleService.get_manager_schedule_detail(manager_id, date)
        staff_data = result['staff'][0]
        self.assertEqual(staff_data['status_am'], 'OFFICE')
        self.assertEqual(staff_data['status_pm'], 'WFH')

    def test_get_personal_schedule_with_schedule(self):
        today = datetime.now().date()
        start_date = today + timedelta(days=5)
        end_date = start_date + timedelta(days=1) 
        staff_id=self.staff3.staff_id

        schedule1 = WFHSchedule(
            request_id=1,
            staff_id=staff_id,
            manager_id=self.staff2.staff_id,
            date=start_date,
            duration="FULL_DAY",
            status="APPROVED",
            dept=self.staff3.dept,
            position=self.staff3.position,
        )
        schedule2 = WFHSchedule(
            request_id=2,
            staff_id=staff_id,
            manager_id=self.staff2.staff_id,
            date=start_date + timedelta(days=1),
            duration="HALF_DAY_AM",
            status="PENDING",
            dept=self.staff3.dept,
            position=self.staff3.position,
        )
        db.session.add_all([schedule1, schedule2])
        db.session.commit()
        result = WFHScheduleService.get_personal_schedule(staff_id, start_date, end_date)
        expected_result = {
            'dates': [
                {'date': start_date.isoformat(), 'schedule': 'FullDay'},
                {'date': (start_date + timedelta(days=1)).isoformat(), 'schedule': 'AMPending'},
            ]
        }
        self.assertEqual(result, expected_result)

    def test_get_personal_schedule_with_no_schedule(self):
        today = datetime.now().date()
        start_date = today + timedelta(days=5)
        end_date = start_date + timedelta(days=1) 
        staff_id=self.staff3.staff_id
        result = WFHScheduleService.get_personal_schedule(staff_id, start_date, end_date)
        expected_result = {
            'dates': [
                {'date': start_date.isoformat(), 'schedule': ''},
                {'date': (start_date + timedelta(days=1)).isoformat(), 'schedule': ''},
            ]
        }
        self.assertEqual(result, expected_result)

    def test_get_staff_schedule_summary_no_subordinates(self):
        manager_id = 99  # Non-existent manager ID
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=5)
        result = WFHScheduleService.get_staff_schedule_summary(manager_id, start_date, end_date)
        self.assertEqual(result, {'dates': []})

    def test_get_staff_schedule_summary_with_schedules(self):
        manager_id = self.staff2.staff_id
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=5)

        # Create approved schedules for the staff
        schedule1 = WFHSchedule(
            request_id=1,
            staff_id=self.staff3.staff_id,
            manager_id=manager_id,
            date=start_date,
            duration='FULL_DAY',
            status='APPROVED',
            dept=self.staff3.dept,
            position=self.staff3.position,
        )
        schedule2 = WFHSchedule(
            request_id=2,
            staff_id=self.staff3.staff_id,
            manager_id=manager_id,
            date=start_date + timedelta(days=2),
            duration='HALF_DAY_AM',
            status='APPROVED',
            dept=self.staff3.dept,
            position=self.staff3.position,
        )
        schedule3 = WFHSchedule(
            request_id=3,
            staff_id=self.staff3.staff_id,
            manager_id=manager_id,
            date=start_date + timedelta(days=4),
            duration='HALF_DAY_PM',
            status='APPROVED',
            dept=self.staff3.dept,
            position=self.staff3.position,
        )
        db.session.add_all([schedule1, schedule2, schedule3])
        db.session.commit()

        result = WFHScheduleService.get_staff_schedule_summary(manager_id, start_date, end_date)
        self.assertEqual(len(result['dates']), 6)

        for date_data in result['dates']:
            date = datetime.strptime(date_data['date'], '%Y-%m-%d').date()
            if date == start_date:
                self.assertEqual(date_data['wfh_count_am'], 1)
                self.assertEqual(date_data['wfh_count_pm'], 1)
            elif date == start_date + timedelta(days=2):
                self.assertEqual(date_data['wfh_count_am'], 1)
                self.assertEqual(date_data['wfh_count_pm'], 0)
            elif date == start_date + timedelta(days=4):
                self.assertEqual(date_data['wfh_count_am'], 0)
                self.assertEqual(date_data['wfh_count_pm'], 1)
            else:
                self.assertEqual(date_data['wfh_count_am'], 0)
                self.assertEqual(date_data['wfh_count_pm'], 0)

    def test_get_manager_schedule_summary_director_with_managers_subordinates(self):
        manager_id = self.staff1.staff_id  # Director
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=5)

        # Create approved schedules for staff3 and staff5
        schedule1 = WFHSchedule(
            request_id=1,
            staff_id=self.staff3.staff_id,
            manager_id=self.staff2.staff_id,
            date=start_date,
            duration='FULL_DAY',
            status='APPROVED',
            dept=self.staff3.dept,
            position=self.staff3.position,
        )
        schedule2 = WFHSchedule(
            request_id=2,
            staff_id=self.staff5.staff_id,
            manager_id=self.staff4.staff_id,
            date=start_date + timedelta(days=2),
            duration='HALF_DAY_AM',
            status='APPROVED',
            dept=self.staff5.dept,
            position=self.staff5.position,
        )
        db.session.add_all([schedule1, schedule2])
        db.session.commit()

        result = WFHScheduleService.get_manager_schedule_summary(manager_id, start_date, end_date)
        self.assertEqual(len(result['dates']), 6)
        for date_data in result['dates']:
            date = datetime.strptime(date_data['date'], '%Y-%m-%d').date()
            if date == start_date:
                self.assertEqual(date_data['wfh_count_am'], 1)
                self.assertEqual(date_data['wfh_count_pm'], 1)
            elif date == start_date + timedelta(days=2):
                self.assertEqual(date_data['wfh_count_am'], 1)
                self.assertEqual(date_data['wfh_count_pm'], 0)
            else:
                self.assertEqual(date_data['wfh_count_am'], 0)
                self.assertEqual(date_data['wfh_count_pm'], 0)
            self.assertEqual(date_data['total_staff'], 4)

    def test_get_manager_schedule_summary_director_with_direct_subordinates(self):
        # Adding a direct subordinate to the director
        staff6 = Staff(
            staff_id=6,
            staff_fname="DirectStaff",
            staff_lname="UnderDirector",
            dept="Test Department",
            position="Staff",
            country="Test Country",
            email="directstaff@test.com",
            reporting_manager=self.staff1.staff_id,
            role=2,
            password="testpassword6",
        )
        db.session.add(staff6)
        db.session.commit()

        manager_id = self.staff1.staff_id  # Director
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=5)

        # Create approved schedules for direct staff
        schedule = WFHSchedule(
            request_id=3,
            staff_id=staff6.staff_id,
            manager_id=manager_id,
            date=start_date,
            duration='FULL_DAY',
            status='APPROVED',
            dept=staff6.dept,
            position=staff6.position,
        )
        db.session.add(schedule)
        db.session.commit()

        result = WFHScheduleService.get_manager_schedule_summary(manager_id, start_date, end_date)
        self.assertEqual(len(result['dates']), 6)
        for date_data in result['dates']:
            date = datetime.strptime(date_data['date'], '%Y-%m-%d').date()
            if date == start_date:
                self.assertEqual(date_data['wfh_count_am'], 1)
                self.assertEqual(date_data['wfh_count_pm'], 1)
            else:
                self.assertEqual(date_data['wfh_count_am'], 0)
                self.assertEqual(date_data['wfh_count_pm'], 0)
            self.assertEqual(date_data['total_staff'], 1)

    def test_get_manager_schedule_summary_manager_with_subordinates(self):
        manager_id = self.staff2.staff_id
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=5)

        result = WFHScheduleService.get_manager_schedule_summary(manager_id, start_date, end_date)
        self.assertEqual(len(result['dates']), 6)
        for date_data in result['dates']:
            self.assertEqual(date_data['total_staff'], 1)
            self.assertEqual(date_data['wfh_count_am'], 0)
            self.assertEqual(date_data['wfh_count_pm'], 0)
            self.assertEqual(date_data['office_count_am'], 1)
            self.assertEqual(date_data['office_count_pm'], 1)

    def test_get_manager_schedule_summary_manager_with_no_subordinates(self):
        staff7 = Staff(
            staff_id=7,
            staff_fname="ManagerNoSubs",
            staff_lname="NoSubs",
            dept="Test Department",
            position="Manager",
            country="Test Country",
            email="manager.nosubs@test.com",
            reporting_manager=self.staff1.staff_id,
            role=3,
            password="testpassword7",
        )
        db.session.add(staff7)
        db.session.commit()

        manager_id = staff7.staff_id
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=2)

        result = WFHScheduleService.get_manager_schedule_summary(manager_id, start_date, end_date)
        self.assertEqual(len(result['dates']), 3)
        for date_data in result['dates']:
            self.assertEqual(date_data['total_staff'], 0)
            self.assertEqual(date_data['wfh_count_am'], 0)
            self.assertEqual(date_data['wfh_count_pm'], 0)
            self.assertEqual(date_data['office_count_am'], 0)
            self.assertEqual(date_data['office_count_pm'], 0)

if __name__ == "__main__":
    unittest.main()
