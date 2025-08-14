from flask import Blueprint, render_template

# blueprint -> 객체 생성
# 'user'는 bluprint 이름, __name__은 현재 파일 이름, url_prefix는 접두 경로

user_bp = Blueprint('user', __name__, url_prefix='/user')

# 라우터 정의
@user_bp.route('/<username>')
def profile(username):
    return render_template('kuser.html', username=username)
