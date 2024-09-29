from app import db
from app.models.staff import Staff
from app.models.wfh_request import WFHRequest
from app.models.wfh_schedule import WFHSchedule
from app.services.staff_service import StaffService
class WFHCheckService:
    @staticmethod
    def check_department_count(staff_id, date):
        # identify the staff department
        department = StaffService.get_staff_by_id(staff_id).to_dict()['dept']
        print(department)
        # department = WFHCheckService.get_department(staff_id)

        # find out how many people in that department
        department_count = WFHCheckService.department_count(department)
        print("deparment count:" + str(department_count))

        # now, find out how many people in that department also applied for that date itself
        applied_count = 0

        # get all the rows of those with same date
        schedules = db.session.query(WFHSchedule).filter_by(date=date).all()
        schedule_dicts = [schedule.to_dict() for schedule in schedules]
        for schedule in schedule_dicts:
            schedule_staff_id = schedule['staff_id']
            schedule_department = StaffService.get_staff_by_id(schedule_staff_id).to_dict()['dept']
            if schedule_department == department:
                applied_count += 1
        print("applied count:" +str(applied_count))

        if ((department_count - applied_count) / department_count) < 0.5:
            print("too many lazy people")
            print(applied_count / department_count)
            return('1')
        else:
            print("ok")
            return('2')


    # @staticmethod
    # def get_department(staff_id):
    #     staff = db.session.query(Staff).filter_by(staff_id=staff_id).first()
    #     department = staff.dept
    #     return department

    @staticmethod
    def department_count(department):
        staff_count = db.session.query(Staff).filter_by(dept=department).count()
        return staff_count
        
    

