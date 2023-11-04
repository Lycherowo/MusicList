"""
与消息有关的页面。\n
包括：查看消息列表和消息详情；添加和删除帖子和评论；查看一个用户的帖子和评论；
点赞和取消点赞帖子；查看已点赞的帖子。
"""


from datetime import datetime
from flask import request, flash, redirect, url_for, render_template
from flask_login import current_user, login_required

from MusicList import app, db
from MusicList.model import User, List, Message, Comment, FavoriteMessage


@app.route("/message_list", methods=["GET"])
@login_required
def message_list():
    """
    GET: 最新帖子页面 \n
    """
    per_page = 30
    page = request.args.get("page", 1, type=int)
    columns = [Message.index, Message.time, Message.title, Message.owner, User.username]
    messages = (
        Message.query.join(User, Message.owner == User.index)  # 合并两个数据表
        .with_entities(*columns)  # 选择所需要的列
        .order_by(Message.time.desc())  # 按照时间排序
        .paginate(page, per_page, error_out=False)  # 进行分页
    )
    data = dict(messages=messages, info="最新消息", is_current_user=True)
    return render_template("message/message_list.html", **data)


@app.route("/new_message", methods=["GET", "POST"])
@login_required
def new_message():
    """
    GET: 发送消息页面 \n
    POST: 发送消息 \n
    """
    if request.method == "GET":
        lists = List.query.filter_by(owner=current_user.index, share=1).all()
        return render_template("message/new_message.html", lists=lists)
    elif request.method == "POST":
        title = request.form.get("title")
        text = request.form.get("text")
        list_index = request.form.get("list_index")
        # 检查是否输入数据
        if title is None or text is None:
            flash("请输入标题和正文")
            return redirect(url_for("new_message"))
        # 检查歌单是否存在
        list_index = list_index if list_index is not None else "0"
        if list_index != "0":
            music_list = List.query.filter_by(index=list_index).first()
            if music_list is None:
                flash(f"歌单不存在")
                return redirect(url_for("new_message"))
            if not music_list.owner == current_user.index:
                flash("发生错误，请重试")
                return redirect(url_for("new_message"))
        # 插入数据
        data = {
            "title": title,
            "text": text,
            "owner": current_user.index,
            "time": datetime.now(),
            "list_index": list_index,
        }
        db.session.add(Message(**data))
        db.session.commit()
        flash("发送成功")
        return redirect(url_for("message_list"))


@app.route("/message_detail/<int:message_index>", methods=["GET", "POST"])
@login_required
def message_detail(message_index):
    """
    GET: 消息详情页面，包含消息，时间，发送者，关联的歌单，评论 \n
    POST: 在这条消息下发送一条评论 \n
    """
    if request.method == "GET":
        # 获取页码
        per_page = 30
        page = request.args.get("page", 1, type=int)
        # 从数据库中获取消息并检查
        message = Message.query.filter(Message.index == message_index).first()
        if message == None:
            flash("发生错误，请重试")
            return redirect(url_for("message_list"))
        message.text = message.text.replace("\n", "<br>")
        # 获取歌单信息
        music_list = None
        if not message.list_index == 0:
            music_list = List.query.filter_by(index=message.list_index, share=1).first()
        # 获取用户信息
        user = User.query.filter(User.index == message.owner).first()
        if user == None:
            flash("发生错误，请重试")
            return redirect(url_for("message_list"))
        # 获取评论
        cols = [Comment.index, Comment.text, Comment.time, Comment.owner, User.username]
        comments = (
            Comment.query.join(User, User.index == Comment.owner)
            .filter(Comment.parent_massage == message_index)
            .with_entities(*cols)
            .order_by(Comment.time.desc())
            .paginate(page, per_page, error_out=False)
        )
        # 检查用户是否为消息点赞
        favorite_message = (
            FavoriteMessage.query.filter(FavoriteMessage.message_id == message_index)
            .filter(FavoriteMessage.user_id == current_user.index)
            .first()
        )
        favorite = False
        if favorite_message:
            favorite = True
        # 返回网页
        data = {
            "user": user,
            "message": message,
            "comments": comments,
            "music_list": music_list,
            "favorite": favorite,
        }
        return render_template("message/message_detail.html", **data)
    elif request.method == "POST":
        # 获取表单数据
        message_index = request.form.get("message_index")
        text = request.form.get("text")
        # 检查数据合法性
        parent_message = Message.query.filter(Message.index == message_index).first()
        if message_index is None:
            flash("试图评论的消息不存在")
            return redirect(url_for("message_list"))
        if text is None or text == "":
            flash("请输入评论内容")
            return redirect(url_for(message_detail), message_index=message_index)
        # 向数据库中插入消息
        data = {
            "text": text,
            "owner": current_user.index,
            "time": datetime.now(),
            "parent_massage": message_index,
        }
        db.session.add(Comment(**data))
        db.session.commit()
        flash("发送成功")
        return redirect(url_for("message_detail", message_index=message_index))


@app.route("/delete_message/<int:message_index>", methods=["GET"])
@login_required
def delete_message(message_index):
    """
    GET: 删除消息
    """
    # 检索，确认和删除帖子
    message = Message.query.filter(Message.index == message_index).first()
    if message is None:
        flash("消息不存在")
        return redirect(url_for("message_list"))
    if not message.owner == current_user.index:
        flash("发生错误，请重试")
        return redirect(url_for("message_list"))
    db.session.delete(message)
    # 检索和删除评论
    Comment.query.filter(Comment.parent_massage == message_index).delete()
    # 提交删除指令和返回成功信息
    db.session.commit()
    flash("删除成功")
    return redirect(url_for("message_list"))


@app.route("/delete_comment/<int:comment_index>", methods=["GET"])
@login_required
def delete_comment(comment_index):
    """
    GET: 删除评论
    """
    # 检索，确认和删除评论
    comment = Comment.query.filter(Comment.index == comment_index).first()
    comment_parent = comment.parent_massage
    if comment is None:
        flash("消息不存在")
        return redirect(url_for("message_detail", message_index=comment_parent))
    if not comment.owner == current_user.index:
        flash("发生错误，请重试")
        return redirect(url_for("message_detail", message_index=comment_parent))
    db.session.delete(comment)
    db.session.commit()
    # 提交删除指令和返回成功信息
    flash("删除成功")
    return redirect(url_for("message_detail", message_index=comment_parent))


@app.route("/user_message/<int:user_index>", methods=["GET"])
@login_required
def user_message(user_index):
    """
    GET: 用户发送的消息页面 \n
    """
    # 检查用户是否存在
    user = User.query.filter(User.index == user_index).first()
    if not user:
        flash("用户不存在")
        return redirect(url_for("message_list"))
    is_current_user = user.index == current_user.index
    info = f"{user.username}的消息"
    # 获取消息
    per_page = 30
    page = request.args.get("page", 1, type=int)
    columns = [Message.index, Message.time, Message.title, Message.owner, User.username]
    messages = (
        Message.query.join(User, Message.owner == User.index)  # 合并两个数据表
        .filter(Message.owner == user_index)  # 过滤用户
        .with_entities(*columns)  # 选择所需要的列
        .order_by(Message.time.desc())  # 按照时间排序
        .paginate(page, per_page, error_out=False)  # 进行分页
    )
    data = dict(messages=messages, info=info, is_current_user=is_current_user)
    return render_template("message/message_list.html", **data)


@app.route("/user_comment/<int:user_index>", methods=["GET"])
@login_required
def user_comment(user_index):
    """
    GET: 用户发送的评论页面 \n
    """
    # 检查用户是否存在
    user = User.query.filter(User.index == user_index).first()
    if not user:
        flash("用户不存在")
        return redirect(url_for("message_list"))
    info = f"{user.username}的评论"
    # 获取消息
    per_page = 30
    page = request.args.get("page", 1, type=int)
    columns = [
        Comment.index,
        Comment.time,
        Comment.owner,
        Comment.text,
        Comment.parent_massage,
        User.username,
        Message.title,
    ]
    comments = (
        Comment.query.join(User, Comment.owner == User.index)  # 合并两个数据表
        .join(Message, Message.index == Comment.parent_massage)
        .filter(Comment.owner == user_index)  # 过滤用户
        .with_entities(*columns)  # 选择所需要的列
        .order_by(Comment.time.desc())  # 按照时间排序
        .paginate(page, per_page, error_out=False)  # 进行分页
    )
    return render_template("message/comment_list.html", comments=comments, info=info)


@app.route("/favorite_message_list/<int:user_index>", methods=["GET"])
@login_required
def favorite_message_list(user_index):
    """
    GET: 用户发送的消息页面 \n
    """
    # 检查用户是否存在
    user = User.query.filter(User.index == user_index).first()
    if not user:
        flash("用户不存在")
        return redirect(url_for("message_list"))
    info = f"{user.username}喜欢的消息"
    # 获取消息
    per_page = 30
    page = request.args.get("page", 1, type=int)
    columns = [Message.index, Message.time, Message.title, Message.owner, User.username]
    messages = (
        Message.query.join(User, Message.owner == User.index)
        .join(FavoriteMessage, FavoriteMessage.message_id == Message.index)
        .filter(FavoriteMessage.user_id == user_index)  # 过滤用户
        .with_entities(*columns)  # 选择所需要的列
        .order_by(Message.time.desc())  # 按照时间排序
        .paginate(page, per_page, error_out=False)  # 进行分页
    )
    data = dict(messages=messages, info=info, is_current_user=False)
    return render_template("message/message_list.html", **data)


@app.route("/favorite_message/<int:user_index>/<int:message_index>", methods=["GET"])
def favorite_message(user_index, message_index):
    # 检查用户和消息是否存在
    user = User.query.filter(User.index == user_index).first()
    if not user:
        flash("发生错误，请重试（用户不存在）")
        return redirect(url_for("message_detail", message_index=message_index))
    message = Message.query.filter(Message.index == message_index).first()
    if not message:
        flash("发生错误，请重试（用户不存在）")
        return redirect(url_for("message_detail", message_index=message_index))
    # 检查是否已经喜欢该消息
    data = dict(message_id=message_index, user_id=user_index)
    favorite = FavoriteMessage.query.filter_by(**data).first()
    if favorite:
        flash("已取消点赞")
        db.session.delete(favorite)
    else:
        flash("已点赞消息")
        db.session.add(FavoriteMessage(**data))
    db.session.commit()
    return redirect(url_for("message_detail", message_index=message_index))
