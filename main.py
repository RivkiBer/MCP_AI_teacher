"""
אחראי על:
- ניהול שלבי המערכת
- ניהול session_state
- תצוגת UI
- קריאה לפונקציות חיצוניות
"""

import streamlit as st
import time
import os
from datetime import datetime

from ui_setup import setup_page
from utils import generate_summary_text
from api_service import generate_lesson_from_api

# הגדרת עמוד ו-CSS
setup_page()

# --- ניהול זיכרון מערכת ---
if 'step' not in st.session_state:
    st.session_state.step = "input"

if 'last_api_call' not in st.session_state:
    st.session_state.last_api_call = 0


# ===============================
# שלב א' – קבלת קלט מהמשתמש
# ===============================
if st.session_state.step == "input":

    st.title("🎓 עוזר למידה אישי")

    topic = st.text_input("מה הנושא שתרצו ללמוד?")

    st.markdown("### בחר רמת למידה:")
    level = st.radio(
        "רמה:",
        ["ילדים", "נוער", "מבוגרים"],
        horizontal=True,
        label_visibility="collapsed"
    )

    if st.button("ייצר שיעור עכשיו 🚀"):

        current_time = time.time()
        elapsed = current_time - st.session_state.last_api_call

        # הגבלת קצב קריאה ל-API
        if elapsed < 10:
            remaining = int(10 - elapsed)
            st.error(f"⏳ אנא המתן {remaining} שניות.")

        elif not topic:
            st.warning("⚠️ נא להזין נושא.")

        else:
            st.session_state.last_api_call = current_time

            lesson_data = generate_lesson_from_api(topic, level)

            if lesson_data:
                st.session_state.lesson_data = lesson_data
                st.session_state.step = "lesson"
                st.rerun()


# ===============================
# שלב ב' – הצגת שיעור ובוחן
# ===============================
elif st.session_state.step == "lesson":

    data = st.session_state.lesson_data

    st.subheader(f"📖 שיעור: {data['topic']}")
    st.info(data['lesson'])

    st.divider()
    st.subheader("📝 בוחן אמריקאי")

    user_answers = []

    for i, q_item in enumerate(data['questions']):

        st.markdown(f"**{i + 1}. {q_item['q']}**")

        choice = st.radio(
            f"שאלה {i}",
            options=q_item['choices'],
            index=None,
            key=f"q_{i}",
            label_visibility="collapsed",
            disabled='final_score' in st.session_state
        )

        user_answers.append(choice)

        # הצגת משוב לאחר בדיקה
        if 'final_score' in st.session_state:
            actual_sel = st.session_state.user_answers[i]
            correct_val = q_item['correct']

            if actual_sel == correct_val:
                st.success("✅ נכון מאוד!")
            else:
                st.error(f"❌ התשובה הנכונה היא: '{correct_val}'")

    if 'final_score' not in st.session_state:
        if st.button("בדוק את הציון שלי! 🏁"):
            if None in user_answers:
                st.warning("⚠️ נא לסמן תשובה לכל השאלות.")
            else:
                # חישוב הציון
                score_count = sum(
                    1 for i, q in enumerate(data['questions'])
                    if user_answers[i] == q['correct']
                )
                st.session_state.final_score = int(
                    (score_count / len(data['questions'])) * 100
                )
                st.session_state.user_answers = user_answers

                # הצגת בילונים והודעה אם הציון מושלם
                if st.session_state.final_score == 100:
                    st.success(f"ציון מושלם: {st.session_state.final_score}! כל הכבוד 🏆")
                    st.balloons()
                else:
                    st.info(f"סיימת את הבוחן בציון: {st.session_state.final_score}")

                # אין צורך ב-st.rerun() כאן, השארת ה־session_state מספיק

    # סיכום ושמירה
    if 'final_score' in st.session_state:

        st.info(f"סיימת בציון: {st.session_state.final_score}")

        summary_txt = generate_summary_text(
            data['topic'],
            data['lesson'],
            data['questions'],
            st.session_state.user_answers,
            st.session_state.final_score
        )

        if st.button("שמור בתיקיה 💾"):

            folder = "my_lessons"

            if not os.path.exists(folder):
                os.makedirs(folder)

            date_str = datetime.now().strftime('%d-%m-%Y')
            filename = f"{data['topic']}_{date_str}.txt"
            path = os.path.join(folder, filename)

            with open(path, "w", encoding="utf-8") as f:
                f.write(summary_txt)

            st.success(f"נשמר: {filename}")

    # התחלה מחדש
    if st.button("שיעור חדש 🔄"):
        for key in ['final_score', 'user_answers', 'lesson_data']:
            if key in st.session_state:
                del st.session_state[key]

        st.session_state.step = "input"
        st.rerun()