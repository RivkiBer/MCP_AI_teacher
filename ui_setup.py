

import streamlit as st

def setup_page():


    # הגדרות בסיסיות לדף
    st.set_page_config(page_title="עוזר למידה AI", page_icon="🎓", layout="centered")

    # CSS מותאם לימין
    st.markdown("""
    <style>
    /* דף ראשי */
    .stApp {
        direction: rtl !important;
        text-align: right !important;
        font-family: Arial, sans-serif;
    }

    /* כותרות ופסקאות */
    h1, h2, h3, h4, h5, h6, p, span, label, .stTextInput label, .stMarkdown {
        text-align: right !important;
        direction: rtl !important;
    }

    /* רכיבי Radio */
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        display: flex;
        flex-direction: row; 
        align-items: center;
        justify-content: flex-start; 
        padding: 10px;
        border-radius: 8px;
        cursor: pointer;
        width: 100%;
        transition: background 0.3s;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        background-color: #f0f2f6;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] > label div[data-testid="stMarkdownContainer"] {
        margin-right: 10px;
        margin-left: 0px;
    }

    /* כפתורים */
    button[kind="primary"], button[kind="secondary"] {
        text-align: center;
    }

    /* info, warning, success */
    .stAlert {
        text-align: right !important;
        direction: rtl !important;
    }

    /* div פנימי רגיל */
    div {
        direction: rtl !important;
        text-align: right !important;
    }

    /* טקסט בתוך accordion / expander */
    .stExpander {
        direction: rtl !important;
        text-align: right !important;
    }

    </style>
    """, unsafe_allow_html=True)