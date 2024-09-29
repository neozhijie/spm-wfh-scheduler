from app.models.staff import Staff
from sqlalchemy.exc import SQLAlchemyError

class StaffService:
    @staticmethod
    def authenticate_staff(email, password):
        try:
            staff = Staff.query.filter_by(email=email).first()
            if staff and staff.password == password:
                return staff
            else:
                print("Wrong email or password")
                return None
            
        except SQLAlchemyError as e:
            print(f"Database error during authentication: {str(e)}")
            raise


    @staticmethod
    def get_staff_by_id(staff_id):
        try:
            staff = Staff.query.get(staff_id)
            if staff is None:
                raise ValueError(f"No staff found with id: {staff_id}")
            return staff
        except SQLAlchemyError as e:
            print(f"Database error while fetching staff by ID: {str(e)}")
            raise
        except ValueError as e:
            print(str(e))
            raise