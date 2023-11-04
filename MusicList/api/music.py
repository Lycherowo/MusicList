"""
包含了与搜索歌曲相关的页面和操作。\n
包括：搜索歌曲的页面和结果页面；添加歌曲；歌曲详情。
"""

from flask import request, flash, redirect, url_for, render_template
from flask_login import current_user, login_required

from MusicList import app, db
from MusicList.model import Music, List


@app.route("/search_music", methods=["GET", "POST"])
@login_required
def search_music():
    """
    GET: 歌曲搜索页面 \n
    POST: 搜索歌曲
    """
    if request.method == "GET":
        per_page = 30  # 每页中最大内容数
        page = request.args.get("page", 1, type=int)
        musics = Music.query.order_by(Music.index.desc()).paginate(
            page, per_page, error_out=False
        )
        return render_template("music_list/search_music.html", musics=musics)
    elif request.method == "POST":
        keyword = request.form.get("keyword")
        if not keyword:
            flash("请输入搜索词")
            return render_template("music_list/search_music.html")
        return redirect(url_for("search_result", keyword=keyword))


@app.route("/search_result/<string:keyword>", methods=["GET", "POST"])
@login_required
def search_result(keyword):
    """
    GET: 歌曲搜索结果页面 \n
    POST: 添加歌曲
    """
    if request.method == "GET":
        musics = Music.query.filter(Music.music_name == keyword).all()
        data = dict(keyword=keyword, musics=musics)
        return render_template("music_list/search_result.html", **data)
    elif request.method == "POST":
        # 从前端获取数据
        music_name = request.form.get("music_name")
        artist = request.form.get("artist")
        link = request.form.get("link")
        if not music_name or not artist or music_name == "" or artist == "":
            flash("请输入完整的歌曲信息")
            return redirect(url_for("search_result", keyword=keyword))
        if not link:
            link = ""
        # 检查歌曲是否已经存在
        music_info = dict(music_name=music_name, artist=artist, link=link)
        if Music.query.filter_by(**music_info).first() is not None:
            flash("歌曲信息已存在")
            return redirect(url_for("search_result", keyword=keyword))
        # 添加歌曲
        db.session.add(Music(**music_info))
        db.session.commit()
        return redirect(url_for("search_result", keyword=keyword))


@app.route("/music_detail/<int:index>", methods=["GET"])
@login_required
def music_detail(index):
    """
    GET: 歌曲详情页面；页面中也可以将歌曲添加到列表
    """
    music = Music.query.filter(Music.index == index).first()
    lists = List.query.filter_by(owner=current_user.index).all()
    data = dict(music=music, lists=lists[::-1])
    if not music:
        flash("歌曲不存在")
        return redirect(url_for("search_music"))
    return render_template("music_list/music_detail.html", **data)
