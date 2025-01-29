from flask import Blueprint, request, jsonify
from models.comment import Comment
from app import db

comment_bp = Blueprint('comment', __name__)

@comment_bp.route('/comment', methods=['POST'])
def add_comment():
    data = request.get_json()
    # 添加评论逻辑
    return jsonify({'message': 'Comment added successfully'}), 201
