"""保存了与用户相关的操作的 API，如注册、登录、查看和更改信息、登出等。"""

from flask import request, flash, redirect, url_for, render_template
from flask_login import current_user, login_required, login_user, logout_user

from MusicList import app, db
from MusicList.model import User


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("users/login.html")
    elif request.method == "POST":
        # 从前端获取数据
        username = request.form.get("username")
        password = request.form.get("password")
        if not password or not username:
            flash("用户名和密码不能为空")
            return redirect(url_for("login"))
        # 从数据库中获取用户
        user = User.query.filter(User.username == username).first()
        # 检查密码是否正确
        if not user or not user.validate_password(password):
            flash("用户名或密码错误")
            return redirect(url_for("login"))
        # 进行登录，返回成功信息，跳转页面
        login_user(user)
        flash(f"{username}登录成功")
        return redirect(url_for("index"))


@app.route("/logout")
@login_required
def logout():
    """POST 用户登出"""
    logout_user()
    flash("登出成功")
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    `GET`: 注册页面 \n
    `POST`: 注册用户
    """
    if request.method == "GET":
        return render_template("users/register.html")
    elif request.method == "POST":
        # 从前端获取数据
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        if not username or not password or not confirm_password:
            flash("请输入用户名和密码")
            return redirect(url_for("register"))
        if not password == confirm_password:
            flash("两次输入的密码不一致")
            return redirect(url_for("register"))
        # 检查用户名是否重复
        if User.query.filter(User.username == username).first() is not None:
            flash("用户名已被占用，请更换新的用户名。")
            return redirect(url_for("register"))
        # 将用户信息添加到数据库中
        user = User(username=username, password="", level=0)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        # 返回成功信息，跳转页面
        flash("成功注册，正在返回登录页面")
        return redirect(url_for("login"))


@app.route("/user_info", methods=["GET"])
@login_required
def user_info():
    """`GET`: 用户信息页面"""
    return render_template("users/user_info.html")

@app.route("/other_user_info/<int:user_index>", methods=["GET"])
@login_required
def other_user_info(user_index):
    user = User.query.filter(User.index == user_index).first()
    # 检查用户是否存在
    if not user:
        flash("用户不存在")
        return redirect(url_for("index"))
    # 检查用户是否为当前用户
    if user_index == current_user.index:
        return redirect(url_for("user_info"))
    return render_template("users/other_user_info.html", user=user)


@app.route("/change_password", methods=["POST"])
@login_required
def change_password():
    """`POST`: 更改密码"""
    # 从前端获取数据
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")
    if not password or not confirm_password:
        flash("请输入想要更改的密码")
        return redirect(url_for("user_info"))
    # 检查两次输入的密码是否一致
    if password == confirm_password:
        flash("两次输入的密码不一致")
        return redirect(url_for("user_info"))
    # 更改当前用户的密码
    current_user.set_password(password)
    db.session.commit()
    # 返回成功信息
    flash("密码更改成功")
    return redirect(url_for("index"))


@app.route("/change_username", methods=["POST"])
@login_required
def change_username():
    """`POST`: 更改用户名"""
    username = request.form.get("username")
    if not username:
        flash("请输入想要更改的用户名")
        return redirect(url_for("user_info"))
    if current_user.username == username:
        flash("新用户名和旧用户名相同")
        return redirect(url_for("user_info"))
    # 检查用户名是否重复
    if User.query.filter(User.username == username).first() is not None:
        flash("用户名已被占用，请更换新的用户名")
        return redirect(url_for("user_info"))
    # 更改用户名
    current_user.username = username
    db.session.commit()
    # 跳转到主页
    return redirect(url_for("user_info"))
