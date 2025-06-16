## Rasa를 이용한 성화학숙 챗봇

📖 프로젝트 소개
본 프로젝트는 기존 '성화학숙 앱'을 유학생을 포함한 모든 학생들을 위한 **'통합 스마트 생활 플랫폼'**으로 고도화하는 것을 목표로 진행한 애플리케이션 개발 과제입니다. 분산되어 있던 정보 채널과 소통 창구를 하나로 통합하여, 학생들의 기숙사 생활 만족도를 높이고 행정 업무의 효율성을 증대시키고자 했습니다.

✨ 주요 기능
🎨 UI/UX 전면 개편

현대적이고 직관적인 디자인 적용
사용 편의성을 고려한 탐색 구조 및 레이아웃 개선
다크 모드 및 개인화 테마 기능
💬 커뮤니티 및 소통 강화

실시간 1:1 및 그룹 메신저 기능
페이스북 그룹 형태의 소모임 공간
학생 참여형 익명 게시판 및 이벤트 캘린더
ኑ 생활 편의 증진

공용 주방 실시간 이용 현황 공유 및 예약
각종 행정 서류를 다운로드할 수 있는 문서 보관소
실시간 푸시 알림 (공지, 메시지 등)
🤖 지능형 정보 지원

Rasa 기반 AI 챗봇: 24시간 규칙, 연락처 등 문의에 자동 응답
FAQ, 아산 탐방, 선문대 소개 등 생활 정보 콘텐츠 제공
다국어 번역 및 지역화(Localization)를 통한 언어 장벽 해소
🛠️ 기술 스택
분야	주요 기술
Frontend	Flutter, Android Studio
Backend	Python, Flask, MySQL
AI Chatbot	Rasa, KoNLPy, Googletrans
개발 환경	Anaconda, Git, GitHub

Sheets로 내보내기
🏗️ 시스템 아키텍처
본 시스템은 역할에 따라 명확하게 분리된 마이크로서비스 아키텍처를 기반으로 설계되었습니다.

(여기에 직접 만드신 시스템 구성도 다이어그램 이미지를 추가하세요. 예: ![시스템 구성도](path/to/diagram.png))

Rasa 서버 (5005): NLU 및 대화 관리를 담당하는 챗봇의 핵심 두뇌
액션 서버 (5055): DB 조회 등 복잡한 로직을 수행하는 actions.py 실행
이미지 서버 (8080): Flask 기반으로 구축된 독립 이미지 제공 서버
데이터베이스: MySQL을 통해 chatbot(연락처), rules_data(규칙), images(이미지 정보) 등 모든 데이터를 영속적으로 관리
⚙️ 설치 및 시작하기
사전 요구사항
Flutter & Android Studio
Anaconda (or Miniconda) & Python 3.10
MySQL Server
1. 프로젝트 클론
Bash

git clone https://github.com/your-username/your-repository.git
cd your-repository
2. 백엔드(Rasa/Python) 환경 설정
Bash

# 새로운 Conda 가상 환경 생성 및 활성화
conda create --name seonghwa_env python=3.10
conda activate seonghwa_env

# 필수 라이브러리 설치
pip install rasa==3.6.21 "rasa[transformers]" mysql-connector-python pymysql googletrans==4.0.0-rc1 konlpy

# (만약 의존성 충돌 발생 시) 아래 명령어로 호환 버전 직접 명시
pip install packaging==20.9 protobuf==4.23.3 tensorflow==2.12.0 tensorflow-intel==2.12.0
3. 데이터베이스 및 데이터 설정
MySQL 서버에 rasa_core 데이터베이스를 생성합니다.
프로젝트 내 Python 스크립트(insert_rules.py, insert_contacts.py 등)를 실행하여 rules_data, chatbot, images 테이블에 초기 데이터를 삽입합니다.
image_server.py의 BASE_IMAGE_DIR 경로에 맞게 이미지 파일들을 준비합니다.
4. Rasa 모델 학습
Bash

rasa train
🚀 실행 방법
백엔드 서버들을 각각 다른 터미널에서 실행해야 합니다.

이미지 서버 실행:
Bash

python image_server.py
Rasa 액션 서버 실행:
Bash

rasa run actions
Rasa 메인 서버 실행:
Bash

rasa run
Flutter 앱 실행:
Android Studio를 열고 프로젝트를 빌드하거나, 터미널에서 다음을 실행합니다. <!-- end list -->
Bash

flutter run
