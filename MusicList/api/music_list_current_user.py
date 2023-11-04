"""
保存了查看自身歌单的操作。\n
包括：添加和删除歌单；更改歌单私密性；查看当前用户歌单列表；查看当前用户歌单详情；将歌曲从列表中添加和删除。
"""

from flask import request, flash, redirect, url_for, render_template
from flask_login import current_user, login_required

from MusicList import app, db
from MusicList.model import User, Music, List, MusicList, FavoriteList


@app.route("/my_lists", methods=["GET", "POST"])
@login_required
def music_lists():
    """
    GET: 用户歌单列表页面 \n
    POST: 添加歌单
    """
    if request.method == "GET":
        lists = List.query.filter_by(owner=current_user.index).all()
        return render_template("music_list/my_lists.html", lists=lists[::-1])
    elif request.method == "POST":
        # 从前端获得数据
        list_name = request.form.get("list_name")
        if not list_name:
            flash("请输入歌单名称")
            return redirect(url_for("music_lists"))
        # 检查是否已存在同名歌单
        existed_list = List.query.filter_by(
            owner=current_user.index, list_name=list_name
        ).first()
        if existed_list is not None:
            flash("歌单已存在，请更改歌单名称")
            return redirect(url_for("music_lists"))
        # 新建歌单
        new_list = List(owner=current_user.index, list_name=list_name, share=0)
        db.session.add(new_list)
        db.session.commit()
        flash("添加成功")
        return redirect(url_for("music_lists"))


@app.route("/list_detail/<int:list_index>", methods=["GET", "POST"])
@login_required
def list_detail(list_index):
    """
    GET: 歌单详细信息页面 \n
    POST: 更改歌单名称操作 \n
    """
    if request.method == "GET":
        # 检查列表是否正确
        music_list = List.query.filter(List.index == list_index).first()
        if music_list is None:
            flash("发生错误，请重试（歌单不存在）")
            return redirect(url_for("music_lists"))
        if music_list.share == 0 and not music_list.owner == current_user.index:
            flash("发生错误，请重试（歌单未公开）")
            return redirect(url_for("music_lists"))
        # 获取歌曲并返回
        musics = (
            Music.query.join(MusicList, MusicList.music_id == Music.index)
            .filter(MusicList.list_id == list_index)
            .all()
        )
        return render_template(
            "music_list/list_detail.html", musics=musics, list=music_list
        )
    elif request.method == "POST":
        # 获取表单数据
        list_name = request.form.get("list_name")
        list_index = request.form.get("list_index")
        if not list_index:
            flash("发生错误，请重试（歌单序号为空）")
            return redirect(url_for("music_lists"))
        if not list_name:
            flash("请输入歌单名称")
            return redirect(url_for("list_detail", list_index=list_index))
        # 获取和检查列表
        this_list = List.query.filter_by(index=list_index).first()
        if not this_list.owner == current_user.index:
            flash("发生错误，请重试（操作的歌单与当前用户不符）")
            return redirect(url_for("music_lists"))
        if this_list.list_name == list_name:
            flash("新名称和和原名称不能一致")
            return redirect(url_for("list_detail", list_index=list_index))
        # 检查新歌单名是否与其他列表重复
        all_list = List.query.filter_by(
            owner=current_user.index, list_name=list_name
        ).first()
        if all_list is not None:
            flash("歌单已存在")
            return redirect(url_for("list_detail", list_index=list_index))
        # 进行更改
        this_list.list_name = list_name
        db.session.commit()
        flash("更改成功")
        return redirect(url_for("list_detail", list_index=list_index))


@app.route("/add_music_to_list/<int:music_id>/<int:list_id>", methods=["GET"])
@login_required
def add_music_to_list(music_id, list_id):
    """
    GET: 将歌曲添加到列表
    """
    # 检测列表的正确性
    music_list = List.query.filter(List.index == list_id).first()
    if music_list is None or not music_list.owner == current_user.index:
        flash("发生错误，请重试（操作的歌单不存在或操作的歌单与当前用户不符）")
        return redirect(url_for("music_detail", index=music_id))
    # 检测歌曲的正确性
    music = Music.query.filter(Music.index == music_id).first()
    if music is None:
        flash("歌曲不存在")
        return redirect(url_for("music_detail", index=music_id))
    # 检测歌曲是否已经存在
    record = MusicList.query.filter_by(music_id=music_id, list_id=list_id).first()
    if record is not None:
        flash("歌曲已经存在于列表中")
        return redirect(url_for("music_detail", index=music_id))
    # 添加记录
    record = MusicList(music_id=music_id, list_id=list_id)
    db.session.add(record)
    db.session.commit()
    flash("添加成功")
    return redirect(url_for("music_detail", index=music_id))


@app.route("/delete_list/<int:list_index>", methods=["GET"])
@login_required
def delete_list(list_index):
    """
    GET: 删除列表
    """
    # 检测列表的正确性
    music_list = List.query.filter(List.index == list_index).first()
    if music_list is None or not music_list.owner == current_user.index:
        flash("发生错误，请重试（操作的歌单不存在或操作的歌单与当前用户不符）")
        return redirect(url_for("music_lists"))
    # 删除列表中的所有歌曲
    db.session.query(MusicList).filter(list_index == list_index).delete()
    # 删除列表
    db.session.delete(music_list)
    db.session.commit()
    flash("删除成功")
    return redirect(url_for("music_lists"))


@app.route(
    "/delete_music_from_list/<int:music_index>/<int:list_index>", methods=["GET"]
)
@login_required
def delete_music_from_list(music_index, list_index):
    """
    GET: 从列表中删除歌曲
    """
    # 检测列表的正确性
    music_list = List.query.filter(List.index == list_index).first()
    if music_list is None or not music_list.owner == current_user.index:
        flash("发生错误，请重试（操作的歌单不存在或操作的歌单与当前用户不符）")
        return redirect(url_for("list_detail", list_index=list_index))
    # 检查歌曲的正确性...算了，检查个der
    # 检查歌曲是否在列表里
    record = MusicList.query.filter_by(list_id=list_index, music_id=music_index).first()
    if record is None:
        flash("发生错误，请重试（歌曲不在列表中）")
        return redirect(url_for("list_detail", list_index=list_index))
    # 删除记录
    db.session.delete(record)
    db.session.commit()
    flash("删除成功")
    return redirect(url_for("list_detail", list_index=list_index))


@app.route("/change_privacy/<int:list_index>", methods=["GET"])
@login_required
def change_privacy(list_index):
    """
    GET: 更改歌单私密性
    """
    music_list = List.query.filter(List.index == list_index).first()
    if music_list is None or not music_list.owner == current_user.index:
        flash("发生错误，请重试")
        return redirect(url_for("list_detail", list_index=list_index))
    # 更改私密性
    if music_list.share != 0:
        FavoriteList.query.filter(FavoriteList.list_id == music_list.index).delete()
        music_list.share = 0
    elif music_list.share != 1:
        music_list.share = 1
    db.session.commit()
    return redirect(url_for("list_detail", list_index=list_index))
