import json
import re
from datetime import datetime, timedelta

import requests
from flask import Blueprint, jsonify, request
from models.emotionAnalysisReport import EmotionAnalysisReport
from models.diaryEmotionTagLink import DiaryEmotionTagLink
from models.emotionTag import EmotionTag
from models.diary import Diary
from models.utils import token_required, generate_unique_linkID, normalize_datetime
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

def remove_emojis(text):
    # 使用正则表达式去除表情符号
    return re.sub(r'[^\w\s,]', '', text)  # 只保留字母、数字、空格和逗号

@emotion_report_bp.route('/getAnalysisReport', methods=['GET'])
@token_required
def get_analysis_reports():
    # 逻辑获取报告
    return jsonify({'message': 'Reports retrieved successfully'})



@emotion_report_bp.route('/analysisEmotion_system', methods=['GET'])
def perform_analysis():
    print('现在是',datetime.now(),'点，开始执行情绪分析任务')

    url = "https://spark-api-open.xf-yun.com/v1/chat/completions"

    headers = {
        "Authorization": "Bearer rcvRKvXkWOsHxgzNocoe:xAUDdGeBhzeeSSzOfBNF",
        "Content-Type": "application/json"
    }

    diaries = Diary.query.all()
    diariesList = [diaryToDict(diary) for diary in diaries]

    count = 0

    for diary in diariesList:
        count += 1
        existingLink = DiaryEmotionTagLink.query.filter_by(diaryID=diary['diaryID']).first()
        # 只分析未分析的数据
        if int(existingLink.tagID) != -1:
            continue
        print(f'分析第${count}篇日记')
        # ai分析情感
        payload = {
            "model": "lite",
            "stream": False,
            "max_tokens": 4096,
            "top_k": 4,
            "temperature": 0.5,
            "messages": [
                {
                    "role": "system",
                    "content": "你是情感分析大师，只会分析文章情感并返回固定结果：'日记情绪值：。'(0：消极，1：积极)"
                },
                {
                    "content": f'分析下面这篇日记，获取其的情感，返回并只返回指定结果，如积极的日记返回‘日记情绪值：1。’，消极的日记返回‘日记情绪值：0。如果没有文本内容的日记按消极日记结算’:${str(diary["content"])}',
                    "role": "user"
                }
            ]
        }

        response = requests.request('POST', url, json=payload, headers=headers)
        response.encoding = "utf-8"
        analysis_data = json.loads(response.text)
        response_msg = analysis_data['choices'][0]['message']
        response_content = response_msg['content']
        emotion = response_content.split('日记情绪值：')[1]
        emotion_id = emotion.split('。')[0]

        existingLink.tagID = str(emotion_id)
        existingLink.result = response_content
        if len(existingLink.tagID) > 4:
            print(existingLink.tagID, '超长', response_content)
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


@emotion_report_bp.route('/getUserEmotionData', methods=['POST'])
@token_required
def get_User_Emotion_Data(currentUserId):
    print('查询用户的日记并生成报告')
    data = request.get_json()
    start_time = data['start_time']
    end_time = data['end_time']

    # 如果没有传入 start_time 或 end_time，则设置默认值为最近30天
    if not start_time:
        start_time = (datetime.now() - timedelta(days=30))  # 默认起始时间为30天前
    else:
        start_time = normalize_datetime(start_time)  # 正常化传入的 start_time

    if not end_time:
        end_time = datetime.now()  # 默认结束时间为当前时间
    else:
        end_time = normalize_datetime(end_time)  # 正常化传入的 end_time
    recent_diaries = Diary.query.filter(Diary.userID == currentUserId, Diary.createdDate >= start_time, Diary.createdDate <= end_time).order_by(Diary.createdDate).all()
    diary_list = []

    for diary in recent_diaries:
        DELink = DiaryEmotionTagLink.query.filter_by(diaryID=diary.diaryID).first()
        tag = EmotionTag.query.filter_by(tagID=DELink.tagID).first() if DELink else None

        # 将转换后的日记添加到列表中
        diary_dict = diaryToDict(diary)
        diary_dict['tagName'] = tag.tagName if tag else None
        diary_dict['tagID'] = tag.tagID if tag else None
        diary_list.append(diary_dict)


    return jsonify({'code': 'SUCCESS', 'data': diary_list }), 201

@emotion_report_bp.route('/getDiariesSuggestion', methods=['POST'])
@token_required
def get_diaries_suggestion(currentUserId):
    print('根据统计信息提供建议')
    data = request.get_json()
    info = data['info']

    if not info:
        return jsonify({'code': 'PARAM_ERROR', 'message': '参数错误'}), 403

    # 获取建议
    url = "https://spark-api-open.xf-yun.com/v1/chat/completions"

    headers = {
        "Authorization": "Bearer rcvRKvXkWOsHxgzNocoe:xAUDdGeBhzeeSSzOfBNF",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "lite",
        "stream": False,
        "max_tokens": 4096,
        "top_k": 4,
        "temperature": 0.5,
        "messages": [
            {
                "role": "system",
                "content": "你是一位情感分析导师,目标任务,请总结我给出的全部日记，进行情感分析并返回报告,需求说明,要求分析情感并总结后提供总结和建议，同时文字温暖、文笔流畅，段落清晰,风格设定,温暖真诚，如果可以，请推荐几首音乐，回复设定：总结：... \n建议：...；"
            },
            {
                "content": info,
                "role": "user"
            }
        ]
    }

    response = requests.request('POST', url, json=payload, headers=headers)
    response.encoding = "utf-8"
    analysis_data = json.loads(response.text)
    response_msg = analysis_data['choices'][0]['message']
    response_content = response_msg['content']

    return jsonify({'code': 'SUCCESS', 'message': '成功获取建议', 'suggest': response_content}), 201

@emotion_report_bp.route('/getUseranalysis', methods=['GET'])
@token_required
def get_User_Analysis(currentUserId):
    print('分析用户近30天日记')

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

    thirty_days_ago = datetime.now() - timedelta(days=30)
    # 查询用户最近30天的日记
    recent_diaries = Diary.query.filter(Diary.userID == currentUserId, Diary.createdDate >= thirty_days_ago).all()

    diariesList = [diaryToDict(diary) for diary in recent_diaries]

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


        existingLink.tagID = str(predictions_nb[0])
        db.session.commit()

    result = "Analysis performed successfully"
    return jsonify({'code': 'SUCCESS','message': '分析完成'}), 201

@emotion_report_bp.route('/getUseranalysisByAI', methods=['GET'])
@token_required
def get_User_Analysis_by_AI(currentUserId):
    print('ai分析用户未分析的日记')

    url = "https://spark-api-open.xf-yun.com/v1/chat/completions"

    headers = {
        "Authorization": "Bearer rcvRKvXkWOsHxgzNocoe:xAUDdGeBhzeeSSzOfBNF",
        "Content-Type": "application/json"
    }


    recent_diaries = Diary.query.filter(Diary.userID == currentUserId).order_by(Diary.createdDate).all()

    diariesList = [diaryToDict(diary) for diary in recent_diaries]

    count = 0

    for diary in diariesList:
        count += 1
        existingLink = DiaryEmotionTagLink.query.filter_by(diaryID=diary['diaryID']).first()
        # 只分析未分析的数据
        # if int(existingLink.tagID) != -1:
        #     continue
        print(f'分析第${count}篇日记')
        # ai分析情感
        payload = {
            "model": "lite",
            "stream": False,
            "max_tokens": 4096,
            "top_k": 4,
            "temperature": 0.5,
            "messages": [
                {
                    "role": "system",
                    "content": "你是情感分析大师，只会分析文章情感并返回固定结果：'日记情绪值：。'(0：消极，1：积极)"
                },
                {
                    "content": f'分析下面这篇日记，获取其的情感，返回并只返回指定结果，如积极的日记返回‘日记情绪值：1。’，消极的日记返回‘日记情绪值：0。如果没有文本内容的日记按消极日记结算’:${str(diary["content"])}',
                    "role": "user"
                }
            ]
        }

        response = requests.request('POST', url, json=payload, headers=headers)
        response.encoding = "utf-8"
        analysis_data = json.loads(response.text)
        response_msg = analysis_data['choices'][0]['message']
        response_content = response_msg['content']
        emotion = response_content.split('日记情绪值：')[1]
        emotion_id = emotion.split('。')[0]

        existingLink.tagID = str(emotion_id)
        existingLink.result = response_content
        if len(existingLink.tagID) > 4:
            print(existingLink.tagID, '超长', response_content)
        db.session.commit()

    result = "Analysis performed successfully"
    return jsonify({'code': 'SUCCESS','message': '分析完成'}), 201