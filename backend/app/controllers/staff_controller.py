from flask import Blueprint, request, jsonify
from app.models.staff import Staff
from app import db

staff_bp = Blueprint('staff', __name__, url_prefix='/api')

@staff_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Missing email or password"}), 400

    staff = Staff.query.filter_by(Email=data['email']).first()

    if not staff or staff.Password != data['password']:
        return jsonify({"message": "Invalid email or password"}), 401
    
    return jsonify({
        "message": "Login successful",
        "staff_id": staff.Staff_ID,
        "name": f"{staff.Staff_FName} {staff.Staff_LName}",
        "role": staff.Role
    }), 200