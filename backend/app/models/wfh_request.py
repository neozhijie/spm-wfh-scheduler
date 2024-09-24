from app import db
from sqlalchemy.sql import expression

class WFHRequest(db.Model):
    __tablename__ = 'WFHRequest'

    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('Staff.staff_id'), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('Staff.staff_id'), nullable=False)
    request_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, server_default=expression.text("'PENDING'"))
    reason_for_applying = db.Column(db.Text, nullable=False)
    reason_for_rejection = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'request_id': self.request_id,
            'staff_id': self.staff_id,
            'manager_id': self.manager_id,
            'request_date': self.request_date.isoformat(),
            'status': self.status,
            'reason_for_applying': self.reason_for_applying,
            'reason_for_rejection': self.reason_for_rejection
        }
