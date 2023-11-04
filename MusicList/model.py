from datetime import datetime
from MusicList import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    """
    存储用户信息。\n
    `level`: 表示用户的权限，`0` 表示普通用户，`1` 表示管理员。
    """

    index = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))
    level = db.Column(db.Integer)

    def set_password(self, password):
        """
        设定密码。
        """
        self.password = generate_password_hash(password)

    def validate_password(self, password):
        """
        校验密码。
        """
        return check_password_hash(self.password, password)

    def is_authenticated(self):
        """
        用于检测用户是否为已登录用户。只有已登录用户才可以满足 `@login_required` 的标准。\n
        这个函数的返回值应该与 `self.is_anonymous()` 相反。
        """
        return True

    def is_active(self):
        """
        用于检测用户是否已经激活。未经激活的账户无法登录。
        """
        return True

    def is_anonymous(self):
        """
        用于检测用户是否为未登录用户。\n
        这个函数的返回值应该与 `self.is_authenticated()` 相反。
        """
        return False

    def get_id(self):
        return str(self.index)


class Music(db.Model):
    """
    存储歌曲信息。
    """

    index = db.Column(db.Integer, primary_key=True)
    music_name = db.Column(db.String(100))
    artist = db.Column(db.String(100))
    link = db.Column(db.String(100))


class List(db.Model):
    """
    存储歌单信息。\n
    `owner`: 歌单创建者的用户的 `index`。\n
    `share`: 表示歌单是否公开，`0` 表示私密，`1`表示公开。
    """

    index = db.Column(db.Integer, primary_key=True)
    list_name = db.Column(db.String(100))
    owner = db.Column(db.Integer)
    share = db.Column(db.Integer)


class MusicList(db.Model):
    """
    存储歌曲和歌单的信息。\n
    如果一条记录出现在数据库中，则表名对应的歌曲在对应的列表中。
    """

    index = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer)
    music_id = db.Column(db.Integer)


class Message(db.Model):
    """
    一条消息。\n
    `owner`: 消息创建者的用户的 `index`。\n
    `list_index`: 每个消息可以关联一个列表，该字段为列表id \n
    """

    index = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    text = db.Column(db.String(500))
    owner = db.Column(db.Integer)
    time = db.Column(db.DateTime, default=datetime.now)
    list_index = db.Column(db.Integer)


class Comment(db.Model):
    """
    一条评论。\n
    `parent_message`: 原帖的`index`
    """

    index = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500))
    owner = db.Column(db.Integer)
    time = db.Column(db.DateTime, default=datetime.now)
    parent_massage = db.Column(db.Integer)


class FavoriteList(db.Model):
    """
    存储用户和歌单的信息。\n
    如果一条记录出现在数据库中，则表名对应的用户收藏了对应的列表。
    """

    index = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)


class FavoriteMessage(db.Model):
    """
    存储用户点赞帖子的记录。\n
    如果一条记录出现在数据库中，则表名对应的用户点赞了对应的帖子。
    """

    index = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
