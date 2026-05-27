from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Router(db.Model):
    __tablename__ = 'routers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)  # IPv4/IPv6
    admin_login = db.Column(db.String(50), nullable=False)
    admin_password = db.Column(db.String(100), nullable=False)
    wifi_password = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    note = db.Column(db.Text, nullable=True)
    web_port = db.Column(db.Integer, default=80)
    ssh_port = db.Column(db.Integer, default=22)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ip_address': self.ip_address,
            'admin_login': self.admin_login,
            'admin_password': self.admin_password,
            'wifi_password': self.wifi_password,
            'location': self.location,
            'note': self.note,
            'web_port': self.web_port,
            'ssh_port': self.ssh_port,
        }