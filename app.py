from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from config import Config

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config.from_object(Config)
db = SQLAlchemy(app)
mail = Mail(app)

from routes import user_bp, diary_bp, emotion_report_bp

app.register_blueprint(user_bp)
app.register_blueprint(diary_bp)
app.register_blueprint(emotion_report_bp)


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

if __name__ == '__main__':
    app.run(debug=True)
