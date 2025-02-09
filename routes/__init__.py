from .userRoutes import user_bp
from .diaryRoutes import diary_bp
from .emotionAnalysisReportRoutes import emotion_report_bp
from .reminderRoutes import reminder_bp
from .suggestionRoutes import suggestion_bp
from .communityPostRoutes import community_post_bp
from .commentRoutes import comment_bp
from .fileRoutes import file_bp

def register_routes(app):
    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(diary_bp, url_prefix='/diaries')
    app.register_blueprint(emotion_report_bp, url_prefix='/emotion_reports')
    app.register_blueprint(reminder_bp, url_prefix='/reminders')
    app.register_blueprint(suggestion_bp, url_prefix='/suggestions')
    app.register_blueprint(community_post_bp, url_prefix='/community_posts')
    app.register_blueprint(comment_bp, url_prefix='/comments')
    app.register_blueprint(file_bp, url_prefix='/files')
