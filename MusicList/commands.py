""" 
命令行相关工具，用于后台管理数据库等操作。
"""

import click

from MusicList import app, db
from MusicList.model import User


@app.cli.command()
@click.option("--drop", is_flag=True, help="Create after drop.")
def initdb(drop):
    """自动创建数据库"""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo("数据库初始化成功。")


@app.cli.command()
@click.option("--username", prompt=True, help="The username used to login.")
@click.option("--password", prompt=True, help="The password used to login.")
def admin(username, password):
    """创建管理员账户"""
    if User.query.filter(User.username == username).first() is not None:
        click.echo("用户名已被占用，请更换新的用户名。")
    else:
        user = User(username=username, password="", level=1)
        user.set_password(password)
        db.session.commit()
        click.echo("操作成功。")
