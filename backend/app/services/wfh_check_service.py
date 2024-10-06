from app import db
from app.models.staff import Staff
from app.models.wfh_schedule import WFHSchedule
from app.services.staff_service import StaffService

class WFHCheckService:
    @staticmethod
    def check_department_count(staff_id, date):
        # identify the staff department
        department = StaffService.get_staff_by_id(staff_id).dept

        # find out how many people in that department
        department_count = WFHCheckService.department_count(department)

        # now, find out how many people in that department also have approved WFH on that date
        applied_count = 0

        # get all the schedules with the same date and status 'APPROVED' or 'PENDING'
        schedules = db.session.query(WFHSchedule).filter(
            WFHSchedule.date == date,
            WFHSchedule.status == 'APPROVED')
        
        for schedule in schedules:
            # get the department of the schedule's staff
            schedule_staff = StaffService.get_staff_by_id(schedule.staff_id)
            schedule_department = schedule_staff.dept

            # if department is same as the one applying, increase counter
            if schedule_department == department:
                applied_count += 1

        # Calculate the percentage of staff working from home, if including this request
        wfh_percentage = (applied_count +1) / department_count

        # If more than 50% are working from home, return an error
        if wfh_percentage > 0.5:
            print(f"Max limit for Dept: {department} on date: {date}")
            return 'Unable to apply due to max limit'
        else:
            return 'Success'

    @staticmethod
    def department_count(department):
        staff_count = db.session.query(Staff).filter_by(dept=department).count()
        return staff_count
        
    

