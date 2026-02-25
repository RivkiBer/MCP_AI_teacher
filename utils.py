from datetime import datetime

def generate_summary_text(topic, content, questions=None, user_answers=None, score=None):
    summary = f"סיכום שיעור: {topic}\n"
    summary += f"תאריך: {datetime.now().strftime('%d/%m/%Y')}\n"
    summary += "=" * 30 + "\n\n"
    summary += "📖 תוכן השיעור:\n"
    summary += content + "\n\n"

    if questions and score is not None:
        summary += "=" * 30 + "\n"
        summary += f"📝 ציון: {score}\n\n"
        for i, q in enumerate(questions):
            summary += f"{i + 1}. {q['q']}\n"
            summary += f"תשובתך: {user_answers[i]}\n"
            summary += f"תשובה נכונה: {q['correct']}\n\n"

    return summary