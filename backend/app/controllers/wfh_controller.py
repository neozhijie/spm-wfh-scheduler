from flask import Blueprint, request, jsonify
from app.services.wfh_request_service import WFHRequestService
from app.services.wfh_schedule_service import WFHScheduleService
from app.services.wfh_check_service import WFHCheckService
from datetime import datetime, timedelta, date
from app import db

wfh_bp = Blueprint('wfh', __name__, url_prefix='/api')

@wfh_bp.route('/request', methods=['POST'])
def create_wfh_request():
    print("\n===== NEW WFH REQUEST =====")
    print("Received a new WFH request")
    data = request.get_json()

    # Validate input
    print("\n----- Input Validation -----")
    required_fields = ['staff_id', 'manager_id', 'reason_for_applying', 
                       'date', 'duration', 'dept', 'position']
    for field in required_fields:
        if field not in data:
            print(f"Validation failed: Missing required field: {field}")
            return jsonify({"message": f"Missing required field: {field}"}), 400
    print("Input validation successful")

    try:
        # Get today's date for the request_date
        today = datetime.now().date()

        # Create WFHRequest
        print("\n----- Creating WFH Request -----")
        end_date = None
        if 'end_date' in data and data['end_date']:
            if(not isinstance(data['end_date'], date)):
                end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()

        wfh_request = WFHRequestService.create_request(
            staff_id=data['staff_id'],
            manager_id=data['manager_id'],
            request_date=today,
            start_date=data['date'],
            end_date=end_date,
            reason_for_applying=data['reason_for_applying']
        )
        print(f"WFH request created successfully. Request ID: {wfh_request.request_id}")

        # Create WFH Schedules
        print("\n----- Creating WFH Schedules -----")
        if(not isinstance(data['date'], date)):
            start_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        wfh_schedules = WFHScheduleService.create_schedule(
            request_id=wfh_request.request_id,
            staff_id=data['staff_id'],
            manager_id=data['manager_id'],
            start_date=start_date,
            end_date=end_date,
            duration=data['duration'],
            dept=data['dept'],
            position=data['position']
        )
        print(f"WFH schedules created successfully. Number of schedules: {len(wfh_schedules)}")

        print("\n===== WFH REQUEST COMPLETED =====")
        print("WFH request and schedules creation completed successfully")
        print(f"Request ID: {wfh_request.request_id}")
        print(f"Number of Schedules: {len(wfh_schedules)}")
        print(f"Status: {wfh_request.status}")
        print("==================================\n")

        return jsonify({
            "message": "WFH request and schedules created successfully",
            "request_id": wfh_request.request_id,
            "schedule_count": len(wfh_schedules),
            "status": wfh_request.status
        }), 201

    except ValueError as ve:
        print(f"\n===== ERROR OCCURRED =====")
        print(f"Validation failed: {ve}")
        print("============================\n")
        db.session.rollback()
        return jsonify({"message": str(ve)}), 400
        
    except Exception as e:
        db.session.rollback()
        print("\n===== ERROR OCCURRED =====")
        print(f"An error occurred while processing the WFH request: {str(e)}")
        print("============================\n")
        db.session.rollback()
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

@wfh_bp.route('/pending-requests/<int:manager_id>', methods=['GET'])
def get_pending_requests(manager_id):
    print(f"\n===== GET PENDING REQUESTS =====")
    print(f"Retrieving pending requests for manager_id: {manager_id}")
    
    try:
        print("Calling WFHRequestService.get_pending_requests_for_manager()")
        pending_requests = WFHRequestService.get_pending_requests_for_manager(manager_id)
        
        print(f"Number of pending requests retrieved: {len(pending_requests)}")
        
        response = [request.to_dict() for request in pending_requests]
        print("Successfully converted requests to dictionary format")
        
        print("===== GET PENDING REQUESTS COMPLETED =====\n")
        return jsonify(response), 200
    
    except Exception as e:
        print(f"ERROR: An exception occurred while retrieving pending requests")
        print(f"Exception details: {str(e)}")
        print("===== GET PENDING REQUESTS FAILED =====\n")
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500


@wfh_bp.route('/update-request', methods=['PATCH'])
def update_wfh_request():
    print(f"\n===== UPDATE REQUESTS =====")
    data = request.get_json()
    request_id = data['request_id']
    new_request_status = data['request_status']
    reason = data['reason']

    # Get the current date
    current_date = datetime.now().date()
    # Calculate the date 2 months ago
    two_months_ago = current_date - timedelta(days=60)

    print(f"Updating request for request_id: {request_id}")
    
    try:
        print("Calling WFHRequestService.update_request()")
        response = WFHRequestService.update_request(request_id, new_request_status, two_months_ago, reason)
        if response == True:
            response2 = WFHScheduleService.update_schedule(request_id, new_request_status)

            if response2 == True:
                print("Successfully updated")
                print("===== UPDATE PENDING REQUESTS COMPLETED =====\n")
                return jsonify(f"Successfully updated request {request_id} as {new_request_status}"), 200
            
            else:
                return jsonify(response), 404
            
        else:
            return jsonify(response), 404
    
    except Exception as e:
        db.session.rollback()
        print("\n===== ERROR OCCURRED =====")
        print(f"An error occurred while processing the WFH request: {str(e)}")
        print("============================\n")
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500


@wfh_bp.route('/reject-expired-request', methods=['POST'])
def reject_expired_request():
    """
    Check the current date against the start date in the database rows.
    If the start date is older than 2 months, update the status to 'REJECTED'.
    """
    try:
        # Get the current date
        current_date = datetime.now().date()

        # Calculate the date 2 months ago
        two_months_ago = current_date - timedelta(days=60)

        # Fetch all requests from the database
        expired = WFHRequestService.reject_expired(two_months_ago)
        return jsonify({"message": f"Updated {expired} requests to 'REJECTED'."}), 200

    except Exception as e:
        db.session.rollback()  # Rollback the session in case of an error
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500
    
@wfh_bp.route('/check-wfh-count', methods=['POST'])
def check_wfh_count():

    data = request.get_json()
    staff_id = data['staff_id']
    date = data['date']
    
    try:
        result = WFHCheckService.check_department_count(staff_id, date)
        return('done')
        print('done')
    except Exception as e:
        db.session.rollback()  # Rollback the session in case of an error
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500
