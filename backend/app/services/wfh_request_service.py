from app import db
from app.models.wfh_request import WFHRequest
from datetime import date

class WFHRequestService:
    @staticmethod
    def create_request(staff_id, manager_id, request_date, reason_for_applying):
        new_request = WFHRequest(
            staff_id=staff_id,
            manager_id=manager_id,
            request_date=request_date,
            reason_for_applying=reason_for_applying
        )
        db.session.add(new_request)
        db.session.commit()
        return new_request