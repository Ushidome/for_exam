import streamlit as st

from db import current_streak, init_db, progress_rate, recent_logs, today_logs, today_xp, total_xp
from xp import calculate_level, next_level_xp, progress_to_next_level


def render_metric_row(total: int) -> None:
    level = calculate_level(total)
    next_xp = next_level_xp(total)
    today_total = today_xp()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("総XP", f"{total:,} XP")
    col2.metric("現在レベル", f"Lv{level}")
    col3.metric("今日の学習", f"{today_total:,} XP")
    col4.metric("連続学習日数", f"{current_streak()} 日")

    st.progress(progress_to_next_level(total))
    if next_xp is None:
        st.caption("Lv10 到達済みです。あとはラスボス対策を積み上げましょう。")
    else:
        st.caption(f"次のレベルまで {max(0, next_xp - total):,} XP")


def render_exam_progress() -> None:
    st.subheader("攻略率")
    col1, col2 = st.columns(2)

    applied_rate = progress_rate("応用情報")
    hazardous_rate = progress_rate("危険物甲種")

    with col1:
        st.metric("応用情報 攻略率", f"{applied_rate * 100:.0f}%")
        st.progress(applied_rate)

    with col2:
        st.metric("危険物甲種 攻略率", f"{hazardous_rate * 100:.0f}%")
        st.progress(hazardous_rate)


def render_today_status() -> None:
    st.subheader("今日の学習状況")
    logs = today_logs()
    if not logs:
        st.info("今日はまだ学習ログがありません。1つ完了してスタンプを押しましょう。")
        return

    st.success(f"今日のスタンプ: {'★' * min(5, len(logs))}")
    for log in logs:
        st.write(f"{log['exam']} / {log['action']} / +{log['xp']:,} XP")


def render_recent_logs() -> None:
    st.subheader("最近の学習ログ")
    logs = recent_logs()
    if not logs:
        st.caption("まだログがありません。各ページの完了ボタンから記録できます。")
        return

    for log in logs:
        st.write(
            f"{log['created_at']} | {log['exam']} | {log['action']} | +{log['xp']:,} XP"
        )


def main() -> None:
    st.set_page_config(page_title="資格攻略RPG Dashboard", page_icon="🎮", layout="wide")
    init_db()

    st.title("資格攻略RPG Dashboard")
    st.caption("応用情報技術者試験と危険物取扱者甲種の攻略状況を、XP・レベル・スタンプで可視化します。")

    total = total_xp()
    render_metric_row(total)
    render_exam_progress()
    render_today_status()
    render_recent_logs()


if __name__ == "__main__":
    main()
