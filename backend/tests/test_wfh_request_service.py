import unittest
from unittest.mock import patch, MagicMock
from app import db
from app.models.wfh_schedule import WFHSchedule
from app.models.wfh_request import WFHRequest
from datetime import date, timedelta
from app.services.wfh_schedule_service import WFHScheduleService


class WFHScheduleServiceTestCase(unittest.TestCase):

    @patch('app.services.wfh_schedule_service.WFHSchedule')
    @patch('app.services.wfh_schedule_service.db.session')
    def test_create_schedule_success(self, mock_db_session, mock_WFHSchedule):
        # Setup mock data
        request_id = 1
        staff_id = 101
        manager_id = 202
        start_date = date(2024, 10, 1)
        end_date = date(2024, 10, 29)
        duration = "full-day"
        dept = "Engineering"
        position = "Developer"

        # Mock no existing schedules
        mock_WFHSchedule.query.filter.return_value.first.return_value = None

        # Call the method
        schedules = WFHScheduleService.create_schedule(
            request_id, staff_id, manager_id, start_date, end_date, duration, dept, position
        )

        # Assertions
        self.assertEqual(len(schedules), 5)  # Should create 5 schedules (every 7 days in October)
        mock_db_session.add.assert_called()
        mock_db_session.commit.assert_called()
        self.assertEqual(schedules[0].date, start_date)

    @patch('app.services.wfh_schedule_service.WFHSchedule')
    @patch('app.services.wfh_schedule_service.db.session')
    def test_create_schedule_existing_schedule(self, mock_db_session, mock_WFHSchedule):
        # Setup mock data
        request_id = 1
        staff_id = 101
        manager_id = 202
        start_date = date(2024, 10, 1)
        end_date = date(2024, 10, 29)
        duration = "full-day"
        dept = "Engineering"
        position = "Developer"

        # Mock an existing schedule
        mock_WFHSchedule.query.filter.return_value.first.return_value = MagicMock()

        # Call the method
        schedules = WFHScheduleService.create_schedule(
            request_id, staff_id, manager_id, start_date, end_date, duration, dept, position
        )

        # Assertions
        self.assertEqual(len(schedules), 0)  # Should not create any schedules
        mock_db_session.commit.assert_not_called()  # No commit because no schedules created

    @patch('app.services.wfh_schedule_service.WFHSchedule')
    @patch('app.services.wfh_schedule_service.db.session')
    def test_create_schedule_no_schedules(self, mock_db_session, mock_WFHSchedule):
        # Setup mock data
        request_id = 1
        staff_id = 101
        manager_id = 202
        start_date = date(2024, 10, 1)
        end_date = None  # Single day scheduling
        duration = "half-day"
        dept = "Engineering"
        position = "Developer"

        # Mock an existing schedule
        mock_WFHSchedule.query.filter.return_value.first.return_value = None

        # Call the method
        with self.assertRaises(ValueError) as context:
            WFHScheduleService.create_schedule(
                request_id, staff_id, manager_id, start_date, end_date, duration, dept, position
            )

        # Assertions
        self.assertTrue("No schedules were created" in str(context.exception))
        mock_db_session.delete.assert_called_once_with(WFHRequest.query.get(request_id))

    @patch('app.services.wfh_schedule_service.WFHSchedule')
    @patch('app.services.wfh_schedule_service.db.session')
    def test_update_schedule_success(self, mock_db_session, mock_WFHSchedule):
        # Setup mock data
        request_id = 1
        mock_schedule = MagicMock()

        # Mock schedules found
        mock_WFHSchedule.query.filter_by.return_value.all.return_value = [mock_schedule]

        # Call the method
        result = WFHScheduleService.update_schedule(request_id)

        # Assertions
        self.assertTrue(result)
        self.assertEqual(mock_schedule.status, "APPROVED")
        mock_db_session.commit.assert_called_once()

    @patch('app.services.wfh_schedule_service.WFHSchedule')
    def test_update_schedule_no_schedules(self, mock_WFHSchedule):
        # Setup mock data
        request_id = 1

        # Mock no schedules found
        mock_WFHSchedule.query.filter_by.return_value.all.return_value = []

        # Call the method and check for exception
        with self.assertRaises(ValueError) as context:
            WFHScheduleService.update_schedule(request_id)

        # Assertions
        self.assertTrue(f"No schedules found for request_id: {request_id}" in str(context.exception))

# Run the tests
if __name__ == '__main__':
    unittest.main()
