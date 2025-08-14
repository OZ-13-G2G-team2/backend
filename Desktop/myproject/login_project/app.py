from flask import Flask, jsonify, render_template, request, make_response
from routes.user import user_bp
from routes.admin import admin_bp

app =Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', name = "승현")

@app.route('/set')
def set_cookie():
    # 쿠키 설정 완료라는 내용이 담길 응답 (편집) 먼저 만들기
    resp = make_response("쿠키 설정 완료")

    # 그 응답에 'username'이라는 이름의 쿠키(도장 카드)를 붙여서 보낸다.
    resp.set_cookie('username','kim')
    return resp

@app.route('/get')
def get_cookie():
    # 사용자의 요청에 붙어있는 쿠키 확인
    username = request.cookies.get('username')
    return f'지갑에서 꺼낸 쿠키: {username}'




if __name__ == '__main__':
    app.run(debug=True)