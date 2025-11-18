### **[G2G]** 백엔드 레포지토리
> 프로젝트의 백엔드 시스템을 Django와 DRF로 구축합니다.

## 🏗️ 시스템 아키텍처 (System Architecture)
프로젝트의 백엔드, 인프라, 배포 구성을 나타내는 다이어그램입니다.


#### 기술 스택
* **Python**: 3.13 (또는 현재 사용 버전)
* **Django**: 5.2.7 (또는 현재 사용 버전)
* **Django REST Framework**: 3.16.1
* **Authentication**: OAuth2 / JWT
* **Database**: SQLite (개발용), PostgreSQL (프로덕션용)

### ⚙️ Infrastructure & Deployment
* **Poetry**: 의존성 관리 및 가상 환경
* **Docker**: 컨테이너화
* **Nginx**: 리버스 프록시
* **AWS**: EC2, RDS (클라우드 인프라)
* **GitHub Actions**: CI/CD 파이프라인

### Development Tools
PyCharm: IDE<br>
Git: 버전 관리<br>
Postman: API 테스트<br>

### 빠른 시작
#### 1. 저장소 클론
```
git clone https://github.com/OZ-13-G2G-team2/backend.git
cd backend
```
#### 2. Poetry 설치 및 의존성 설치
```
# Poetry 설치 (없는 경우)
curl -sSL https://install.python-poetry.org | python3 -

# 의존성 설치
poetry install
```
#### 3. 환경변수 설정
```
# .env 파일 내용 (로컬 개발용)
SECRET_KEY=your-super-secret-key-here
DEBUG=True
USE_S3_STORAGE=False
```
#### 4. 데이터베이스 마이그레이션
```
poetry run python manage.py migrate --settings=config.dev
```
#### 5. 개발 서버 실행
```
poetry run python manage.py runserver --settings=config.settings.dev
```
http://127.0.0.1:8000 에서 확인 가능!

#### 6. API 문서 확인
개발 서버 실행 후 아래 주소에서 Swagger UI 문서를 확인합니다.<br>
http://127.0.0.1:8000/docs/



## 팀원 필수 체크리스트<hr>
### 첫 설정 시 확인사항<br>
Poetry 설치 완료<br>
.env 파일 생성 완료<br>
poetry install 성공<br>
Poetry로만 패키지 설치 (pip 사용 금지)<br>
개발 서버 정상 실행 (runserver)<br>
http://127.0.0.1:8000/admin/ 접속 가능<br>
http://127.0.0.1:8000/api/ DRF 화면 확인<br>
### 브랜치 작업 전 체크리스트<br>
git pull origin develop 최신 코드 받기<br>
feature/기능명 형식으로 브랜치 생성<br>
커밋 메시지 규칙 준수<br>
PR 생성 전 충돌 해결

## 프로젝트 구조
```
.
├── Dockerfile
├── README.md
├── app
│   ├── __init__.py
│   ├── address
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── carts
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── orders
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   ├── migrations
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── order_items.py
│   │   │   └── orders.py
│   │   ├── permissions.py
│   │   ├── serializers
│   │   │   ├── __init__.py
│   │   │   ├── order_item_serializer.py
│   │   │   └── order_serializer.py
│   │   ├── services
│   │   │   ├── __init__.py
│   │   │   ├── order_item_service.py
│   │   │   └── order_service.py
│   │   ├── signals.py
│   │   ├── tests
│   │   ├── urls.py
│   │   ├── utils.py
│   │   └── views
│   │       ├── __init__.py
│   │       ├── order_item_view.py
│   │       └── order_view.py
│   ├── products
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── signals.py
│   │   ├── tests
│   │   ├── urls.py
│   │   └── views.py
│   ├── reviews
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── sellers
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── user_auth
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── tests
│   │   ├── urls.py
│   │   ├── utils.py
│   │   └── views.py
│   ├── users
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations
│   └── wishlists
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── migrations
│       ├── models.py
│       ├── serializers.py
│       ├── tests.py
│       ├── urls.py
│       └── views.py
├── ci_db
├── config
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── urls.py
│   └── wsgi.py
├── docker-compose.yml
├── logs
│   └── app.log
├── manage.py
├── poetry.lock
├── pyproject.toml
├── pytest.ini
└── scripts
    └── run.sh
```
## 🔧 개발 가이드
### 환경별 설정<br>
개발 환경 (dev)<br>
- SQLite 데이터베이스 사용<br>
- DEBUG = True<br>
- REST API 권한: AllowAny<br>
- 정적 파일: 로컬 서빙<br>
- Django runserver

### 프로덕션 환경 (prod)<br>
- PostgreSQL 데이터베이스 사용<br>
- DEBUG = False<br>
- 보안 설정 강화
- Gunicorn/uWSGI + Nginx 기반


## ⚠️의존성 관리 (중요!)
✅ 올바른 방법: poetry add package-name<br>
❌ 금지된 방법: pip install package-name


## 브랜치 활동

### 지점구조
- main: 활동용 배포 브랜치
- develop: 개발 통합 지점
- feature/*: 기능 개발용 지점

### Poetry를 사용하는 이유:

- 의존성 버전 충돌 자동 해결
- pyproject.toml과 poetry.lock으로 정확한 버전 관리
- 팀원 간 동일한 환경 보장
- 가상환경 자동 관리


### API 개발
REST API는 Django REST Framework를 사용합니다:

* **API Base URL**: `/api/`
* **Swagger UI (API 문서)**: `/docs/`
* **API Schema (OpenAPI)**: `/api/schema/`
* **Admin Panel**: `/admin/`

## 🌿 브랜치 전략

### 브랜치 구조
- main: 프로덕션 배포용 브랜치
- develop: 개발 통합 브랜치
- feat/*: 기능 개발용 브랜치

### 워크플로우
1. develop 브랜치에서 feat/기능명브랜치 생성
2. 개발이 완료 후 develop으로 PR 생성
3. 코드 리뷰 후 develop에 머지
4. develop에서 테스트 완료 후 main머지

### 코드 작업중에 팀원이 pr요청 -> 원격 develop 브랜치가 최신화 되었을때

1. develop 브랜치 최신화 하기(develop브랜치에서 실행)
 ```
 git fetch origin
 ```
 2. 원격 develop 내용 가져오기
 ```
 git pull origin develop
 ```
3. migrate
```
python manage.py migrate
```
4. 작업 브랜치로 이동
```
git switch <작업브랜치명>
```
5. 최신 내역으로 최신화(최신화한 develop 내용을 rebase합니다.)
```
git rebase develop
```


### 4.Pull Request
PR시 수정에 대한 상세한 설명 작성
스크린샷 첨부 (UI 변경 시)
커밋 메시지 규칙
feat: 새로운 기능
fix: 버그 수정
docs: 문서 수정
style: 코드 스타일 변경
refactor: 코드 리팩토링
test: 테스트 추가/수정
chore: 빌드 및 설정 변경