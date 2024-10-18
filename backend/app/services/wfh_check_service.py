from app import db
from app.models.staff import Staff
from app.models.wfh_schedule import WFHSchedule
from app.services.staff_service import StaffService

class WFHCheckService:
    @staticmethod
    def check_team_count(staff_id, date, duration):
        # identify the staff department
        manager_id = StaffService.get_staff_by_id(staff_id).reporting_manager
        
        # find out how many people in that department
        team_count = WFHCheckService.team_count(manager_id)
        
        # now, find out how many people in that department also have approved WFH on that date
        applied_count = 0

        # get all the schedules with the same date and status 'APPROVED' or 'PENDING'
        schedules = db.session.query(WFHSchedule).filter(
            WFHSchedule.date == date,
            WFHSchedule.status == 'APPROVED')
        
        for schedule in schedules:
            # get the department of the schedule's staff
            schedule_staff = StaffService.get_staff_by_id(schedule.staff_id)
            m_id = schedule_staff.reporting_manager

            # if department is same as the one applying, increase counter
            if m_id == manager_id:
                if schedule.duration == duration or schedule.duration == "FULL_DAY":
                    applied_count += 1

        # Calculate the percentage of staff working from home, if including this request
        wfh_percentage = (applied_count +1) / team_count
        # If more than 50% are working from home, return an error
        if wfh_percentage > 0.5:
            print(f"Max limit for Team under manager: {m_id} on date: {date}")
            return 'Unable to apply due to max limit'
        else:
            return 'Success'

    @staticmethod
    def team_count(m_id):
        staff_count = db.session.query(Staff).filter_by(reporting_manager = m_id).count()
        return staff_count
        
    

