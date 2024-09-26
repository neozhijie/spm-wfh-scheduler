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