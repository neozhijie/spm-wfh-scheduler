from app import db

class Staff(db.Model):
    __tablename__ = 'Staff'

    staff_id = db.Column(db.Integer, primary_key=True)
    staff_fname = db.Column(db.String(255), nullable=False)
    staff_lname = db.Column(db.String(255), nullable=False)
    dept = db.Column(db.String(255), nullable=True)
    position = db.Column(db.String(255), nullable=True)
    country = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    reporting_manager = db.Column(db.Integer, db.ForeignKey('Staff.staff_id'), nullable=True)
    role = db.Column(db.Integer, nullable=True)
    password = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            'staff_id': self.staff_id,
            'staff_fname': self.staff_fname,
            'staff_lname': self.staff_lname,
            'dept': self.dept,
            'position': self.position,
            'country': self.country,
            'email': self.email,
            'reporting_manager': self.reporting_manager,
            'role': self.role
        }
