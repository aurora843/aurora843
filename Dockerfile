# 공식 Rasa 이미지를 확장합니다. (rasa CLI를 포함하는 이미지)
FROM rasa/rasa:latest 
# 혹은 특정 Rasa 코어 버전에 맞춰서: FROM rasa/rasa:3.x.x (예: rasa/rasa:3.8.1)

# 작업 디렉토리를 /app으로 설정합니다.
WORKDIR /app

# 커스텀 액션 코드를 컨테이너에 복사합니다.
COPY ./actions /app/actions

# 필요한 경우, 추가 요구사항 파일을 복사하고 설치합니다.
COPY actions/requirements.txt ./

# root 사용자로 전환하여 권한 문제 해결
USER root
RUN pip install --no-cache-dir -r requirements.txt
USER rasa 

# 액션 서버를 시작합니다.
CMD ["rasa", "run", "actions", "--port", "5055"]