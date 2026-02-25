"""
- בניית prompt
- שליחת בקשה ל-Gemini
- טיפול בשגיאות
- פירוק תשובת ה-AI
"""

import requests
import os
import urllib3
from dotenv import load_dotenv
import streamlit as st

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def generate_lesson_from_api(topic, level):

    level_descriptions = {
        "ילדים": "שפה פשוטה מאוד, עם אימוגים והסברים קצרים",
        "נוער": "שפה בגובה העיניים, עם אימוגים בודדים רק איפה שחייבים",
        "מבוגרים": "שפה מקצועית ומעמיקה, ללא אימוגים"
    }

    detailed_level = level_descriptions.get(level, level)

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        st.error("המפתח לא נמצא בקובץ .env")
        return None

    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={api_key}"

    prompt = (
        f"כתוב שיעור מתומצת וקצר קצר בעברית על '{topic}' לרמת {detailed_level}. "
                    "השתמש בשפה נקייה ומכובדת. "
                    "אחריו הוסף 3 שאלות אמריקאיות. "
                    "פורמט השאלות חייב להיות בדיוק כך:\n"
                    "Q: [השאלה]\n"
                    "A1: [תשובה 1]\n"
                    "A2: [תשובה 2]\n"
                    "A3: [תשובה 3]\n"
                    "A4: [תשובה 4]\n"
                    "CORRECT: [מספר התשובה הנכונה בלבד]\n"
                    "הפרד בין השיעור לשאלות עם '---QUIZ---'."
    )

    try:
        response = requests.post(
            url,
            json={"contents": [{"parts": [{"text": prompt}]}]},
            verify=False,
            timeout=30
        )
        if response.status_code == 429:
            st.error("הגעת למגבלת השימוש. אנא המתן ונסה שוב מאוחר יותר.")
            return None
        elif response.status_code ==418:
            st.error("אופסס... נטפרי לא מרשה לי לדבר איתך על זה")
            return None
        elif response.status_code != 200:
            st.error("שגיאה בשרת.")
            return None

        response_data = response.json()
        full_text = response_data['candidates'][0]['content']['parts'][0]['text']

        if "---QUIZ---" not in full_text:
            st.error("פורמט לא תקין.")
            return None

        lesson_part, quiz_part = full_text.split("---QUIZ---")

        questions_data = []
        raw_questions = quiz_part.split("Q:")[1:]

        for rq in raw_questions:
            lines = [l.strip() for l in rq.strip().split('\n') if l.strip()]
            choices = [l.split(": ")[1] for l in lines[1:5]]
            correct_idx = int(lines[5].split(": ")[1].strip()) - 1

            questions_data.append({
                "q": lines[0],
                "choices": choices,
                "correct": choices[correct_idx]
            })

        return {
            "topic": topic,
            "lesson": lesson_part,
            "questions": questions_data
        }

    except Exception as e:
        st.error(f"שגיאה: {str(e)}")
        return None