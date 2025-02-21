import os
import tempfile

from flask import Blueprint, request, jsonify, make_response, send_file
from app import db
from models.fileSlice import FileSlice
from models.utils import token_required, generate_unique_file_id, generate_unique_fileSlice_id
from models.files import File
from io import BytesIO
from werkzeug.utils import secure_filename
import urllib.parse

file_bp = Blueprint('file', __name__)


@file_bp.route('/uploadSmallFile', methods=['POST'])
@token_required
def upload_small_file(currentUserId):
    # 检查上传的文件
    if 'file' not in request.files:
        return jsonify({'code': 'PARAM_ERROR', 'message': '未找到文件'}), 400

    file = request.files['file']

    # 参数校验
    file_name = request.form.get('fileName')
    file_size = request.form.get('fileSize')
    file_type = request.form.get('fileType')


    if not file_name or file.filename == '':
        return jsonify({'code': 'PARAM_ERROR', 'message': '文件名不能为空'}), 400


    try:
        file_id = generate_unique_file_id()

        # 存储文件信息到数据库
        new_file = File(
            fileID=file_id,
            fileName=file_name,
            fileType=file_type,
            fileSize=int(file_size),
            fileContent=file.read()  # 读取文件内容
        )
        db.session.add(new_file)
        db.session.commit()


        return jsonify({'code': 'SUCCESS', 'message': '文件上传成功', 'data': {'fileID': new_file.fileID}}), 201
    except Exception as e:
        db.session.rollback()
        print(f'发生了错误: {str(e)}')
        return jsonify({'code': 'EXCEPTION', 'message': '未知错误'}), 500


@file_bp.route('/startLUpload', methods=['POST'])
@token_required
def start_upload(currentUserId):
    # 获取请求参数
    file_name = request.form.get('fileName')  # 文件名
    file_type = request.form.get('fileType')  # 文件类型
    file_size = request.form.get('fileSize')  # 文件大小（字节）

    if not file_name or not file_type or file_size is None:
        return jsonify({'code': 'PARAM_ERROR', 'message': '缺少必要参数'}), 400

    try:
        # 生成唯一文件 ID
        file_id = generate_unique_file_id()

        # 创建一个新的文件记录，但不存储内容
        new_file = File(
            fileID=file_id,
            fileName=file_name,
            fileType=file_type,
            fileSize=file_size,
            fileContent=None  # 默认设置为 None
        )
        db.session.add(new_file)
        db.session.commit()

        return jsonify({'code': 'SUCCESS', 'message': '开始上传成功', 'data': {'fileID': file_id}}), 201
    except Exception as e:
        db.session.rollback()
        print(f'发生了错误: {str(e)}')
        return jsonify({'code': 'EXCEPTION', 'message': '未知错误'}), 500


@file_bp.route('/uploadLargeFile', methods=['POST'])
@token_required
def upload_large_file(currentUserId):
    # 检查上传的文件
    if 'file' not in request.files:
        return jsonify({'code': 'PARAM_ERROR', 'message': '未找到文件'}), 400

    file = request.files['file']

    # 获取参数
    file_id = request.form.get('fileID')
    slice_id = generate_unique_fileSlice_id()
    slice_index = request.form.get('sliceIndex')  # 切片索引
    slice_size = request.form.get('sliceSize')  # 切片大小（字节）

    if not file_id or not slice_index or not slice_size:
        return jsonify({'code': 'PARAM_ERROR', 'message': '缺少必要参数'}), 400

    try:
        # 读取切片内容
        print(1231313)
        slice_content = file.read()
        print('asdasd')

        # 存储切片信息到数据库
        new_slice = FileSlice(
            fileID=file_id,
            sliceID=slice_id,
            sliceIndex=int(slice_index),
            sliceContent=slice_content,
            sliceSize=int(slice_size)
        )
        db.session.add(new_slice)
        db.session.commit()  # 提交切片和文件信息

        return jsonify({'code': 'SUCCESS', 'data': {
            'sliceID': slice_id,
            'fileID': file_id,
        }}), 201

    except Exception as e:
        db.session.rollback()
        File.query.filter_by(fileID=file_id).delete()
        db.session.commit()
        print(f'发生了错误: {str(e)}')
        return jsonify({'code': 'EXCEPTION', 'message': '未知错误'}), 500


@file_bp.route('/mergeFileSlices', methods=['POST'])
@token_required
def mergeFileSlices(currentUserId):
    # 获取参数
    file_id = request.get_json().get('fileID')

    if not file_id:
        return jsonify({'code': 'PARAM_ERROR', 'message': '缺少必要的 fileID'}), 400

    try:
        temp_file_path = os.path.join(tempfile.gettempdir(), f"{file_id}.tmp")

        # 确认临时文件存在
        if not os.path.exists(temp_file_path):
            return jsonify({'code': 'ERROR', 'message': '临时文件不存在'}), 404

        # 读取临时文件内容
        with open(temp_file_path, 'rb') as f:
            full_file_content = f.read()
        # 保存到数据库
        existing_file = File.query.filter_by(fileID=file_id).first()
        if existing_file:
            existing_file.fileContent = full_file_content
            existing_file.fileSize = len(full_file_content)  # 更新文件大小
        else:
            existing_file = File(
                fileID=file_id,
                fileContent=full_file_content,
                fileSize=len(full_file_content)
            )
            db.session.add(existing_file)
        print('bf1212')
        db.session.commit()
        print(1321321546)

        # 删除临时文件
        os.remove(temp_file_path)

        return jsonify({'code': 'SUCCESS', 'message': '文件上传完成'}), 200

    except Exception as e:
        print(f'发生了错误: {str(e)}')
        db.session.rollback()  # 回滚事务
        return jsonify({'code': 'EXCEPTION', 'message': '未知错误'}), 500


@file_bp.route('/files/<file_id>', methods=['GET'])
def get_file_or_slices(file_id):
    try:
        # 从数据库中查找文件
        file = File.query.filter_by(fileID=file_id).first()
        if not file:
            return jsonify({'code': 'NOT_FOUND', 'message': '文件未找到'}), 404

        # 查找与文件ID关联的切片
        slices = FileSlice.query.filter_by(fileID=file_id).order_by(FileSlice.sliceIndex).all()
    
        # 如果没有切片，则直接返回文件内容
        if not slices:
            # 直接返回文件内容
            mime_type = file.fileType
            filename = file.fileName
            safe_filename = secure_filename(filename)  # 确保文件名安全

            response = make_response(file.fileContent)
            response.headers['Content-Type'] = mime_type
            response.headers['Content-Disposition'] = f'inline; filename="{safe_filename}"'
            return response

        # 如果有切片，合并切片内容
        file_content = b''.join(slice.sliceContent for slice in slices)

        # 创建一个临时文件并写入合并后的内容
        temp_file = BytesIO(file_content)

        # 设置文件名和 MIME 类型
        mime_type = file.fileType
        filename = file.fileName

        response = send_file(temp_file, mimetype=mime_type, as_attachment=False, download_name=filename)
        return response

    except Exception as e:
        print(f'发生了错误: {str(e)}')
        return jsonify({'code': 'EXCEPTION', 'message': '未知错误'}), 500


@file_bp.route('/getFilePath', methods=['POST'])
@token_required
def getFilePath(currentUserId):
    # 获取请求数据
    data = request.get_json()

    fileID = data.get('fileID')

    if not fileID:
        return jsonify({'code': 'PARAM_ERROR', 'message': '参数错误'}), 400

    try:
        # 根据文件ID生成文件访问路径
        file_url = f"{request.host_url}files/{fileID}"

        return jsonify({'code': 'SUCCESS', 'message': '路径生成成功', 'data': {'fileID': fileID, 'fileURL': file_url}}), 200
    except Exception as e:
        print(f'发生了错误: {str(e)}')
        return jsonify({'code': 'EXCEPTION', 'message': '未知错误'}), 500
