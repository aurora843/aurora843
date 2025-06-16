Rasa & MySQL 기반 지능형 기숙사 정보 안내 챗봇
   

본 프로젝트는 선문대학교 성화학숙(기숙사) 학생들을 위한 정보 안내 AI 챗봇입니다. Rasa 프레임워크를 기반으로, 데이터베이스에 저장된 정보를 바탕으로 사용자의 질문에 텍스트와 이미지로 답변합니다.

1. 주요 기능
데이터베이스 연동 정보 제공: MySQL DB에 저장된 200여 개의 규칙 및 연락처 정보를 동적으로 조회하여 텍스트로 답변합니다.
멀티미디어 응답 (이미지): 규칙 안내, 수강신청 방법, 학교 지도 등 특정 질문에 대해 텍스트와 함께 관련 이미지를 시각적으로 제공하여 정보 이해도를 향상시킵니다.
지능형 한국어 처리: KoNLPy(Okt) 기반의 커스텀 토크나이저를 구현하여, 한국어의 유연한 띄어쓰기 및 다양한 표현에 대응합니다.
다국어 지원 기반: googletrans 라이브러리를 활용하여, 외국인 유학생의 비한국어 질문에 대한 기본적인 응대 및 번역 기능을 구현했습니다.
2. 시스템 구성도
본 챗봇은 안정성과 확장성을 위해 역할에 따라 3개의 독립적인 서버와 1개의 데이터베이스로 구성된 모듈형 아키텍처를 가집니다.

Rasa 서버 (Port 5005): NLU(자연어 이해) 및 Core(대화 관리)를 담당하는 챗봇의 핵심 두뇌
액션 서버 (Port 5055): 데이터베이스 조회 등 복잡한 로직을 수행하는 actions.py 실행
이미지 서버 (Port 8080): Flask 기반으로 구축, 로컬 이미지 파일을 웹 URL로 제공
데이터베이스 (MySQL): rules_data(규칙), chatbot(연락처), images(이미지 정보) 테이블에 챗봇의 모든 지식 저장
3. 핵심 기술 스택
기술	활용 내용
Rasa	NLU, 대화 관리 등 챗봇 개발의 핵심 프레임워크
Python	액션 서버, 이미지 서버 등 전체 백엔드 로직 구현
MySQL	챗봇의 지식(규칙, 연락처, 이미지 정보)을 저장하는 데이터베이스
Flask	로컬 이미지 파일을 웹으로 제공하는 독립 이미지 서버 구축
KoNLPy (Okt)	커스텀 토크나이저를 통해 한국어 문장을 형태소 단위로 분석하여 NLU 성능 향상
Googletrans	다국어 입력에 대한 기본적인 번역 기능 제공

Sheets로 내보내기
4. 로컬 환경 설정 및 실행 방법
사전 요구사항
Anaconda (or Miniconda)
Python 3.10
MySQL Server
설치 및 설정 과정
Conda 가상 환경 생성 및 활성화:

Bash

conda create --name your_env_name python=3.10
conda activate your_env_name
필수 라이브러리 설치:

pip으로 Rasa 및 기타 라이브러리를 설치합니다. (의존성 충돌을 피하기 위해 특정 버전을 명시하는 것이 중요합니다.)
<!-- end list -->

Bash

pip install rasa==3.6.21
pip install mysql-connector-python pymysql googletrans==4.0.0-rc1 konlpy
pip install packaging==20.9 protobuf==4.23.3 tensorflow==2.12.0 tensorflow-intel==2.12.0
데이터베이스 설정:

MySQL에서 rasa_core 데이터베이스를 생성합니다.
chatbot, rules_data, images 테이블을 생성하고, 제공된 Python 스크립트(insert_contacts.py, insert_rules.py 등)를 사용하여 데이터를 삽입합니다.
이미지 폴더 설정:

image_server.py에 명시된 경로(예: C:/pjw/image)에 이미지 파일들을 위치시킵니다.
실행 방법
프로젝트를 실행하려면 3개의 터미널 창이 필요합니다. 각 터미널에서 가상 환경을 활성화한 후 다음을 순서대로 실행합니다.

이미지 서버 실행:

Bash

python image_server.py
Rasa 액션 서버 실행:

Bash

rasa run actions
Rasa 메인 서버 실행:

Bash

rasa run
<!-- end list -->

모든 서버가 실행되면, webchat.html 파일을 웹 브라우저에서 열어 챗봇을 테스트할 수 있습니다.
5. 프로젝트 구조
/
├── actions.py             # 커스텀 액션 로직
├── image_server.py        # Flask 이미지 서버
├── korean_tokenizer.py    # KoNLPy 커스텀 토크나이저
├── config.yml             # NLU 파이프라인 및 정책 설정
├── domain.yml             # 챗봇의 세계관 (인텐트, 액션, 응답)
├── credentials.yml        # 채널 연결 정보
├── endpoints.yml          # 액션서버, DB 등 외부 엔드포인트
├── data/
│   ├── nlu.yml            # NLU 학습 데이터
│   ├── rules.yml          # 대화 규칙
│   └── stories.yml        # 대화 시나리오
└── models/                # 훈련된 모델 저장 폴더
