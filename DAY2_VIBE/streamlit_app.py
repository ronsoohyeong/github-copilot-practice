import os
from datetime import datetime

import requests
import streamlit as st


API_BASE_URL = os.getenv("BBS_API_BASE_URL", "http://127.0.0.1:8000")


def handle_article_checkbox_change(changed_article_id: int, article_ids: list[int]) -> None:
    changed_key = f"select-{changed_article_id}"
    changed_checked = bool(st.session_state.get(changed_key, False))

    if changed_checked:
        for article_id in article_ids:
            if article_id != changed_article_id:
                st.session_state[f"select-{article_id}"] = False
        st.session_state.selected_action_id = changed_article_id
        return

    if st.session_state.selected_action_id == changed_article_id:
        st.session_state.selected_action_id = None


def api_get_list() -> list[list[int | str]]:
    response = requests.get(f"{API_BASE_URL}/articles", timeout=5)
    response.raise_for_status()
    return response.json()


def api_get_article(article_id: int) -> tuple[str, str, str]:
    response = requests.get(f"{API_BASE_URL}/articles/{article_id}", timeout=5)
    response.raise_for_status()
    title, body, created_time = response.json()
    return title, body, created_time


def api_post_article(title: str, body: str, created_time: str) -> bool:
    response = requests.post(
        f"{API_BASE_URL}/articles",
        json={"title": title, "body": body, "time": created_time},
        timeout=5,
    )
    response.raise_for_status()
    return bool(response.json().get("success"))


def api_delete_article(article_id: int) -> bool:
    response = requests.delete(f"{API_BASE_URL}/articles/{article_id}", timeout=5)
    response.raise_for_status()
    return bool(response.json().get("success"))


if "screen" not in st.session_state:
    st.session_state.screen = "list"
if "selected_article_id" not in st.session_state:
    st.session_state.selected_article_id = None
if "selected_action_id" not in st.session_state:
    st.session_state.selected_action_id = None

st.title("무기명 BBS")

if st.session_state.screen == "list":
    st.subheader("목록")
    try:
        articles = api_get_list()
        if not articles:
            st.info("게시글이 없습니다.")
            st.session_state.selected_action_id = None
        if articles:
            article_ids = [int(article_id) for article_id, _, _ in articles]
            if st.session_state.selected_action_id not in article_ids:
                st.session_state.selected_action_id = None

            checkbox_keys = {f"select-{article_id}" for article_id in article_ids}
            stale_keys = [
                key for key in st.session_state.keys() if key.startswith("select-") and key not in checkbox_keys
            ]
            for key in stale_keys:
                del st.session_state[key]

            st.caption("체크박스로 article 1개를 선택한 뒤 Read/Delete를 누르거나, 제목을 바로 눌러 Read할 수 있습니다.")
            for article_id, title, created_time in articles:
                normalized_article_id = int(article_id)
                checkbox_key = f"select-{normalized_article_id}"
                if checkbox_key not in st.session_state:
                    st.session_state[checkbox_key] = (
                        st.session_state.selected_action_id == normalized_article_id
                    )

                col_check, col_title, col_time = st.columns([1, 5, 3])
                with col_check:
                    st.checkbox(
                        "선택",
                        key=checkbox_key,
                        label_visibility="collapsed",
                        on_change=handle_article_checkbox_change,
                        args=(normalized_article_id, article_ids),
                    )
                with col_title:
                    if st.button(
                        title,
                        key=f"title-read-{normalized_article_id}",
                        use_container_width=True,
                    ):
                        st.session_state.selected_article_id = normalized_article_id
                        st.session_state.screen = "view"
                        st.rerun()
                with col_time:
                    st.write(str(created_time))

            selected_id = st.session_state.selected_action_id
            if selected_id is not None and not st.session_state.get(f"select-{selected_id}", False):
                st.session_state.selected_action_id = None
    except requests.RequestException:
        st.error("API 서버 연결에 실패했습니다.")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("New", use_container_width=True):
            st.session_state.screen = "new"
            st.rerun()
    with col2:
        if st.button("Read", use_container_width=True):
            if st.session_state.selected_action_id is None:
                st.error("읽을 article을 선택해 주세요.")
            else:
                st.session_state.selected_article_id = int(st.session_state.selected_action_id)
                st.session_state.screen = "view"
                st.rerun()
    with col3:
        if st.button("Delete", use_container_width=True):
            delete_id = st.session_state.selected_action_id
            if delete_id is None:
                st.error("삭제할 article을 선택해 주세요.")
            else:
                try:
                    success = api_delete_article(delete_id)
                    if success:
                        checkbox_key = f"select-{delete_id}"
                        if checkbox_key in st.session_state:
                            st.session_state[checkbox_key] = False
                        st.session_state.selected_action_id = None
                        st.rerun()
                    else:
                        st.error("삭제에 실패했습니다.")
                except requests.RequestException:
                    st.error("API 서버 연결에 실패했습니다.")

elif st.session_state.screen == "view":
    st.subheader("article 열람")
    article_id = st.session_state.selected_article_id
    if article_id is None:
        st.session_state.screen = "list"
        st.rerun()

    try:
        title, body, created_time = api_get_article(article_id)
        st.markdown(f"### {title}")
        st.caption(f"작성시각: {created_time}")
        st.write(body)
    except requests.HTTPError as http_error:
        if http_error.response.status_code == 404:
            st.error("게시글을 찾을 수 없습니다.")
        else:
            st.error("게시글 조회 중 오류가 발생했습니다.")
    except requests.RequestException:
        st.error("API 서버 연결에 실패했습니다.")

    if st.button("List"):
        st.session_state.screen = "list"
        st.session_state.selected_article_id = None
        st.rerun()

elif st.session_state.screen == "new":
    st.subheader("article 생성")
    title = st.text_input("제목 (한글 20자 이내)", max_chars=20)
    body = st.text_area("본문 (한글 200자 이내)", max_chars=200, height=200)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Post", use_container_width=True):
            try:
                created_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                success = api_post_article(title, body, created_time)
                if success:
                    st.session_state.screen = "list"
                    st.rerun()
                else:
                    st.error("입력값이 유효하지 않습니다.")
            except requests.RequestException:
                st.error("API 서버 연결에 실패했습니다.")
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.session_state.screen = "list"
            st.rerun()
