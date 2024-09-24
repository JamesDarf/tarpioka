# 사용할 베이스 이미지
FROM python:slim

# pip 업그레이드 및 Flask 설치
RUN pip install --upgrade pip
RUN pip install Flask
ENV TZ Asia/Seoul

# requirements.txt를 컨테이너로 복사하고, 필요한 패키지 설치
COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 작업 디렉토리 설정
WORKDIR /chal
# flag 파일 및 소스 코드 복사
COPY --chmod=444 flag ./



# 일반 유저로 실행
RUN groupadd -g 999 appuser
RUN useradd -r -u 999 -g appuser appuser

USER appuser

COPY --chown=appuser:appuser ./src/ /chal/
COPY --chown=appuser:appuser ./app.log ./

# 8000번 포트 노출
EXPOSE 8000

# 컨테이너가 시작될 때 실행할 명령어
CMD ["python3", "app.py"]
