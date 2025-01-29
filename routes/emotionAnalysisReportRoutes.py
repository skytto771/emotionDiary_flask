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


@emotion_report_bp.route('/getAnalysis', methods=['GET'])
@token_required
def get_analysis(currentUserID):
    # 逻辑获取分析
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
    linkList = [diaryLinkToDict(link) for link in diaryEmotionTagLinks]


    for diary in diariesList:
        # 不重复添加
        existingLink = DiaryEmotionTagLink.query.filter_by(diaryID=diary['diaryID']).first()
        if(existingLink):
            continue

        # 获取日记的创建日期
        diary_date = diary.createdDate  # 假设 createdDate 为日记创建日期字段
        today = datetime.now().date()

        # 检查是否为昨天的日记
        if diary_date.date() == (today - timedelta(days=1)):
            continue

        # 对数据进行特征提取
        new_reviews_vectorized = vectorizer.transform([diary['content']])
        predictions_nb = nb_model.predict(new_reviews_vectorized)

        diary_dict = diary
        diary_dict['emotion'] = int(predictions_nb[0])  # 添加情感预测（取第一个元素）

        link_id = generate_unique_linkID()


        new_link = DiaryEmotionTagLink(
            linkID=link_id,
            diaryID=diary['diaryID'],
            tagID=str(predictions_nb[0])
        )
        db.session.add(new_link)
        db.session.commit()

    data = []
    for link in diaryEmotionTagLinks:
        diary = Diary.query.filter_by(diaryID=link.diaryID).first()
        tag = EmotionTag.query.filter_by(tagID=link.tagID).first()
        item = {
            'linkID': link.linkID,
            'tagID': link.tagID,
            'tagName': tag.tagName,
            'diaryID': link.diaryID,
            'diaryTitle': diary.title,
            'diaryContent': diary.content,
            'createdDate': diary.createdDate,
        }
        data.append(item)

    return jsonify({'code': 'SUCCESS', 'data': data})


