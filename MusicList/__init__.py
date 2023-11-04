"""
用于初始化项目。
"""

from flask import Flask
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
import os

"""创建 Flask 实例"""
app = Flask(__name__)
app.config["SECRET_KEY"] = "dev"

"""初始化数据库(数据库保存在本地)"""
database_path = os.path.join(app.root_path, "data.db")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + database_path
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

"""用户登录"""
login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(index):
    """加载用户"""
    from MusicList.model import User
    return User.query.get(int(index))

@app.context_processor
def inject_user():
    from MusicList.model import User
    return dict(user=current_user)


# 导入其他模块
from MusicList import model, commands, api
