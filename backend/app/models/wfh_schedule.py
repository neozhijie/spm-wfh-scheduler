from app import db
from sqlalchemy.sql import expression

class WFHSchedule(db.Model):
    __tablename__ = 'WFHSchedule'

    schedule_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_id = db.Column(db.Integer, db.ForeignKey('WFHRequest.request_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    duration = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, server_default=expression.text("'PENDING'"))
    reason_for_withdrawing = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'schedule_id': self.schedule_id,
            'request_id': self.request_id,
            'date': self.date.isoformat(),
            'duration': self.duration,
            'status': self.status,
            'reason_for_withdrawing': self.reason_for_withdrawing
        }
