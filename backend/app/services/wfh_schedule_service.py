from app import db
from app.models.wfh_schedule import WFHSchedule
from app.models.wfh_request import WFHRequest
from app.models.staff import Staff
from datetime import timedelta

class WFHScheduleService:
    @staticmethod
    def create_schedule(request_id, staff_id, manager_id, start_date, end_date, duration, dept, position):
        schedules = []
        current_date = start_date
        
        while True:

            existing_schedule = WFHSchedule.query.filter(
                WFHSchedule.staff_id == staff_id,
                WFHSchedule.date == current_date,
                WFHSchedule.status != 'EXPIRED'
            ).first()
            
            if existing_schedule and existing_schedule.status != 'REJECTED':
                print(f"Schedule for {current_date} already exists")
                current_date += timedelta(days=7)  # Move to the next week
                if end_date is None or current_date > end_date:
                    break  # If no end_date or we've passed the end_date, stop creating schedule
                continue

            new_schedule = WFHSchedule(
                request_id=request_id,
                staff_id=staff_id,
                manager_id=manager_id,
                date=current_date,
                duration=duration,
                dept=dept,
                position=position
            )
            db.session.add(new_schedule)
            schedules.append(new_schedule)
            print(f"Schedule for {current_date} created successfully")

            current_date += timedelta(days=7)  # Move to the next week
            if end_date is None or current_date > end_date:
                break  # If no end_date or we've passed the end_date, stop creating schedule
        
        if len(schedules) == 0:
            print("No schedules were created. Removing request from entry")
            db.session.delete(WFHRequest.query.get(request_id))
            db.session.commit()
            raise ValueError("No schedules were created")

        
        db.session.commit()
        return schedules
    
    @staticmethod
    def update_schedule(request_id, status):
        # Fetch the existing schedules based on the request_id
        schedules = WFHSchedule.query.filter_by(request_id=request_id).all()

        if not schedules:
            raise ValueError(f"No schedules found for request_id: {request_id}")


        for schedule in schedules:
            if status == "APPROVED":
                schedule.status = "APPROVED"
            elif status == "REJECTED":
                schedule.status = "REJECTED"

        # Commit the updated schedules to the database
        db.session.commit()
        print(f"Schedules for request_id {request_id} have been updated successfully.")

        return True
    
    @staticmethod
    def get_manager_schedule_summary(manager_id, start_date, end_date):
        staff_list = Staff.query.filter_by(reporting_manager=manager_id).all()
        staff_ids = [staff.staff_id for staff in staff_list]
        total_staff = len(staff_ids)
        if total_staff == 0:
            return {'dates': []}

        date_list = []
        current_date = start_date
        while current_date <= end_date:
            date_list.append(current_date)
            current_date += timedelta(days=1)

        dates_data = []
        for d in date_list:
            date_str = d.isoformat()

            # Initialize counts
            wfh_count_am = 0
            wfh_count_pm = 0

            # Get all approved schedules for the date
            schedules = WFHSchedule.query.filter(
                WFHSchedule.staff_id.in_(staff_ids),
                WFHSchedule.date == d,
                WFHSchedule.status == 'APPROVED'
            ).all()

            for sched in schedules:
                if sched.duration == 'FULL_DAY':
                    wfh_count_am += 1
                    wfh_count_pm += 1
                elif sched.duration == 'HALF_DAY_AM':
                    wfh_count_am += 1
                elif sched.duration == 'HALF_DAY_PM':
                    wfh_count_pm += 1

            office_count_am = total_staff - wfh_count_am
            office_count_pm = total_staff - wfh_count_pm

            dates_data.append({
                'date': date_str,
                'total_staff': total_staff,
                'wfh_count_am': wfh_count_am,
                'wfh_count_pm': wfh_count_pm,
                'office_count_am': office_count_am,
                'office_count_pm': office_count_pm
            })
        return {'dates': dates_data}

    @staticmethod
    def get_manager_schedule_detail(manager_id, date):
        staff_list = Staff.query.filter_by(reporting_manager=manager_id).all()
        staff_ids = [staff.staff_id for staff in staff_list]
        if not staff_ids:
            return {'date': date.isoformat(), 'staff': []}

        staff_status = {}
        for staff in staff_list:
            staff_status[staff.staff_id] = {
                'staff_id': staff.staff_id,
                'name': f"{staff.staff_fname} {staff.staff_lname}",
                'position': staff.position,
                'status_am': 'OFFICE',
                'status_pm': 'OFFICE'
            }
        print(staff_status)

        schedules = WFHSchedule.query.filter(
            WFHSchedule.staff_id.in_(staff_ids),
            WFHSchedule.date == date,
            WFHSchedule.status == 'APPROVED'
        ).all()

        for sched in schedules:
            if sched.duration == 'FULL_DAY':
                staff_status[sched.staff_id]['status_am'] = 'WFH'
                staff_status[sched.staff_id]['status_pm'] = 'WFH'
            elif sched.duration == 'HALF_DAY_AM':
                staff_status[sched.staff_id]['status_am'] = 'WFH'
                staff_status[sched.staff_id]['status_pm'] = 'OFFICE'
            elif sched.duration == 'HALF_DAY_PM':
                staff_status[sched.staff_id]['status_am'] = 'OFFICE'
                staff_status[sched.staff_id]['status_pm'] = 'WFH'

        staff_list_status = list(staff_status.values())

        return {
            'date': date.isoformat(),
            'staff': staff_list_status
        }
    
    @staticmethod
    def get_personal_schedule(staff_id, start_date, end_date):

        date_list = []
        current_date = start_date
        while current_date <= end_date:
            date_list.append(current_date)
            current_date += timedelta(days=1)

        dates_data = []

        for d in date_list:
            date_str = d.isoformat()
            schedule = ''


            # Get all approved schedules for the date
            schedules = WFHSchedule.query.filter(
                WFHSchedule.staff_id == staff_id,
                WFHSchedule.date == d,
                WFHSchedule.status.in_(['APPROVED', 'PENDING']) 
            ).all()

            for sched in schedules:
                if sched.duration == 'FULL_DAY' and sched.status == 'APPROVED':
                    schedule += 'FullDay'
                elif sched.duration == 'HALF_DAY_AM' and sched.status == 'APPROVED':
                    schedule += 'AM'
                elif sched.duration == 'HALF_DAY_PM' and sched.status == 'APPROVED':
                    schedule += 'PM'
                elif sched.duration == 'FULL_DAY' and sched.status == 'PENDING':
                    schedule += 'FullDayPending'
                elif sched.duration == 'HALF_DAY_AM' and sched.status == 'PENDING':
                    schedule += 'AMPending'
                elif sched.duration == 'HALF_DAY_PM' and sched.status == 'PENDING':
                    schedule += 'PMPending'


            dates_data.append({
                'date': date_str,
                'schedule': schedule,
            })
        return {'dates': dates_data}

    @staticmethod
    def get_staff_schedule_detail(staff_id, date):

        manager_id = Staff.query.filter_by(staff_id=staff_id).first().reporting_manager

        if manager_id:
            print(f"The manager in charge has ID: {manager_id}")

        else:
            manager_id = staff_id
            print(f"The manager in charge has ID: {manager_id}")
        
        
        staff_list = Staff.query.filter_by(reporting_manager=manager_id).all()
        staff_ids = [staff.staff_id for staff in staff_list]
        if not staff_ids:
            return {'date': date.isoformat(), 'staff': []}

        staff_status = {}
        for staff in staff_list:
            staff_status[staff.staff_id] = {
                'staff_id': staff.staff_id,
                'name': f"{staff.staff_fname} {staff.staff_lname}",
                'position': staff.position,
                'status_am': 'OFFICE',
                'status_pm': 'OFFICE'
            }
        print(staff_status)

        schedules = WFHSchedule.query.filter(
            WFHSchedule.staff_id.in_(staff_ids),
            WFHSchedule.date == date,
            WFHSchedule.status == 'APPROVED'
        ).all()

        for sched in schedules:
            if sched.duration == 'FULL_DAY':
                staff_status[sched.staff_id]['status_am'] = 'WFH'
                staff_status[sched.staff_id]['status_pm'] = 'WFH'
            elif sched.duration == 'HALF_DAY_AM':
                staff_status[sched.staff_id]['status_am'] = 'WFH'
                staff_status[sched.staff_id]['status_pm'] = 'OFFICE'
            elif sched.duration == 'HALF_DAY_PM':
                staff_status[sched.staff_id]['status_am'] = 'OFFICE'
                staff_status[sched.staff_id]['status_pm'] = 'WFH'

        staff_list_status = list(staff_status.values())

        return {
            'date': date.isoformat(),
            'staff': staff_list_status
        }


