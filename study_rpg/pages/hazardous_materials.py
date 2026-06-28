import streamlit as st

from db import (
    HAZARDOUS_CLASSES,
    add_chemical,
    add_xp_event,
    chemicals,
    first_category,
    init_db,
    increment_progress,
    level_up_chemical,
    progress_items,
)
from xp import XP_RULES

EXAM_NAME = "危険物甲種"


def complete_practice_set() -> None:
    add_xp_event(EXAM_NAME, "問題演習1セット完了", XP_RULES["hazardous_practice_set"])
    category = first_category(progress_items(EXAM_NAME))
    if category:
        increment_progress(EXAM_NAME, category, amount=1)
    st.success("問題演習1セットを記録しました。+800 XP")


def render_add_form() -> None:
    st.subheader("化学物質を追加")
    with st.form("chemical_form", clear_on_submit=True):
        name = st.text_input("物質名")
        class_type = st.selectbox("類別", HAZARDOUS_CLASSES)
        formula_memo = st.text_area("構造式メモ")
        properties = st.text_area("性質")
        hazards = st.text_area("危険ポイント")
        encyclopedia_level = st.number_input("図鑑レベル", min_value=1, max_value=99, value=1)
        submitted = st.form_submit_button("図鑑に追加")

    if submitted:
        if not name.strip():
            st.warning("物質名を入力してください。")
            return

        add_chemical(
            name=name.strip(),
            class_type=class_type,
            formula_memo=formula_memo.strip(),
            properties=properties.strip(),
            hazards=hazards.strip(),
            encyclopedia_level=int(encyclopedia_level),
        )
        add_xp_event(EXAM_NAME, "化学物質図鑑に1件追加", XP_RULES["chemical_added"])
        increment_progress(EXAM_NAME, class_type, amount=1)
        st.success("化学物質を図鑑に追加しました。+200 XP")


def render_chemicals() -> None:
    st.subheader("化学物質図鑑")
    entries = chemicals()
    if not entries:
        st.caption("図鑑はまだ空です。覚えたい物質を1件追加してみましょう。")
        return

    for chemical in entries:
        with st.expander(f"{chemical['name']} / {chemical['class_type']} / Lv{chemical['encyclopedia_level']}"):
            st.write(f"構造式メモ: {chemical['formula_memo'] or '-'}")
            st.write(f"性質: {chemical['properties'] or '-'}")
            st.write(f"危険ポイント: {chemical['hazards'] or '-'}")
            if st.button("図鑑レベルアップ", key=f"level-up-{chemical['id']}"):
                level_up_chemical(int(chemical["id"]))
                add_xp_event(EXAM_NAME, "図鑑レベルアップ", XP_RULES["chemical_level_up"])
                st.success("図鑑レベルを上げました。+100 XP")
                st.rerun()


def render_progress() -> None:
    st.subheader("類別ごとの攻略率")
    for item in progress_items(EXAM_NAME):
        completed = item["completed_units"]
        target = item["target_units"]
        rate = completed / target if target else 0
        st.write(f"{item['category']}：{completed}/{target}")
        st.progress(rate)


def main() -> None:
    st.set_page_config(page_title="危険物甲種", page_icon="🧪", layout="wide")
    init_db()

    st.title("危険物甲種 攻略ページ")
    if st.button("問題演習1セット完了", use_container_width=True):
        complete_practice_set()

    render_add_form()
    render_chemicals()
    render_progress()


main()
