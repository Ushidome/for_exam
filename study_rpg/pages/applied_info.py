import streamlit as st

from db import add_xp_event, first_category, init_db, increment_progress, progress_items, today_logs
from xp import XP_RULES

EXAM_NAME = "応用情報"
PAST_EXAM_URL = "https://www.ap-siken.com/apkakomon.php"


def complete_morning() -> None:
    add_xp_event(EXAM_NAME, "午前問題を100問完了", XP_RULES["applied_morning_100"])
    category = first_category(progress_items(EXAM_NAME))
    if category:
        increment_progress(EXAM_NAME, category, amount=1)
    st.success("午前問題100問を記録しました。+1,000 XP")


def complete_afternoon() -> None:
    add_xp_event(EXAM_NAME, "午後問題を1問完了", XP_RULES["applied_afternoon_1"])
    category = first_category(progress_items(EXAM_NAME))
    if category:
        increment_progress(EXAM_NAME, category, amount=1)
    st.success("午後問題1問を記録しました。+300 XP")


def render_stamp() -> None:
    count = sum(1 for log in today_logs() if log["exam"] == EXAM_NAME)
    if count == 0:
        st.info("今日の応用情報スタンプはまだありません。")
    else:
        st.success(f"今日の応用情報スタンプ: {'★' * min(5, count)}")


def render_progress() -> None:
    st.subheader("分野別攻略率")
    for item in progress_items(EXAM_NAME):
        completed = item["completed_units"]
        target = item["target_units"]
        rate = completed / target if target else 0
        st.write(f"{item['category']}：{completed}/{target}")
        st.progress(rate)


def main() -> None:
    st.set_page_config(page_title="応用情報", page_icon="📘", layout="wide")
    init_db()

    st.title("応用情報 攻略ページ")
    st.link_button("過去問道場を開く", PAST_EXAM_URL)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("午前問題を100問完了", use_container_width=True):
            complete_morning()
    with col2:
        if st.button("午後問題を1問完了", use_container_width=True):
            complete_afternoon()

    render_stamp()
    render_progress()


main()
