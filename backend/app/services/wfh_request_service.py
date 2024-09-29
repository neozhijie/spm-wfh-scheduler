from app import db
from app.models.wfh_request import WFHRequest
from app.services.wfh_schedule_service import WFHScheduleService
from datetime import datetime, timedelta, date

class WFHRequestService:
    @staticmethod
    def create_request(staff_id, manager_id, request_date, start_date, end_date, reason_for_applying):
        error_message = None
        # Check if the start date is valid (within 2 months before or 3 months after today)
        max_valid_date = datetime.now().date() + timedelta(days=90)
        min_valid_date = datetime.now().date() - timedelta(days=60)
        if(not isinstance(start_date, date)):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()


        if start_date < min_valid_date or start_date > max_valid_date:
            raise ValueError("Start date must be between 2 months ago and 3 months from now.")
            

        # Check if the end date is valid for recurring requests
        
        if end_date:
            if(not isinstance(end_date, date)):
                print("try2")
                print(type(end_date))
                print(isinstance(end_date, date))
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
                print("try2")

            if end_date < min_valid_date or end_date > max_valid_date:
                raise ValueError("End date must be between 2 months ago and 3 months from now.")
            # print(type(end_date))
            # print(type(start_date))
            
            if start_date >= end_date:
                raise ValueError("End date must be after start date.")

        # Check if there's an existing request for the same day
        existing_request = WFHRequest.query.filter(
            WFHRequest.staff_id == staff_id,
            WFHRequest.start_date == start_date,
            WFHRequest.status != 'EXPIRED'
        ).first()

        if existing_request and (not end_date):
            raise ValueError("A request for this date already exists.")

        new_request = WFHRequest(
            staff_id=staff_id,
            manager_id=manager_id,
            request_date=request_date,
            start_date=start_date,
            end_date=end_date,
            reason_for_applying=reason_for_applying
        )
        db.session.add(new_request)
        db.session.commit()
        return new_request
    
    @staticmethod
    def get_pending_requests_for_manager(manager_id):
        return WFHRequest.query.filter_by(manager_id=manager_id, status='PENDING').all()
    
    @staticmethod
    def update_request(request_id, new_request_status, two_months_ago, reason=None):   # new_request_status = approved / rejected
        # Fetch the request by its ID
        request = WFHRequest.query.get(request_id)
        
        # Check if the request exists
        if request:
            # Check if the request is within the valid date range
            request_date = request.start_date
            if WFHRequestService.check_date(request_date, two_months_ago):
                
                # Update the status of the request
                request.status = new_request_status
                
                # If the request is rejected, store the reason
                if new_request_status == 'REJECTED':
                    request.reason_for_rejection = reason or "No reason provided"
                    db.session.commit()
                    return True
                
                # If the request is approved, update the associated schedule
                elif new_request_status == 'APPROVED':
                    schedules_updated = WFHScheduleService.update_schedule(request_id)
                    
                    # Check if schedules were successfully updated
                    if schedules_updated:

                        db.session.commit()  # Commit the updates
                        return True
                    else:
                        return f"Error occurred while updating schedules for request_id: {request_id}"
            
            else:
                # The request date is not within the valid date range
                return "The date is invalid to be approved"
        
        # If no request was found with the given request_id
        return "Request Does not Exist!"
    
    @staticmethod
    def reject_expired(two_months_ago):
        # Fetch all requests from the database
        requests = WFHRequest.query.all()
        updated_count = 0

        # Check each request
        for request in requests:

            # Check if date range is within 2 months and only update those that has not been updated
            if (WFHRequestService.check_date(request.start_date , two_months_ago) != True) and request.status!= 'REJECTED':
                request.status = 'REJECTED'  # Update status to rejected
                request.reason_for_rejection = "Rejected due to past time period" 
                updated_count += 1

        # Commit the changes to the database
        db.session.commit()
        return updated_count
    

    @staticmethod
    def check_date(request_date , two_months_ago):
        if request_date > two_months_ago:
            return True
        else:
            return False