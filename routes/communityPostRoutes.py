from flask import Blueprint, request, jsonify
from models.communityPost import CommunityPost
from app import db

community_post_bp = Blueprint('community_post', __name__)

@community_post_bp.route('/community_post', methods=['POST'])
def add_post():
    data = request.get_json()
    # 添加社区帖子逻辑
    return jsonify({'message': 'Community post added successfully'}), 201
