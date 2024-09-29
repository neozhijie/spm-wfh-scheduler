from app import db
from app.models.wfh_schedule import WFHSchedule
from app.models.wfh_request import WFHRequest
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
            
            if existing_schedule:
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
    def update_schedule(request_id):
        # Fetch the existing schedules based on the request_id
        schedules = WFHSchedule.query.filter_by(request_id=request_id).all()

        if not schedules:
            raise ValueError(f"No schedules found for request_id: {request_id}")
            return False
        else:
            for schedule in schedules:
                schedule.status = "APPROVED"

            # Commit the updated schedules to the database
            db.session.commit()
            print(f"Schedules for request_id {request_id} have been updated successfully.")

            return True
