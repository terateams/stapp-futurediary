import json
import os
from dotenv import load_dotenv
import streamlit as st
from .common import check_apptoken_from_apikey, get_global_datadir
from .session import PageSessionState
from .common import openai_text_generate, write_stream_text
from streamlit_ace import st_ace
from datetime import datetime, timedelta

load_dotenv()

st.set_page_config(page_title="未来日记", page_icon="📅")

page_state = PageSessionState("future_diary")
page_state.initn_attr("topic", "")
page_state.initn_attr("diary_data", "")
page_state.initn_attr("last_diary_data", "")
page_state.initn_attr("last_diary_datetime", "")

future_diary_history_dir = get_global_datadir("future_diary_history")


def parse_diary_datetime(diary_datetime: str):
    if not diary_datetime:
        return datetime.now()
    return datetime.strptime(diary_datetime, "%Y-%m-%d %H:%M:%S")


def get_diary_list():
    files = os.listdir(future_diary_history_dir)
    return files and [file.split("_future_diary.json")[0] for file in files] or []


def load_diary_data_by_topic(topic: str):
    if not topic:
        return
    filepath = os.path.join(future_diary_history_dir, f"{topic}_future_diary.json")
    with open(filepath, "r", encoding="utf-8") as f:
        plan_data = json.load(f)
        _load_diary_data(plan_data)


def _load_diary_data(plan_data: dict):
    if not plan_data:
        return
    page_state.topic = plan_data["topic"]
    page_state.diary_data = plan_data["diary_data"]
    page_state.last_diary_data = plan_data["last_diary_data"]
    page_state.last_diary_datetime = plan_data["last_diary_datetime"]


def sync_diary_data(last_datetime: datetime = None):
    if not page_state.topic.strip():
        st.warning("请先输入主题")
        return
    if not page_state.diary_data:
        return

    plan_data = {
        "topic": page_state.topic,
        "diary_data": page_state.diary_data,
        "last_diary_data": page_state.last_diary_data,
        "last_diary_datetime": (
            last_datetime.strftime("%Y-%m-%d %H:%M:%S") if last_datetime else None
        ),
    }

    page_state.last_diary_datetime = plan_data["last_diary_datetime"]

    filepath = os.path.join(
        future_diary_history_dir, f"{page_state.topic}_future_diary.json"
    )
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(plan_data, f, ensure_ascii=False, indent=4)


def main():
    with st.sidebar:
        st.title("📅 未来日记")
        tab1, tab2 = st.tabs(["参数设置", "关于"])
        apikey_box = st.empty()
        with tab1:
            if not page_state.app_uid:
                apikey = st.query_params.get("apikey")
                if not apikey:
                    apikey = apikey_box.text_input("请输入 API Key", type="password")

                if apikey:
                    appuid = check_apptoken_from_apikey(apikey)
                    if appuid:
                        page_state.app_uid = appuid
                        page_state.apikey = apikey
                        apikey_box.empty()

            if not page_state.app_uid:
                st.error("Auth is invalid")
                st.stop()
            param_box = st.container()

        with tab2:
            st.image(
                os.path.join(os.path.dirname(__file__), "future_diary.png"),
                use_column_width=True,
            )
            st.caption(
                "未来日记是一个革命性的基于想象力的日记生成系统，旨在将用户的未来梦想、目标或情景变成生动的故事。"
                "这个系统不仅仅是一个简单的日记工具，它是一个让用户探索未来可能性的平台，让你通过文字绘制心中的蓝图。"
            )

    with param_box:
        options = ["..."]
        ext_options = get_diary_list()
        if ext_options:
            options.extend(ext_options)
        history = st.selectbox("历史记录", options, index=0)
        if history != "...":
            load_diary_data_by_topic(history)
            page_state.topic = history

        page_state.topic = st.text_input("Topic", page_state.topic)
        completed = st.text_area("Completed conditions", "")
        goal_tips = st.text_input("Goal Tips", "")
        start_time_obj = parse_diary_datetime(page_state.last_diary_datetime)
        start_time = st.date_input("Start Time", start_time_obj)
        days = st.number_input("Days", 1, 365, 7)
        end_time = start_time + timedelta(days=days)
        st.markdown(f"**End Time**: `{end_time.strftime('%Y-%m-%d')}`")
        gen_button = st.button("生成内容")

    tab_gen, tab_articles, tab_editor = st.tabs(["写作", "预览", "编辑"])

    with tab_gen:
        tmp_box = st.empty()
        if gen_button:
            if not page_state.topic:
                st.warning("请输入主题")
                st.stop()
            _sysmsg = f"""You will begin writing a future diary, continuing according to the given conditions proposed by the user.

    Given conditions:
    - Journal Theme: A setting for a specific theme story in the future
    - Completed Condition: A description of the main character of the current story, as well as a description of the events that have already occurred
    - Goal Prompts: Some relevant hints for future story development
    - Time Range: The scope constraint of the event for future events

    ----------------------------------------------------------
    Historical Diary Contents:

    {page_state.diary_data}
    ----------------------------------------------------------
    Clarify:
    - Write creatively based on the journal theme, completed conditions, and goal prompts.
    - Each writing content should be conceived with a specific idea, which should reflect the story, and should be described in key details.
    - Reflect the temporal characteristics of the story and hint at the direction of the story in the next chapter.
    - If the given condition is not clear enough, the user should be prompted to improve.
    - Generate content that is imaginative and engaging.
    - If the content of the historical diary is not empty, it should be written coherently, and the content should not contradict the events in a conditional, if there is a contradiction, please point it out.

    ----------------------------------------------------------
    Output Format(Markdown):

    ## <topic content> - <starttime - endtime> 

    > Summary: <completed condition entered by the user> 

    ---

    < the contents of the diary, be careful not to output the date, and directly output the full content paragraphs...>"""
            _prompt = f"""
    Journal Topic: {page_state.topic}
    Completed Conditions: {completed}
    Goal Prompts: {goal_tips}
    Datime Range: {start_time} - {end_time}
    """
            with st.spinner("思考中..."):
                stream = openai_text_generate(
                    _sysmsg, _prompt, apikey=page_state.apikey
                )
                page_state.last_diary_data = write_stream_text(tmp_box, stream)

        if page_state.last_diary_data:
            tmp_box.markdown(page_state.last_diary_data)
            if (
                st.button("Save")
                and page_state.last_diary_data not in page_state.diary_data
            ):
                page_state.diary_data += "\n\n" + page_state.last_diary_data
                sync_diary_data(end_time)
            else:
                st.warning("没有新的内容可以保存")
        else:
            st.info("请设置参数并点击生成按钮")

    with tab_articles:
        if page_state.diary_data:
            st.markdown(page_state.diary_data)
        else:
            st.warning("还没有内容")

    with tab_editor:
        if page_state.diary_data:
            diary_data_content = st_ace(
                page_state.diary_data,
                language="markdown",
                height=480,
                wrap=True,
            )
            if diary_data_content:
                page_state.diary_data = diary_data_content
                sync_diary_data(page_state.last_diary_datetime)
        else:
            st.warning("还没有内容")
