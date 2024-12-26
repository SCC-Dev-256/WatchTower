from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class LogEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(64))
    log_message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp()) 