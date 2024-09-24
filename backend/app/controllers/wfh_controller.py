from flask import Blueprint, request, jsonify
from app.services.wfh_request_service import WFHRequestService
from app.services.wfh_schedule_service import WFHScheduleService
from datetime import datetime
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
                       'date', 'duration']
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
        wfh_request = WFHRequestService.create_request(
            staff_id=data['staff_id'],
            manager_id=data['manager_id'],
            request_date=today,
            reason_for_applying=data['reason_for_applying']
        )
        print(f"WFH request created successfully. Request ID: {wfh_request.request_id}")

        # Create WFH Schedules
        print("\n----- Creating WFH Schedules -----")
        start_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        end_date = None
        if 'end_date' in data and data['end_date']:
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()

        wfh_schedules = WFHScheduleService.create_schedule(
            request_id=wfh_request.request_id,
            start_date=start_date,
            end_date=end_date,
            duration=data['duration']
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

    except Exception as e:
        db.session.rollback()
        print("\n===== ERROR OCCURRED =====")
        print(f"An error occurred while processing the WFH request: {str(e)}")
        print("============================\n")
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500
