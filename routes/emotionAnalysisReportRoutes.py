from datetime import datetime, timedelta


from flask import Blueprint, jsonify
from models.emotionAnalysisReport import EmotionAnalysisReport
from models.diaryEmotionTagLink import DiaryEmotionTagLink
from models.emotionTag import EmotionTag
from models.diary import Diary
from models.utils import token_required, generate_unique_linkID
from app import db
import pandas as pd
import joblib
import os

emotion_report_bp = Blueprint('emotion_report', __name__)


def diaryLinkToDict(link):
    return {
        'linkID': link.linkID,
        'diaryID': link.linkID,
        'tagID': link.linkID,
    }

def diaryToDict(diary):
    return {
        'diaryID': diary.diaryID,
        'userID': diary.userID,
        'title': diary.title,
        'content': diary.content,
        'createdDate': diary.createdDate.isoformat()  # 将日期时间转换为字符串格式
    }


@emotion_report_bp.route('/getAnalysisReport', methods=['GET'])
@token_required
def get_analysis_reports():
    # 逻辑获取报告
    return jsonify({'message': 'Reports retrieved successfully'})



@emotion_report_bp.route('/analysisEmotion_system', methods=['GET'])
def perform_analysis():
    print('现在是',datetime.now(),'点，开始执行情绪分析任务')
    # 获取当前文件的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建模型和向量化器的绝对路径
    nb_model_path = os.path.join(current_dir, '../static/naive_bayes_model.pkl')
    logreg_model_path = os.path.join(current_dir, '../static/logistic_regression_model.pkl')
    vectorizer_path = os.path.join(current_dir, '../static/vectorizer.pkl')

    # 加载保存的模型
    nb_model = joblib.load(nb_model_path)
    logreg_model = joblib.load(logreg_model_path)
    # svm_model = joblib.load('../static/svm_model.pkl')
    # rf_model = joblib.load('../static/random_forest_model.pkl')

    # 加载特征向量化器
    vectorizer = joblib.load(vectorizer_path)
    diaryEmotionTagLinks = DiaryEmotionTagLink.query.all()
    diaries = Diary.query.all()
    diariesList = [diaryToDict(diary) for diary in diaries]


    for diary in diariesList:
        # 不重复添加
        existingLink = DiaryEmotionTagLink.query.filter_by(diaryID=diary['diaryID']).first()
        if(int(existingLink.tagID) != -1):
            continue

        # 对数据进行特征提取
        new_reviews_vectorized = vectorizer.transform([diary['content']])
        predictions_nb = nb_model.predict(new_reviews_vectorized)

        diary_dict = diary
        diary_dict['emotion'] = int(predictions_nb[0])  # 添加情感预测（取第一个元素）

        link_id = generate_unique_linkID()


        existingLink.tagID = str(predictions_nb[0])
        db.session.commit()

    result = "Analysis performed successfully"
    return result


@emotion_report_bp.route('/predictRecentDiaries', methods=['GET'])
def predict_recent_diaries():
    # 获取当前文件的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    vectorizer_path = os.path.join(current_dir, '../static/vectorizer.pkl')
    nb_model_path = os.path.join(current_dir, '../static/naive_bayes_model.pkl')

    # 加载模型和向量化器
    vectorizer = joblib.load(vectorizer_path)
    nb_model = joblib.load(nb_model_path)

    # 计算30天前的日期
    thirty_days_ago = datetime.now() - timedelta(days=30)

    # 查询最近30天的日记
    recent_diaries = Diary.query.filter(Diary.createdDate >= thirty_days_ago).all()
    predictions = []

    for diary in recent_diaries:
        # 对数据进行特征提取
        new_reviews_vectorized = vectorizer.transform([diary.content])
        predictions_nb = nb_model.predict(new_reviews_vectorized)

        # 创建结果字典
        predictions.append({
            'diaryID': diary.diaryID,
            'title': diary.title,
            'predictedEmotion': int(predictions_nb[0])  # 保存情感预测
        })

    return jsonify({'code': 'SUCCESS', 'data': predictions}), 201


@emotion_report_bp.route('/getUserRecentDiaries', methods=['POST'])
@token_required
def get_user_recent_diaries(currentUserId):
    print('获取用户近30天日记及其情感标签')

    thirty_days_ago = datetime.now() - timedelta(days=30)

    # 查询用户最近30天的日记
    recent_diaries = Diary.query.filter(Diary.userID == currentUserId, Diary.createdDate >= thirty_days_ago).all()
    diary_list = []

    for diary in recent_diaries:
        DELink = DiaryEmotionTagLink.query.filter_by(diaryID=diary.diaryID).first()
        tag = EmotionTag.query.filter_by(tagID=DELink.tagID).first() if DELink else None

        # 将转换后的日记添加到列表中
        diary_dict = diaryToDict(diary)
        diary_dict['tagName'] = tag.tagName if tag else None
        diary_dict['tagID'] = tag.tagID if tag else None
        diary_list.append(diary_dict)

    return jsonify({'code': 'SUCCESS', 'data': diary_list}), 201