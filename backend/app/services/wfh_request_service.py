from app import db
from app.models.wfh_request import WFHRequest

class WFHRequestService:
    @staticmethod
    def create_request(staff_id, manager_id, request_date, start_date, end_date,reason_for_applying):
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
    def update_request(request_id, new_request_status, two_months_ago, reason):   #new_request_status = approved / rejected
        # Fetch the request by its ID
        request = WFHRequest.query.get(request_id)
        
        # Check if the request exists
        if request:
            
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