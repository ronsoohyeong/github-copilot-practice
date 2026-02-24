# 무기명 BBS 

## 목표

무기명 게시판 BBS 기능을 개발한다. 최신 10개의 article만 관리하며, 각 article은 제목 (한글 20자 이내), 작성시각 time, 본문 (한글 200자 이내) 로 이루어져있다. 3개의 화면 (목록, article 열람, article 생성) 으로 구성되어있고, 목록에서 article을 선택 후 열람하거나 삭제가 가능하다.


## 사용 기술

* Python: 핵심 로직 구현
* pytest: 핵심 로직 단위 테스트
* FastAPI: REST API 구성
* Streamlit: API 기반 UI 구현


## 구현 범위 

3개의 화면으로 구성되어있다. 서비스 최초 진입시에는 목록화면을 보여준다.

* 목록 조회 : article 의 제목과 time을 생성 순서대로 보여주며, 가장 최신의 10개만 관리하며, 그전의 오래된 article은 삭제한다. 목록 밑에 New 버튼 및 Delete 버튼을 제공한다.
* article 열람 : 목록에서 article의 제목을 눌러서 선택하면 article의 제목, time, 본문을 보여준다. 아래에 List 버튼을 누르면 목록 화면으로 돌아간다.
* article 생성 : New 버튼을 누르면, article 작성 창으로 바뀌며, 제목 (한글 20자 이내) 및 본문 (한글 200자 이내) 를 작성할수 있는 필드가 있고, 아래에 Post, Cancel 의 두개 버튼이 있다. Post 버튼을 누르면, 그때의 시각을 time 값으로 하고, 작성한 article을 목록에 추가하며 목록 화면으로 돌아가고, Cancel 버튼은 작성중이던 내용을 버리고 목록 화면으로 돌아간다. 

## 조건

* DB 없이 메모리 기반
* API 4개로 구성 
  - Get_List  : 최대 10개 article 들의 (id , title, time) triple의 리스트를 리턴한다
  - Get_Article : id 를 argument로 해서, (title, body, time) triple 을 리턴한다
  - Delete_Article : id 를 argument로 해서, 해당 id의 article을 삭제하도록 한다. success/fail 여부를 리턴한다
  - Post_Article : (title, body, time) triple 을 argument로 하며, success/fail 여부를 리턴한다. Front-end 는 Post_article 호출 후 곧바로 Get_List를 서버로 보낸다.


## 진행 순서

1. Python으로 BbsService 구현
2. pytest로 핵심 로직 테스트 작성
3. FastAPI로 로직을 API에 연결
4. Streamlit으로 API 호출 Front-end UI 구성


## 완료 기준

* pytest 통과
* FastAPI /docs에서 API 동작 확인
* Streamlit에서 동작 확인
