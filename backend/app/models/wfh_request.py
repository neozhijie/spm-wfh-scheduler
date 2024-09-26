from app import db
from sqlalchemy.sql import expression

class WFHRequest(db.Model):
    __tablename__ = 'WFHRequest'

    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('Staff.staff_id'), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('Staff.staff_id'), nullable=False)
    request_date = db.Column(db.Date, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), nullable=False, server_default=expression.text("'PENDING'"))
    reason_for_applying = db.Column(db.Text, nullable=False)
    reason_for_rejection = db.Column(db.Text, nullable=True)

    def to_dict(self):
        end_date = None
        if self.end_date:
            end_date = self.end_date.isoformat()

        return {
            'request_id': self.request_id,
            'staff_id': self.staff_id,
            'manager_id': self.manager_id,
            'request_date': self.request_date.isoformat(),
            'start_date': self.start_date.isoformat(),
            'end_date': end_date,
            'status': self.status,
            'reason_for_applying': self.reason_for_applying,
            'reason_for_rejection': self.reason_for_rejection,
            'is_recurring': self.end_date is not None
        }
