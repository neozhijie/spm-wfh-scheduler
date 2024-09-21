from app import db

class Employee(db.Model):
    __tablename__ = 'employee'

    Staff_ID = db.Column(db.Integer, primary_key=True)
    Staff_Fname = db.Column(db.String(50), nullable=False)
    Staff_Lname = db.Column(db.String(50), nullable=False)
    Dept = db.Column(db.String(50), nullable=False)
    Position = db.Column(db.String(50), nullable=False)
    Country = db.Column(db.String(50), nullable=False)
    Email = db.Column(db.String(100), nullable=False)
    Password = db.Column(db.String(100), nullable=False)
    Reporting_Manager = db.Column(db.Integer, db.ForeignKey('employee.Staff_ID'))
    Role = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            'Staff_ID': self.Staff_ID,
            'Staff_Fname': self.Staff_Fname,
            'Staff_Lname': self.Staff_Lname,
            'Dept': self.Dept,
            'Position': self.Position,
            'Country': self.Country,
            'Email': self.Email,
            'Reporting_Manager': self.Reporting_Manager,
            'Role': self.Role
        }
