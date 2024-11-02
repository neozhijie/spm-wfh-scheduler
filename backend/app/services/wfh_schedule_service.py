from app import db
from app.models.wfh_schedule import WFHSchedule
from app.models.wfh_request import WFHRequest
from app.models.staff import Staff
from datetime import timedelta
from app.services.staff_service import StaffService

class WFHScheduleService:
    @staticmethod
    def create_schedule(request_id, staff_id, manager_id, start_date, end_date, duration, dept, position):
        schedules = []
        current_date = start_date

        while True:
            # Query all schedules for the current date
            existing_schedules = WFHSchedule.query.filter(
                WFHSchedule.staff_id == staff_id,
                WFHSchedule.date == current_date,
                WFHSchedule.status != 'EXPIRED'
            ).all()

            # Check if any of the existing schedules are 'APPROVED' or 'PENDING'
            if any(schedule.status in ['APPROVED', 'PENDING'] for schedule in existing_schedules):
                print(f"Schedule for {current_date} already exists")
                current_date += timedelta(days=7)  # Move to the next week
                if end_date is None or current_date > end_date:
                    break  # If no end_date or we've passed the end_date, stop creating schedule
                continue

            # Create a new schedule if no 'APPROVED' or 'PENDING' schedules exist
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
            if schedule.status == "PENDING":
                if status == "APPROVED":
                    schedule.status = "APPROVED"
                elif status == "REJECTED":
                    schedule.status = "REJECTED"
                elif status == "EXPIRED":
                    schedule.status = "EXPIRED"
                elif status == "CANCELLED":
                    schedule.status = "CANCELLED"
            elif status == "WITHDRAWN":
                schedule.status = "WITHDRAWN"

        # Commit the updated schedules to the database
        db.session.commit()
        print(f"Schedules for request_id {request_id} have been updated successfully.")

        return True

    @staticmethod
    def get_manager_schedule_summary(manager_id, start_date, end_date):
        try:
            # Get all subordinates based on manager's role
            subordinates_info = StaffService.get_all_subordinates(manager_id)

            if subordinates_info['type'] == 'none':
                return {'dates': []}

            date_list = []
            current_date = start_date
            while current_date <= end_date:
                date_list.append(current_date)
                current_date += timedelta(days=1)

            dates_data = []

            if subordinates_info['type'] == 'direct':
                staff_list = subordinates_info['staff']
                staff_ids = [staff.staff_id for staff in staff_list]
                total_staff = len(staff_ids)

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
            elif subordinates_info['type'] == 'manager':
                # Aggregate counts across all sub-managers, including the managers
                all_staff_ids = []
                total_staff = 0
                for manager, staffs in subordinates_info['managers'].items():
                    all_staff_ids.append(manager.staff_id)  # Include manager's own ID
                    total_staff += 1  # Count the manager
                    all_staff_ids.extend([staff.staff_id for staff in staffs])
                    total_staff += len(staffs)

                for d in date_list:
                    date_str = d.isoformat()

                    # Initialize counts
                    wfh_count_am = 0
                    wfh_count_pm = 0

                    # Get all approved schedules for the date
                    schedules = WFHSchedule.query.filter(
                        WFHSchedule.staff_id.in_(all_staff_ids),
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

        except Exception as e:
            print(f"Error in manager_schedule_summary: {str(e)}")
            return {'dates': []}

    @staticmethod
    def get_manager_schedule_detail(manager_id, date):
        try:
            # Get all subordinates based on manager's role
            subordinates_info = StaffService.get_all_subordinates(manager_id)

            if subordinates_info['type'] == 'none':
                return {'date': date.isoformat(), 'staff': []}

            if subordinates_info['type'] == 'direct':
                staff_list = subordinates_info['staff']
                staff_ids = [staff.staff_id for staff in staff_list]

                staff_status = {}
                for staff in staff_list:
                    staff_status[staff.staff_id] = {
                        'staff_id': staff.staff_id,
                        'name': f"{staff.staff_fname} {staff.staff_lname}",
                        'position': staff.position,
                        'status_am': 'OFFICE',
                        'status_pm': 'OFFICE'
                    }

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
                    elif sched.duration == 'HALF_DAY_PM':
                        staff_status[sched.staff_id]['status_pm'] = 'WFH'

                staff_list_status = list(staff_status.values())

                return {
                    'date': date.isoformat(),
                    'staff': staff_list_status
                }

            elif subordinates_info['type'] == 'manager':
                managers = subordinates_info['managers']
                result = {}

                for manager, staffs in managers.items():
                    # Include the manager in the staff list
                    staff_ids = [manager.staff_id] + [staff.staff_id for staff in staffs]

                    staff_status = {}

                    # For manager
                    staff_status[manager.staff_id] = {
                        'staff_id': manager.staff_id,
                        'name': f"{manager.staff_fname} {manager.staff_lname}",
                        'position': manager.position,
                        'status_am': 'OFFICE',
                        'status_pm': 'OFFICE'
                    }

                    # For staffs
                    for staff in staffs:
                        staff_status[staff.staff_id] = {
                            'staff_id': staff.staff_id,
                            'name': f"{staff.staff_fname} {staff.staff_lname}",
                            'position': staff.position,
                            'status_am': 'OFFICE',
                            'status_pm': 'OFFICE'
                        }

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
                        elif sched.duration == 'HALF_DAY_PM':
                            staff_status[sched.staff_id]['status_pm'] = 'WFH'

                    staff_list_status = list(staff_status.values())

                    result[manager.staff_fname + ' ' + manager.staff_lname + "'s Team"] = {
                        'manager_id': manager.staff_id,
                        'manager_name': f"{manager.staff_fname} {manager.staff_lname}",
                        'manager_position': manager.position,  # Include manager's position
                        'staff': staff_list_status
                    }

                return {
                    'date': date.isoformat(),
                    'managers': result
                }
        except Exception as e:
            print(f"Error in manager_schedule_detail: {str(e)}")
            return {'date': date.isoformat(), 'staff': []}

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

            # Get all approved and pending schedules for the date
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
    def get_staff_schedule_summary(manager_id, start_date, end_date,s_id):
        staff_list = Staff.query.filter_by(reporting_manager=manager_id).all()
        staff_ids = [staff.staff_id for staff in staff_list]
        total_staff = len(staff_ids) - 1
        if total_staff <= 0:
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
                if sched.staff_id != int(s_id):
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
    
    @staticmethod
    def get_hr_schedule_summary(start_date, end_date):
        staff_list = Staff.query.all()
        staff_ids = [staff.staff_id for staff in staff_list]
        total_staff = len(staff_ids)
        if total_staff <= 0:
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
    def get_hr_schedule_detail(date):
        staff_list = Staff.query.all()
        staff_ids = [staff.staff_id for staff in staff_list]
        total_staff = len(staff_ids)
        if total_staff <= 0:
            return {'date': date.isoformat(), 'staff': []}
        
        staff_status = {}
        for staff in staff_list:
            staff_status[staff.staff_id] = {
                'staff_id': staff.staff_id,
                'manager_id': staff.reporting_manager,
                'role': staff.role,
                'dept': staff.dept,
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
            elif sched.duration == 'HALF_DAY_PM':
                staff_status[sched.staff_id]['status_pm'] = 'WFH'

        staff_list_status = list(staff_status.values())

        return {
            'date': date.isoformat(),
            'staff': staff_list_status
        }

    @staticmethod
    def change_schedule_request_id(schedule_id, new_request_id):
        try:
            schedule = WFHSchedule.query.filter(
                WFHSchedule.schedule_id == schedule_id
            ).first()
            if schedule:
                orginal_request_id = schedule.request_id
                schedule.reason_for_withdrawing = orginal_request_id
                schedule.request_id = new_request_id
                db.session.commit()
                return schedule.request_id
            
        except Exception as e:
            print(f"Error in updating schedule request id")

    @staticmethod
    def orig_schedule_request_id(schedule_id):
        try:
            schedule = WFHSchedule.query.filter(
                WFHSchedule.schedule_id == schedule_id
            ).first()
            if schedule:
                orginal_request_id = schedule.reason_for_withdrawing
                schedule.request_id = orginal_request_id
                db.session.commit()
                return schedule.request_id
            
        except Exception as e:
            print(f"Error in updating schedule request id")
            
            
    @staticmethod
    def get_schedules_by_request_id(request_id):
        schedules = WFHSchedule.query.filter_by(request_id=request_id).all()

        schedule_list = [
            {
                'schedule_id': schedule.schedule_id,
                'date': schedule.date,
                'duration': schedule.duration,
                'status': schedule.status
            }
            for schedule in schedules
        ]
        return {'schedules': schedule_list}
    
    @staticmethod
    def get_schedules_by_ori_req_id(request_id):
        all_request_details = []
        schedules = WFHSchedule.query.filter_by(reason_for_withdrawing=int(request_id)).all()

        if schedules:
            for schedule in schedules:
                parent_request_id = schedule.reason_for_withdrawing
                parent_request = WFHRequest.query.filter_by(request_id=parent_request_id).first()
                if parent_request:
                    request_details = {
                        'duration': parent_request.duration,
                        'end_date': None,
                        'manager_id': parent_request.manager_id,
                        'reason_for_applying': parent_request.reason_for_applying,
                        'reason_for_rejection': parent_request.reason_for_rejection,
                        'request_date': parent_request.request_date,
                        'request_id': parent_request.request_id,
                        'staff_id': parent_request.staff_id,
                        'start_date': schedule.date,
                        'status': schedule.status
                    }
                    all_request_details.append(request_details)

        return {
            'schedules': all_request_details
        }
