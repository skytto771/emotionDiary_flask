from flask import Blueprint, request, jsonify
from models.suggestion import Suggestion
from app import db

suggestion_bp = Blueprint('suggestion', __name__)

@suggestion_bp.route('/suggestion', methods=['POST'])
def add_suggestion():
    data = request.get_json()
    # 添加建议逻辑
    return jsonify({'message': 'Suggestion added successfully'}), 201
