# app/controllers/staff_controller.py
from flask import Blueprint, request, jsonify
from app.services.staff_service import StaffService

staff_bp = Blueprint('staff', __name__, url_prefix='/api')

@staff_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Missing email or password"}), 400

    staff = StaffService.authenticate_staff(data['email'], data['password'])

    if not staff:
        return jsonify({"message": "Invalid email or password"}), 401
    
    staff_details = StaffService.get_staff_details(staff)
    return jsonify({
        "message": "Login successful",
        **staff_details
    }), 200
