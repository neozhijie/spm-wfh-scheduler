from app import db
from app.models.wfh_schedule import WFHSchedule
from datetime import timedelta

class WFHScheduleService:
    @staticmethod
    def create_schedule(request_id, start_date, end_date, duration):
        schedules = []
        current_date = start_date
        
        while True:
            new_schedule = WFHSchedule(
                request_id=request_id,
                date=current_date,
                duration=duration,
            )
            db.session.add(new_schedule)
            schedules.append(new_schedule)

            current_date += timedelta(days=7)  # Move to the next week
            if end_date is None or current_date >= end_date:
                break  # If no end_date or we've reached/passed the end_date, stop creating schedules
            
            
        
        db.session.commit()
        return schedules