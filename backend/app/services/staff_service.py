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

    # New Method to Get Subordinates
    @staticmethod
    def get_subordinates(staff_id):
        try:
            subordinates = Staff.query.filter_by(reporting_manager=staff_id).all()
            if not subordinates:
                raise ValueError(f"No subordinates found for staff_id: {staff_id}")
            return subordinates
        except SQLAlchemyError as e:
            print(f"Database error while fetching subordinates: {str(e)}")
            raise
        except ValueError as e:
            print(str(e))
            raise

    # NEW METHOD TO HANDLE BOTH CASES FOR DIRECTORS AND MANAGERS
    @staticmethod
    def get_all_subordinates(staff_id):
        """
        Retrieves all subordinates for a given staff member.
        For directors (role 1):
            - If they have role 2 subordinates, return them.
            - Else, return role 3 subordinates and their role 2 subordinates.
        For managers (role 3):
            - Return their direct role 2 subordinates.
        """
        try:
            staff = Staff.query.get(staff_id)
            if not staff:
                raise ValueError(f"No staff found with id: {staff_id}")

            if staff.role == 1:
                # Director
                # Check for direct role 2 subordinates
                direct_staff = Staff.query.filter_by(reporting_manager=staff_id, role=2).all()
                if direct_staff:
                    return {'type': 'direct', 'staff': direct_staff}
                else:
                    # Get role 3 managers under the director
                    managers = Staff.query.filter_by(reporting_manager=staff_id, role=3).all()
                    if not managers:
                        return {'type': 'none', 'staff': []}
                    managers_with_staff = {}
                    for manager in managers:
                        staffs = Staff.query.filter_by(reporting_manager=manager.staff_id, role=2).all()
                        managers_with_staff[manager] = staffs
                    return {'type': 'manager', 'managers': managers_with_staff}
            elif staff.role == 3:
                # Manager
                direct_staff = Staff.query.filter_by(reporting_manager=staff_id, role=2).all()
                return {'type': 'direct', 'staff': direct_staff}
            else:
                # Other roles do not have subordinates in this context
                return {'type': 'none', 'staff': []}
        except SQLAlchemyError as e:
            print(f"Database error while fetching all subordinates: {str(e)}")
            raise
        except ValueError as e:
            print(str(e))
            raise

    @staticmethod
    def get_departments():
        # Query all unique departments from the staff records
        departments = Staff.query.with_entities(Staff.dept).distinct().all()
        
        # Prepare the department list
        department_list = [{'dept': dept[0]} for dept in departments]  # dept[0] to access the actual department name

        return {'departments': department_list}
 