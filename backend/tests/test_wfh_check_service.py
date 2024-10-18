import unittest
from datetime import datetime, timedelta
from app import create_app, db
from config import TestConfig
from app.models.staff import Staff
from app.models.wfh_schedule import WFHSchedule
from app.services.wfh_check_service import WFHCheckService


class WFHCheckServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        # Create departments
        self.reporting_manager = "Engineering"
        self.dept2 = "Human Resources"

        # Create staff members
        self.staff1 = Staff(
            staff_id=1,
            staff_fname="Alice",
            staff_lname="Engineer1",
            dept=self.reporting_manager,
            position="Engineer",
            country="CountryA",
            email="alice@company.com",
            reporting_manager=1,
            role=2,
            password="password1",
        )
        self.staff2 = Staff(
            staff_id=2,
            staff_fname="Bob",
            staff_lname="Engineer2",
            dept=self.reporting_manager,
            position="Engineer",
            country="CountryA",
            email="bob@company.com",
            reporting_manager=1,
            role=2,
            password="password2",
        )
        self.staff3 = Staff(
            staff_id=3,
            staff_fname="Charlie",
            staff_lname="HR",
            dept=self.dept2,
            position="HR Manager",
            country="CountryA",
            email="charlie@company.com",
            reporting_manager=2,
            role=2,
            password="password3",
        )

        db.session.add_all([self.staff1, self.staff2, self.staff3])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_team_count(self):
        count = WFHCheckService.team_count(self.staff1.reporting_manager)
        self.assertEqual(count, 2)

        count = WFHCheckService.team_count(self.staff3.reporting_manager)
        self.assertEqual(count, 1)

    def test_check_team_count_below_threshold(self):
        # No one is scheduled to WFH
        date = datetime.now().date()
        result = WFHCheckService.check_team_count(self.staff1.staff_id, date, "FULL_DAY")
        self.assertEqual(result, 'Success')  

    def test_check_team_count_above_threshold(self):
        # Schedule more than 50% staff to WFH
        date = datetime.now().date()

        # Schedule both staff1 and staff2
        schedule1 = WFHSchedule(
            request_id=1,
            staff_id=self.staff1.staff_id,
            manager_id=1,
            date=date,
            duration="FULL_DAY",
            status="APPROVED",
            dept=self.staff1.dept,
            position=self.staff1.position,
        )
        schedule2 = WFHSchedule(
            request_id=2,
            staff_id=self.staff2.staff_id,
            manager_id=1,
            date=date,
            duration="FULL_DAY",
            status="APPROVED",
            dept=self.staff2.dept,
            position=self.staff2.position,
        )
        db.session.add_all([schedule1, schedule2])
        db.session.commit()

        # Check for another staff in the same department
        result = WFHCheckService.check_team_count(self.staff1.staff_id, date, "FULL_DAY")
        self.assertEqual(result, 'Unable to apply due to max limit')

    def test_check_team_count_at_threshold(self):
        # Schedule 50% staff to WFH
        date = datetime.now().date()

        # Schedule only staff1
        schedule1 = WFHSchedule(
            request_id=1,
            staff_id=self.staff1.staff_id,
            manager_id=0,
            date=date,
            duration="FULL_DAY",
            dept=self.staff1.dept,
            position=self.staff1.position,
        )
        db.session.add(schedule1)
        db.session.commit()

        result = WFHCheckService.check_team_count(self.staff2.staff_id, date, "FULL_DAY")
        self.assertEqual(result, 'Success')

    def test_check_team_count_no_staff_in_team(self):
        # Remove staff from department
        Staff.query.filter_by(staff_id=self.staff1.staff_id).delete()
        Staff.query.filter_by(staff_id=self.staff2.staff_id).delete()
        db.session.commit()

        count = WFHCheckService.team_count(self.reporting_manager)
        self.assertEqual(count, 0)

        with self.assertRaises(ValueError) as context:
            WFHCheckService.check_team_count(
                self.staff1.staff_id, datetime.now().date(), "FULL_DAY"
            )
        self.assertEqual(str(context.exception), "No staff found with id: 1")

    def test_check_team_count_2_staff_in_dept(self):
        # Remove staff from department
     
        count = WFHCheckService.team_count(1)
        self.assertEqual(count, 2)



if __name__ == "__main__":
    unittest.main()
