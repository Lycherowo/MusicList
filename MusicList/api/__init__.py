"""主页，以及导入其他页面。"""

from flask import request, render_template

from MusicList import app


@app.route("/", methods=["GET", "POST"])
def index():
    """主页"""
    if request.method == "GET":
        return render_template("index.html")


from MusicList.api import (
    errors,
    user,
    music,
    message,
    music_list_current_user,
    music_list_other_user,
)
