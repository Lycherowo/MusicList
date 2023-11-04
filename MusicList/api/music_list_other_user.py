"""
保存了查看他人歌单的操作。\n
包括：查看他人歌单列表；查看他人歌单详情；收藏歌单，取消收藏歌单和查看收藏的歌单。
"""

from flask import flash, redirect, url_for, render_template
from flask_login import current_user, login_required

from MusicList import app, db
from MusicList.model import User, Music, List, MusicList, FavoriteList


@app.route("/user_lists/<int:user_index>", methods=["GET"])
@login_required
def user_lists(user_index):
    """
    GET: 非当前用户的歌单列表
    """
    if user_index == current_user.index:
        return redirect(url_for("music_lists"))
    user = User.query.filter(User.index == user_index).first()
    # 检查用户是否存在
    if not user:
        flash("用户不存在")
        return redirect(url_for("index"))
    lists = List.query.filter_by(owner=user_index, share=1).all()
    return render_template("music_list_other_user/user_lists.html", lists=lists[::-1])


@app.route("/user_list_detail/<int:list_index>", methods=["GET", "POST"])
@login_required
def user_list_detail(list_index):
    # 获取歌单
    music_list = List.query.filter(List.index == list_index).first()
    if not music_list:
        flash("发生错误，请重试（歌单不存在）")
        return redirect(url_for("index"))
    if music_list.owner == current_user.index:
        return redirect(url_for("list_detail"))
    # 获取音乐
    musics = (
        Music.query.join(MusicList, MusicList.music_id == Music.index)
        .filter(MusicList.list_id == list_index)
        .all()
    )
    # 获取收藏情况
    favorite_list = (
        FavoriteList.query.filter(FavoriteList.list_id == list_index)
        .filter(FavoriteList.user_id == current_user.index)
        .first()
    )
    favorite = False
    if favorite_list:
        favorite = True
    # 返回页面
    data = dict(musics=musics, list=music_list, favorite=favorite)
    return render_template("music_list_other_user/user_list_detail.html", **data)


@app.route("/favorite_music_lists/<int:user_index>", methods=["GET"])
@login_required
def favorite_music_lists(user_index):
    """
    `GET`: 用户收藏的歌单的列表 \n
    """
    # 检查用户是否存在
    user = User.query.filter(User.index == user_index).first()
    if not user:
        flash("用户不存在")
        return redirect(url_for("message_list"))
    info = f"{user.username}收藏的歌单"
    # 获取歌单
    columns = [List.index, List.list_name, User.username]
    music_lists = (
        List.query.join(User, User.index == List.owner) # 连接 User 表获取用户名
        .join(FavoriteList, FavoriteList.list_id == List.index) # 连接 FavoriteList 表，以供筛选收藏
        .filter(FavoriteList.user_id == user_index)  # 过滤用户
        .with_entities(*columns)  # 选择所需要的列
        .all()
    )
    data = dict(music_lists=music_lists, info=info)
    return render_template("music_list_other_user/favorite_music_lists.html", **data)


@app.route("/favorite_music_list/<int:user_index>/<int:list_index>", methods=["GET"])
def favorite_music_list(user_index, list_index):
    """
    `GET`: 收藏和取消歌单 API
    """
    # 检查是否已经收藏该歌单
    data = dict(list_id=list_index, user_id=user_index)
    favorite = FavoriteList.query.filter_by(**data).first()
    if favorite:
        flash("已取消收藏")
        db.session.delete(favorite)
        db.session.commit()
        return redirect(url_for("user_list_detail", list_index=list_index))
    # 检查歌单是否存在
    music_list = List.query.filter(List.index == list_index).first()
    if not music_list:
        flash("发生错误，请重试（歌单不存在）")
        return redirect(url_for("index", list_index=list_index))
    if music_list.share == 0:
        flash("发生错误，请重试（歌单未公开）")
        return redirect(url_for("index", list_index=list_index))
    if music_list.owner == current_user.index:
        flash("不能收藏自己的歌单")
        return redirect(url_for("message_detail", message_index=list_index))
    # 检查用户是否存在
    user = User.query.filter(User.index == user_index).first()
    if not user:
        flash("发生错误，请重试（用户不存在）")
        return redirect(url_for("user_list_detail", list_index=list_index))
    db.session.add(FavoriteList(**data))
    db.session.commit()
    flash("已收藏歌单")
    return redirect(url_for("user_list_detail", list_index=list_index))
