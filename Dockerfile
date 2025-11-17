# 베이스 이미지
FROM python:3.13-slim

# EC2 사용자 생성 (컨테이너 내부 사용자 생성용)
RUN useradd -m ec2-user
USER ec2-user
ENV HOME=/home/ec2-user
# 작업 디렉토리 설정
WORKDIR /app

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="$HOME/.local/bin:$PATH" \
    POETRY_VIRTUALENVS_IN_PROJECT=False \
    POETRY_NO_INTERACTION=1 \
    POETRY_HOME="$HOME/.local" \
    POETRY_BIN=$HOME/.local/bin/poetry \
    DJANGO_SETTINGS_MODULE=config.settings.prod

# 시스템 필수 패키지 설치 (Poetry 설치 및 빌드 도구)
# 시스템 패키지는 root 권한으로 설치
USER root
RUN apt-get update \
 && apt-get install -y \
    curl build-essential \
    libpq-dev \
    --no-install-recommends \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# 다시 ec2-user로 전환
USER ec2-user

# Poetry 설치
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && chmod +x $HOME/.local/bin/poetry \
    && poetry --version

# pyproject.toml & poetry.lock 복사 후 의존성 설치
COPY --chown=ec2-user:ec2-user pyproject.toml poetry.lock* ./

# Poetry 의존성 설치 (루트 패키지는 설치하지 않음)
RUN $POETRY_BIN config virtualenvs.create false \
    && $POETRY_BIN install --no-interaction --no-ansi --no-root

# 앱 코드 및 실행 스크립트 복사
COPY --chown=ec2-user:ec2-user . /app

# 실행 스크립트 권한 부여
RUN chmod +x /app/scripts/run.sh

# 정적 파일 저장용 디렉토리 (collectstatic용)
RUN mkdir -p /home/ec2-user/vol/web/static /home/ec2-user/vol/web/media \
    && chmod 755 /home/ec2-user/vol/web

# 로그 디렉토리 생성
RUN mkdir -p /app/logs && chmod 755 /app/logs

# 포트 설정
EXPOSE 8000

CMD ["/app/scripts/run.sh"]

