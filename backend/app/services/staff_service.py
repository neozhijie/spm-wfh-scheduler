from app.models.staff import Staff

class StaffService:
    @staticmethod
    def authenticate_staff(email, password):
        staff = Staff.query.filter_by(email=email).first()
        if staff and staff.password == password:
            return staff
        return None

    @staticmethod
    def get_staff_details(staff):
        return {
            "staff_id": staff.staff_id,
            "fname": staff.staff_fname,"lname": staff.staff_lname,
            "role": staff.role
        }
