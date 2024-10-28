from app import db
from app.models.wfh_request import WFHRequest
from app.models.wfh_schedule import WFHSchedule
from datetime import datetime, timedelta, date

class WFHRequestService:
    @staticmethod
    def create_request(staff_id, manager_id, request_date, start_date, end_date, reason_for_applying, duration):
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
        print(duration)
        if duration == "CANCEL REQUEST":
            existing_request = False

        if existing_request and (not end_date) and existing_request.status in ['APPROVED', 'PENDING']:
            
            raise ValueError("A request for this date already exists.")

        new_request = WFHRequest(
            staff_id=staff_id,
            manager_id=manager_id,
            request_date=request_date,
            start_date=start_date,
            end_date=end_date,
            reason_for_applying=reason_for_applying, duration=duration
        )
        db.session.add(new_request)
        db.session.commit()
        return new_request
    
    @staticmethod
    def get_pending_requests_for_manager(manager_id):
        return WFHRequest.query.filter_by(manager_id=manager_id, status='PENDING').all()
    

    @staticmethod
    def update_request(request_id, new_request_status, two_months_ago, reason):   #new_request_status = approved / rejected
        # Fetch the request by its ID
        request = WFHRequest.query.get(request_id)
        
        # Check if the request exists
        if request:

        # If status is CANCELLED, we don't need to check the date range
            if new_request_status == 'CANCELLED':
                request.status = new_request_status
                db.session.commit()
                return True
            # Check if within date range
            request_date = request.start_date
            if WFHRequestService.check_date(request_date , two_months_ago):

                # Update the status field
                request.status = new_request_status

                # provide reason for reject
                if new_request_status == 'REJECTED':
                    request.reason_for_rejection = reason

            # not within date range = not suppose to approve
            else:
                return "The date is invalid to be approved"
            
            # Commit the updated record to the database
            db.session.commit()

            # happy path 
            return True
        
        else:

            # Request does not exist
            return "Request Does not Exist!"
        
    @staticmethod
    def reject_expired(two_months_ago):
        # Fetch all requests from the database
        requests = WFHRequest.query.all()
        request_ids = []

        # Check each request
        for request in requests:

            # Check if date range is within 2 months and only update those that has not been updated expired
            if (WFHRequestService.check_date(request.start_date , two_months_ago) != True) and request.status == 'PENDING':
                request.status = 'EXPIRED'  # Update status to expired
                request.reason_for_rejection = "Past time period" 
                request_ids.append(request.request_id)

        # Commit the changes to the database
        db.session.commit()
        return request_ids
    

    @staticmethod
    def check_date(request_date , two_months_ago):
        if request_date > two_months_ago:
            return True
        else:
            return False
        
    @staticmethod
    def get_staff_requests(staff_id):
        return WFHRequest.query.filter_by(staff_id = staff_id).all()

