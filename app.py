from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from flask_mail import Mail, Message
import requests
from config import Config

app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()
CORS(app, supports_credentials=True)
app.config.from_object(Config)
db = SQLAlchemy(app)
mail = Mail(app)

from routes import user_bp, diary_bp, emotion_report_bp, file_bp

app.register_blueprint(user_bp)
app.register_blueprint(diary_bp)
app.register_blueprint(emotion_report_bp)
app.register_blueprint(file_bp)


# 设置定时任务
def schedule_analysis():
    # 添加第一个任务：每天0点执行
    scheduler.add_job(
        lambda: requests.get('http://127.0.0.1:5000/analysisEmotion_system'),
        'cron',
        hour=0,  # 每天0点
        minute=0  # 几分执行任务
    )

    # 添加第二个任务：每天12点执行
    scheduler.add_job(
        lambda: requests.get('http://127.0.0.1:5000/analysisEmotion_system'),
        'cron',
        hour=12,  # 每天12点
        minute=0  # 几分执行任务
    )

# 全局错误处理函数
@app.errorhandler(Exception)
def handle_exception(e):
    # 在后端打印错误信息
    print(f"发生错误: {e}")
    # 向前端返回 JSON 格式的错误信息
    response = {
        "code": "UnExpected",
        "message": "未知错误",
    }
    return jsonify(response), 500  # 500 是 HTTP 状态码，表示服务器内部错误


# 在应用启动时安排任务
schedule_analysis()

if __name__ == '__main__':
    app.run(debug=True)
