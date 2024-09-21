from app import db
from datetime import datetime

class Request(db.Model):
    __tablename__ = 'request'

    Request_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Staff_ID = db.Column(db.Integer, db.ForeignKey('employee.Staff_ID'), nullable=False)
    Reporting_Manager = db.Column(db.Integer, db.ForeignKey('employee.Staff_ID'), nullable=True)
    Dept = db.Column(db.String(50), nullable=False)
    Date = db.Column(db.Date, nullable=False)
    Start_Date = db.Column(db.Date, nullable=False)
    End_Date = db.Column(db.Date, nullable=False)
    Half_Day = db.Column(db.String(50))
    Reason = db.Column(db.String(200), nullable=False)
    Status = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            'Request_ID': self.Request_ID,
            'Staff_ID': self.Staff_ID,
            'Reporting_Manager': self.Reporting_Manager,
            'Dept': self.Dept,
            'Date': self.Date.isoformat(),
            'Start_Date': self.Start_Date.isoformat(),
            'End_Date': self.End_Date.isoformat(),
            'Half_Day': self.Half_Day,
            'Reason': self.Reason,
            'Status': self.Status
        }
