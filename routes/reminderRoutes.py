from flask import Blueprint, request, jsonify
from models.reminder import Reminder
from app import db

reminder_bp = Blueprint('reminder', __name__)

@reminder_bp.route('/reminder', methods=['POST'])
def add_reminder():
    data = request.get_json()
    # 添加提醒逻辑
    return jsonify({'message': 'Reminder added successfully'}), 201
