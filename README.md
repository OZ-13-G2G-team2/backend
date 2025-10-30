#### 기술 스택
Backend<br>
Python: 3.13<br>
Django: 5.2.7<br>
Django REST Framework: 3.16.1<br>
PostgreSQL: 프로덕션 데이터베이스<br>
SQLite: 개발 데이터베이스

### Infrastructure
Poetry: 의존성 관리
Django runserver: 현재 서버 (개발/테스트용)
GitHub Actions: CI/CD 파이프라인

### Development Tools
PyCharm: IDE
Git: 버전 관리
Postman: API 테스트 (권장)

### 빠른 시작
1. 저장소 클론
```
git clone https://github.com/OZ-13-G2G-team2/backend.git
cd backend
```
2. Poetry 설치 및 의존성 설치
```
# Poetry 설치 (없는 경우)
curl -sSL https://install.python-poetry.org | python3 -

# 의존성 설치
poetry install
```
3. 환경변수 설정
```
# .env 파일 내용 (로컬 개발용)
SECRET_KEY=your-super-secret-key-here
DEBUG=True
USE_S3_STORAGE=False
```
4. 데이터베이스 마이그레이션
```
poetry run python manage.py migrate --settings=config.settings
```
5. 개발 서버 실행
```
poetry run python manage.py runserver --settings=config.settings.dev
```
http://127.0.0.1:8000 에서 확인 가능!



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
backend/
├── README.md
├── config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── db.sqlite3
├── manage.py
├── media 
├── orders
│   ├── __init__.py
│   ├── __pycache__
│   ├── admin.py
│   ├── apps.py
│   ├── migrations
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── poetry.lock
├── products
│   ├── __init__.py
│   ├── __pycache__
│   ├── admin.py
│   ├── apps.py
│   ├── migrations
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── pyproject.toml
└── users
    ├── __init__.py
    ├── __pycache__
    ├── admin.py
    ├── apps.py
    ├── migrations
    ├── models.py
    ├── tests.py
    └── views.py
```
## 🔧 개발 가이드
### 환경별 설정<br>
개발 환경 (dev)<br>
- SQLite 데이터베이스 사용<br>
- DEBUG = True<br>
- REST API 권한: AllowAny<br>
- 정적 파일: 로컬 서빙<br>

### 프로덕션 환경 (prod)<br>
- PostgreSQL 데이터베이스 사용 (SSL 비활성화)<br>
- S3 Object Storage 연동<br>
- Django runserver 사용 (IP 접근)<br>
- 보안 설정 강화


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

- **Base** URL: /api/
- **API v1**: /api/v1/
- **Admin Panel**: /admin/
- **API Auth**: /api-auth/
- **Token Auth**: /api/token/

## 🌿 브랜치 전략

### 브랜치 구조
- main: 프로덕션 배포용 브랜치
- dev: 개발 통합 브랜치
- feature/*: 기능 개발용 브랜치

### 워크플로우
1. develop 브랜치에서 feature/기능명브랜치 생성
2. 개발이 완료 후 develop으로 PR 생성
3. 코드 리뷰 후 develop에 머지
4. develop에서 테스트 완료 후 main머지

### 코드 작업중에 팀원이 pr요청 -> 원격 develop 브랜치가 최신화 되었을때

1. 내가 작업하던 브랜치에 최신화된 원격 기록 가져오기
 ```
 git fetch origin
 ```
 2. 원격 develop rebase
 ```
 git rebase origin develop
 ```
3. 로컬 develop 브랜치로 이동
```
git switch develop
```
4. 원격 내용으로 최신화
```
git pull origin develop
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