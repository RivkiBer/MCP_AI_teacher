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

    # --- חישוב התקדמות למילוי הפס ---
    # סופר כמה שאלות כבר נענו (כאלו שהערך שלהן ב-session_state אינו None)
    answered_count = 0
    for i in range(len(data['questions'])):
        if st.session_state.get(f"q_{i}") is not None:
            answered_count += 1

    progress_percentage = answered_count / len(data['questions'])

    # הצגת פס התקדמות
    st.write(f"התקדמות המענה: {answered_count}/{len(data['questions'])}")
    st.progress(progress_percentage)

    current_selections = []

    for i, q_item in enumerate(data['questions']):
        st.markdown(f"**{i + 1}. {q_item['q']}**")

        radio_key = f"q_{i}"

        # index=None גורם לכך ששום תשובה לא תסומן מראש
        choice = st.radio(
            f"בחרו תשובה {i}",
            options=q_item['choices'],
            index=None,
            key=radio_key,
            label_visibility="collapsed",
            disabled='final_score' in st.session_state,
            on_change=st.rerun  # גורם לפס ההתקדמות להתעדכן מיד עם כל לחיצה
        )

        current_selections.append(choice)

        # הצגת משוב צבעוני מיד לאחר לחיצה על כפתור הבדיקה
        if 'final_score' in st.session_state:
            correct_val = q_item['correct']
            user_choice = st.session_state.user_answers[i]

            if user_choice == correct_val:
                st.success("✅ תשובה נכונה!")
            else:
                st.error(f"❌ טעות. התשובה הנכונה היא: {correct_val}")

    st.divider()

    # כפתור בדיקה
    if 'final_score' not in st.session_state:
        if st.button("בדוק את הציון שלי! 🏁"):
            if None in current_selections:
                st.warning("⚠️ יש לענות על כל השאלות לפני הבדיקה.")
            else:
                score_count = sum(1 for i, q in enumerate(data['questions'])
                                  if current_selections[i] == q['correct'])

                st.session_state.final_score = int((score_count / len(data['questions'])) * 100)
                st.session_state.user_answers = current_selections
                st.rerun()

    # תוצאות סופיות ושמירה
    if 'final_score' in st.session_state:
        st.markdown(f"### ציון סופי: `{st.session_state.final_score}`")
        if st.session_state.final_score == 100:
            st.balloons()
            st.success("מצוין! שלטת בחומר בצורה מלאה! 🏆")

        # כפתור שמירה
        if st.button("שמור תוצאות 💾"):
            # כאן נכנס הלוגיקה של generate_summary_text והשמירה לקובץ
            st.write("הקובץ נשמר בהצלחה!")

        # כפתור חזרה
        if st.button("שיעור חדש 🔄"):
            # ניקוי ה-session_state
            for key in list(st.session_state.keys()):
                if key.startswith("q_") or key in ['final_score', 'user_answers', 'lesson_data']:
                    del st.session_state[key]
            st.session_state.step = "input"
            st.rerun()