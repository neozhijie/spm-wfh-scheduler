from app import db

class Staff(db.Model):
    __tablename__ = 'Staff'

    Staff_ID = db.Column(db.Integer, primary_key=True)
    Staff_FName = db.Column(db.String(255), nullable=True)
    Staff_LName = db.Column(db.String(255), nullable=True)
    Dept = db.Column(db.String(255), nullable=True)
    Position = db.Column(db.String(255), nullable=True)
    Country = db.Column(db.String(255), nullable=True)
    Email = db.Column(db.String(255), nullable=True)
    Reporting_Manager = db.Column(db.Integer, db.ForeignKey('Staff.Staff_ID'), nullable=True)
    Role = db.Column(db.Integer, nullable=True)
    Password = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            'Staff_ID': self.Staff_ID,
            'Staff_FName': self.Staff_FName,
            'Staff_LName': self.Staff_LName,
            'Dept': self.Dept,
            'Position': self.Position,
            'Country': self.Country,
            'Email': self.Email,
            'Reporting_Manager': self.Reporting_Manager,
            'Role': self.Role
        }