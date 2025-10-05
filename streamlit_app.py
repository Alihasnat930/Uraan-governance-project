import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
import time
import sqlite3
import os
import re
from typing import Dict, List, Any, Optional
import logging

# Advanced Chatbot Response System
def verify_cnic(cnic):
    """Verify CNIC format and check validity"""
    # Remove dashes and spaces
    cnic_clean = cnic.replace('-', '').replace(' ', '')
    
    # Check if 13 digits
    if len(cnic_clean) != 13 or not cnic_clean.isdigit():
        return False, "Invalid CNIC format. Please use format: XXXXX-XXXXXXX-X"
    
    # Simulate database check
    valid_cnics = {
        '3520212345671': {'name': 'Ahmed Khan', 'status': 'Active'},
        '4210198765432': {'name': 'Sara Ali', 'status': 'Active'},
        '3310156789012': {'name': 'Hassan Raza', 'status': 'Active'}
    }
    
    if cnic_clean in valid_cnics:
        return True, valid_cnics[cnic_clean]
    else:
        # For demo, accept any valid format
        return True, {'name': 'Verified User', 'status': 'Active'}

def get_bill_info(cnic_or_id):
    """Retrieve bill information"""
    # Simulate bill database
    bills = {
        '3520212345671': {
            'type': 'Electricity',
            'amount': 'PKR 3,450',
            'due_date': '15 Oct 2025',
            'status': 'Pending',
            'account': 'ELEC-2023-1234'
        },
        '4210198765432': {
            'type': 'Gas',
            'amount': 'PKR 2,120',
            'due_date': '20 Oct 2025',
            'status': 'Pending',
            'account': 'GAS-2023-5678'
        },
        'BILL-123456': {
            'type': 'Water',
            'amount': 'PKR 890',
            'due_date': '10 Oct 2025',
            'status': 'Overdue',
            'account': 'WATER-2023-9012'
        }
    }
    
    cnic_clean = cnic_or_id.replace('-', '').replace(' ', '')
    if cnic_clean in bills:
        return bills[cnic_clean]
    elif cnic_or_id.upper() in bills:
        return bills[cnic_or_id.upper()]
    else:
        # Generate sample bill
        return {
            'type': 'Utility',
            'amount': 'PKR 1,500',
            'due_date': '30 Oct 2025',
            'status': 'Pending',
            'account': 'ACC-' + cnic_or_id[:8]
        }

def get_faqs(category='general'):
    """Get FAQs based on category"""
    faqs = {
        'bill': [
            "Q: How to check my bill?\nA: Provide your CNIC or Bill ID, and I'll retrieve your bill details instantly.",
            "Q: How to pay my bill?\nA: You can pay online through our portal, mobile app, or visit authorized bank branches.",
            "Q: What if I lost my bill?\nA: No worries! Just provide your CNIC and I'll retrieve your bill information.",
            "Q: Can I get a bill extension?\nA: Yes, contact our helpline at 042-111-222-333 for payment extension requests."
        ],
        'cnic': [
            "Q: How to verify my CNIC?\nA: Simply type your CNIC in format XXXXX-XXXXXXX-X and I'll verify it for you.",
            "Q: What if my CNIC is expired?\nA: Visit the nearest NADRA office with required documents to renew your CNIC.",
            "Q: Can I update CNIC details online?\nA: Some updates can be done online at nadra.gov.pk, others require office visit.",
            "Q: How long does CNIC verification take?\nA: Instant verification online. Physical CNIC renewal takes 3-7 working days."
        ],
        'general': [
            "Q: What services do you offer?\nA: Bill checking, CNIC verification, fraud detection, government services, and 24/7 assistance.",
            "Q: Is this service free?\nA: Yes, all our online services are completely free for citizens.",
            "Q: How secure is my data?\nA: We use bank-level encryption and never store your personal information.",
            "Q: Available in which languages?\nA: Currently English and Urdu, more languages coming soon!"
        ]
    }
    return faqs.get(category, faqs['general'])

def get_chatbot_response(user_input, language='English'):
    """Advanced chatbot response with multiple intents"""
    user_input_lower = user_input.lower()
    
    # CNIC Verification Intent
    if any(word in user_input_lower for word in ['cnic', 'verify', 'verification', 'id card', 'identity']):
        # Check if CNIC number is in input
        cnic_pattern = r'\d{5}[-\s]?\d{7}[-\s]?\d'
        cnic_match = re.search(cnic_pattern, user_input)
        
        if cnic_match:
            cnic = cnic_match.group()
            is_valid, result = verify_cnic(cnic)
            if is_valid and isinstance(result, dict):
                if language == 'اردو':
                    return f"✅ CNIC تصدیق شدہ!\n\nنام: {result['name']}\nحیثیت: {result['status']}\n\nآپ کا CNIC درست ہے۔ کیا آپ بل چیک کرنا چاہتے ہیں؟"
                else:
                    return f"✅ CNIC Verified Successfully!\n\nName: {result['name']}\nStatus: {result['status']}\n\nYour CNIC is valid and active. Would you like to check your bills?"
            else:
                return result  # Error message
        else:
            if language == 'اردو':
                return "برائے مہربانی اپنا CNIC نمبر اس فارمیٹ میں درج کریں: XXXXX-XXXXXXX-X\n\nمثال: 35202-1234567-1"
            else:
                return "Please provide your CNIC number in this format: XXXXX-XXXXXXX-X\n\nExample: 35202-1234567-1"
    
    # Bill Checking Intent
    elif any(word in user_input_lower for word in ['bill', 'payment', 'pay', 'invoice', 'amount', 'due']):
        # Check for CNIC or Bill ID
        id_pattern = r'(?:\d{5}[-\s]?\d{7}[-\s]?\d)|(?:BILL-\d+)|(?:[A-Z]+-\d+)'
        id_match = re.search(id_pattern, user_input, re.IGNORECASE)
        
        if id_match:
            bill_id = id_match.group()
            bill_info = get_bill_info(bill_id)
            
            status_emoji = "⚠️" if bill_info['status'] == 'Overdue' else "✅"
            
            if language == 'اردو':
                return f"{status_emoji} بل کی تفصیلات\n\nقسم: {bill_info['type']}\nرقم: {bill_info['amount']}\nآخری تاریخ: {bill_info['due_date']}\nحیثیت: {bill_info['status']}\nاکاؤنٹ: {bill_info['account']}\n\nآن لائن ادائیگی: govai.portal/pay"
            else:
                return f"{status_emoji} Bill Details Retrieved\n\nType: {bill_info['type']}\nAmount: {bill_info['amount']}\nDue Date: {bill_info['due_date']}\nStatus: {bill_info['status']}\nAccount: {bill_info['account']}\n\n💳 Pay Online: govai.portal/pay\n🏦 Or visit any authorized bank"
        else:
            if language == 'اردو':
                return "بل چیک کرنے کے لیے:\n1. اپنا CNIC نمبر درج کریں\n2. یا بل نمبر (BILL-XXXXXX)\n\nمثال: 'میرا بل چیک کریں 35202-1234567-1'"
            else:
                return "To check your bill, please provide:\n1. Your CNIC number (XXXXX-XXXXXXX-X)\n2. Or Bill ID (BILL-XXXXXX)\n\nExample: 'Check bill for 35202-1234567-1'"
    
    # FAQ Intent
    elif any(word in user_input_lower for word in ['faq', 'help', 'question', 'how to', 'what is', 'guide']):
        category = 'general'
        if 'bill' in user_input_lower or 'payment' in user_input_lower:
            category = 'bill'
        elif 'cnic' in user_input_lower or 'verify' in user_input_lower:
            category = 'cnic'
        
        faqs = get_faqs(category)
        faq_text = '\n\n'.join(faqs)
        
        if language == 'اردو':
            return f"📚 اکثر پوچھے گئے سوالات ({category})\n\n{faq_text}\n\nمزید مدد کے لیے پوچھیں!"
        else:
            return f"📚 Frequently Asked Questions ({category.title()})\n\n{faq_text}\n\nAsk me anything else!"
    
    # Complaint Intent
    elif any(word in user_input_lower for word in ['complaint', 'problem', 'issue', 'error', 'wrong']):
        if language == 'اردو':
            return "📝 شکایت درج کرنا\n\nبرائے مہربانی تفصیل دیں:\n1. مسئلے کی نوعیت\n2. آپ کا CNIC\n3. رابطہ نمبر\n\nہماری ٹیم 24 گھنٹے میں جواب دے گی۔\n\nفوری مدد: 111-GOVAI-HELP"
        else:
            return "📝 File a Complaint\n\nPlease provide:\n1. Nature of problem\n2. Your CNIC\n3. Contact number\n\nOur team will respond within 24 hours.\n\n🆘 Urgent Help: 111-GOVAI-HELP"
    
    # Emergency Intent
    elif any(word in user_input_lower for word in ['emergency', 'urgent', 'immediate', 'asap']):
        if language == 'اردو':
            return "🚨 ایمرجنسی رابطے\n\n• پولیس: 15\n• ایمبولینس: 1122\n• فائر بریگیڈ: 16\n• شہری ہیلپ لائن: 1334\n\nقریبی دفتر: maps.govai.pk/offices"
        else:
            return "🚨 Emergency Contacts\n\n• Police: 15\n• Ambulance: 1122\n• Fire Brigade: 16\n• Citizen Helpline: 1334\n\n📍 Nearest Office: maps.govai.pk/offices"
    
    # Greeting Intent
    elif any(word in user_input_lower for word in ['hello', 'hi', 'salam', 'hey', 'assalam']):
        if language == 'اردو':
            return "السلام علیکم! 👋\n\nGovAI میں خوش آمدید!\n\nمیں آپ کی مدد کیسے کر سکتا ہوں؟\n\n✅ بل چیک کریں\n✅ CNIC تصدیق\n✅ شکایت درج کریں\n✅ FAQs دیکھیں\n\nبس اپنا سوال ٹائپ کریں!"
        else:
            return "Hello! 👋 Welcome to GovAI Assistant!\n\nI can help you with:\n\n✅ Check Bills (Electricity, Gas, Water)\n✅ CNIC Verification\n✅ File Complaints\n✅ FAQs & Guides\n✅ Emergency Services\n\nJust type your question!"
    
    # Default Response with Suggestions
    else:
        if language == 'اردو':
            return "میں یہاں مدد کے لیے ہوں! 😊\n\nآپ یہ کر سکتے ہیں:\n\n💡 'میرا بل چیک کریں'\n💡 'CNIC تصدیق کریں'\n💡 'FAQs دیکھیں'\n💡 'شکایت درج کریں'\n\nیا اپنا سوال براہ راست پوچھیں!"
        else:
            return "I'm here to help! 😊\n\nTry asking:\n\n💡 'Check my bill'\n💡 'Verify my CNIC'\n💡 'Show FAQs'\n💡 'File a complaint'\n💡 'Emergency contacts'\n\nOr ask any question directly!"

# Configure page
st.set_page_config(
    page_title="🏛️ GovAI - Government Transparency Platform",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple Light Theme CSS
st.markdown("""
<style>
    /* Import Stylish Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
    
    /* Light Theme Variables */
    :root {
        --primary: #6366f1;
        --secondary: #8b5cf6;
        --accent: #ec4899;
        --success: #10b981;
        --bg-light: #fafafa;
        --card: #ffffff;
        --text: #1f2937;
        --text-light: #6b7280;
        --border: #e5e7eb;
    }

    /* Clean Background - Pure White */
    .stApp {
        background: #ffffff;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Main container */
    .main .block-container {
        background: transparent;
    }
    
    /* Stylish Headers */
    h1 {
        font-family: 'Playfair Display', serif;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        letter-spacing: -0.3px;
    }

    /* Stylish Header with Light Gradient */
    .main-header {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.15);
        margin-bottom: 2.5rem;
    }

    .main-header h1 {
        color: white;
        font-size: 3rem;
        font-weight: 700;
        font-family: 'Playfair Display', serif;
        margin: 0 0 0.75rem 0;
        letter-spacing: -1px;
    }

    .main-header p {
        color: rgba(255,255,255,0.95);
        font-size: 1.2rem;
        margin: 0;
        font-weight: 400;
        letter-spacing: 0.3px;
    }

    /* Stylish Light Cards */
    .metric-card {
        background: #fafafa;
        padding: 1.75rem;
        border-radius: 16px;
        border: 1px solid #e5e7eb;
        margin: 1rem 0;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    .metric-card:hover {
        transform: translateY(-4px);
        border-color: var(--primary);
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.12);
    }

    .metric-card h3 {
        color: var(--text);
        font-weight: 600;
        margin-bottom: 0.75rem;
        font-size: 1.15rem;
        letter-spacing: -0.3px;
    }

    .metric-card p {
        color: var(--text);
        margin: 0.5rem 0;
        line-height: 1.7;
        font-size: 0.95rem;
    }
    
    .metric-card strong {
        color: var(--text);
        font-weight: 600;
    }

    /* Chat Container */
    .chat-container {
        background: #fafafa;
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.5rem;
        min-height: 350px;
        max-height: 450px;
        overflow-y: auto;
        margin: 1rem 0;
    }

    .user-message {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        padding: 1rem 1.3rem;
        border: none;
        border-radius: 16px 16px 4px 16px;
        margin: 0.8rem 0;
        max-width: 70%;
        margin-left: auto;
        text-align: right;
        box-shadow: 0 3px 10px rgba(99, 102, 241, 0.25);
        font-size: 0.95rem;
        line-height: 1.5;
    }

    .bot-message {
        background: white;
        color: var(--text);
        padding: 1rem 1.3rem;
        border: 2px solid #e5e7eb;
        border-radius: 16px 16px 16px 4px;
        margin: 0.8rem 0;
        max-width: 70%;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        font-size: 0.95rem;
        line-height: 1.5;
    }

    /* Stylish Buttons with Light Theme */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 0.95rem;
        letter-spacing: 0.3px;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25);
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.35);
        background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
    }

    /* Stylish Sidebar - White Background, Black Text */
    section[data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 2px solid #e5e7eb;
        box-shadow: 4px 0 12px rgba(0,0,0,0.03);
    }
    
    section[data-testid="stSidebar"] > div {
        background: #ffffff !important;
        padding: 1.5rem 1rem;
    }
    
    /* Sidebar text - All Black with Better Typography */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: var(--text) !important;
        font-weight: 600;
        letter-spacing: -0.3px;
    }
    
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] label {
        color: var(--text) !important;
        font-weight: 400;
    }
    
    /* Sidebar selectbox - White Background */
    section[data-testid="stSidebar"] .stSelectbox label {
        color: var(--text) !important;
        font-weight: 500;
    }
    
    section[data-testid="stSidebar"] .stSelectbox > div > div {
        background: #ffffff !important;
        color: var(--text) !important;
        border: 2px solid #e5e7eb;
        border-radius: 10px;
    }
    
    section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] {
        background: #ffffff !important;
    }
    
    /* Sidebar markdown */
    section[data-testid="stSidebar"] .stMarkdown {
        color: var(--text) !important;
    }

    /* Inputs - White Background, Black Text */
    .stTextInput > div > div > input,
    .stTextArea textarea,
    .stNumberInput > div > div > input {
        border: 2px solid var(--border);
        border-radius: 10px;
        padding: 0.75rem;
        background: #ffffff !important;
        color: var(--text) !important;
    }
    
    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder,
    .stNumberInput input::placeholder {
        color: #9ca3af !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea textarea:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--text);
        box-shadow: none;
        background: #ffffff !important;
    }
    
    /* Selectbox - White Background with Dropdown */
    .stSelectbox > div > div,
    .stSelectbox [data-baseweb="select"],
    .stSelectbox [role="combobox"] {
        background: #ffffff !important;
        color: var(--text) !important;
        border: 2px solid var(--border);
        border-radius: 10px;
    }
    
    .stSelectbox div[data-baseweb="select"] > div {
        background: #ffffff !important;
        color: var(--text) !important;
    }
    
    /* Dropdown Menu - White Background */
    [data-baseweb="popover"],
    [data-baseweb="menu"] {
        background: #ffffff !important;
        border: 2px solid var(--border);
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    [role="listbox"],
    [role="option"] {
        background: #ffffff !important;
        color: var(--text) !important;
    }
    
    [role="option"]:hover {
        background: #f9fafb !important;
        color: var(--text) !important;
    }
    
    /* Selectbox selected value */
    .stSelectbox [data-baseweb="select"] span {
        color: var(--text) !important;
    }
    
    /* Dropdown list items */
    ul[role="listbox"] {
        background: #ffffff !important;
    }
    
    ul[role="listbox"] li {
        background: #ffffff !important;
        color: var(--text) !important;
    }
    
    ul[role="listbox"] li:hover {
        background: #f3f4f6 !important;
        color: var(--text) !important;
    }

    /* Status Badges - No Background */
    .status-high {
        background: transparent;
        color: #dc2626;
        padding: 0.4rem 1rem;
        border: 2px solid #dc2626;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }

    .status-medium {
        background: transparent;
        color: #d97706;
        padding: 0.4rem 1rem;
        border: 2px solid #d97706;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }

    .status-low {
        background: transparent;
        color: #059669;
        padding: 0.4rem 1rem;
        border: 2px solid #059669;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }

    /* Footer */
    .footer-modern {
        background: transparent;
        padding: 2rem;
        border-radius: 16px;
        border-top: 2px solid var(--border);
        margin-top: 2rem;
        text-align: center;
    }
    
    .footer-modern h3 {
        color: var(--text);
    }

    /* Clean Tabs - Black Text Only */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: transparent;
        padding: 0.5rem;
        border-radius: 12px;
        border: 1px solid var(--border);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.7rem 1.3rem;
        color: var(--text) !important;
        font-weight: 500;
        background: transparent;
    }

    .stTabs [aria-selected="true"] {
        background: transparent;
        color: var(--text) !important;
        border-bottom: 3px solid var(--text);
        font-weight: 700;
    }

    /* Stylish Metrics */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #fafafa 0%, #f9fafb 100%);
        border: 1px solid #e5e7eb;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: all 0.3s ease;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1);
    }

    [data-testid="stMetricValue"] {
        color: var(--primary);
        font-weight: 700;
        font-size: 1.75rem;
        letter-spacing: -0.5px;
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--text);
        font-weight: 500;
        font-size: 0.9rem;
        letter-spacing: 0.3px;
    }
    
    [data-testid="stMetricDelta"] {
        color: var(--text-light);
        font-weight: 500;
    }

    /* Hide branding */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Text colors - All Black */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text) !important;
        font-weight: 600;
    }
    
    p, span, div, label {
        color: var(--text) !important;
    }
    
    /* Streamlit components */
    .stMarkdown {
        color: var(--text) !important;
    }
    
    /* Success/Info/Warning/Error boxes - Black Text */
    .stAlert {
        background: transparent !important;
        border-width: 2px;
        color: var(--text) !important;
    }
    
    [data-testid="stInfo"],
    [data-testid="stSuccess"],
    [data-testid="stWarning"],
    [data-testid="stError"] {
        background: transparent !important;
        color: var(--text) !important;
    }
    
    [data-testid="stInfo"] *,
    [data-testid="stSuccess"] *,
    [data-testid="stWarning"] *,
    [data-testid="stError"] * {
        color: var(--text) !important;
    }
    
    /* Remove backgrounds from selectbox */
    .stSelectbox > div > div {
        background: #ffffff;
        color: var(--text) !important;
    }
    
    .stSelectbox label {
        color: var(--text) !important;
    }
    
    /* Buttons text */
    .stButton > button {
        color: #ffffff !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        color: var(--text) !important;
        background: transparent !important;
    }
    
    /* Dataframe */
    .stDataFrame {
        color: var(--text) !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'selected_language' not in st.session_state:
    st.session_state.selected_language = 'English'
if 'user_cnic' not in st.session_state:
    st.session_state.user_cnic = None
if 'bill_data' not in st.session_state:
    st.session_state.bill_data = None

# Header
st.markdown("""
<div class="main-header">
    <h1>GovAI Platform</h1>
    <p>Smart Government Services & Transparency</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### Quick Navigation")
    
    # Language selection
    language = st.selectbox(
        "Select Language",
        ["English", "اردو"],
        index=0,
        key="language_selector"
    )
    st.session_state.selected_language = language
    
    st.markdown("---")
    st.markdown("### System Status")
    st.success("All systems operational")
    st.info("Real-time processing active")
    st.warning("High performance mode")
    
    st.markdown("---")
    st.markdown("### Quick Actions")
    if st.button("Run System Health Check"):
        st.balloons()
        st.success("System health: EXCELLENT")

# Main content with tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Dashboard", 
    "Fraud Detection", 
    "Bill Services", 
    "AI Assistant"
])

with tab1:
    st.header("Analytics Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Budget Processed",
            value="$124.7M",
            delta="12.3% increase"
        )
    
    with col2:
        st.metric(
            label="Fraud Cases Detected",
            value="247",
            delta="-8.1% this month"
        )
    
    with col3:
        st.metric(
            label="System Uptime",
            value="99.94%",
            delta="0.02% improvement"
        )
    
    with col4:
        st.metric(
            label="Citizens Served",
            value="45,821",
            delta="23.1% increase"
        )
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Sample data for budget analysis
        budget_data = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'Budget': [20, 25, 30, 28, 35, 40],
            'Spent': [18, 22, 28, 26, 32, 38]
        })
        
        fig = px.bar(budget_data, x='Month', y=['Budget', 'Spent'], 
                    title="Monthly Budget vs Spending",
                    barmode='group')
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Sample fraud detection data
        fraud_data = pd.DataFrame({
            'Risk Level': ['Low', 'Medium', 'High'],
            'Count': [156, 67, 24]
        })
        
        fig = px.pie(fraud_data, values='Count', names='Risk Level',
                    title="Fraud Risk Distribution",
                    color_discrete_sequence=['#10b981', '#f59e0b', '#ef4444'])
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("Fraud Detection")
    
    st.markdown("""
    <div class="metric-card">
        <h3>Smart Contract Analysis</h3>
        <p>Our AI system analyzes government contracts in real-time to detect potential fraud and irregularities.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Contract Details")
        contract_number = st.text_input("Contract Number", placeholder="e.g., HIGH-RISK-001")
        description = st.text_area("Description", placeholder="Enter contract description...")
        amount = st.number_input("Amount ($)", min_value=0, value=100000)
        supplier = st.text_input("Supplier", placeholder="Supplier name...")
        country = st.selectbox("Country", ["Pakistan", "India", "Bangladesh", "Other"])
        
        if st.button("Analyze Contract", type="primary"):
            with st.spinner("Analyzing contract for fraud indicators..."):
                time.sleep(2)
                
                # Simulate fraud detection
                risk_score = np.random.random()
                if amount > 10000000 or "emergency" in description.lower():
                    risk_score = 0.8 + np.random.random() * 0.2
                elif amount < 50000:
                    risk_score = np.random.random() * 0.3
                
                risk_level = "HIGH" if risk_score > 0.7 else "MEDIUM" if risk_score > 0.4 else "LOW"
                
                st.success("Analysis Complete!")
                
                col_result1, col_result2 = st.columns(2)
                with col_result1:
                    st.metric("Risk Score", f"{risk_score:.3f}")
                with col_result2:
                    if risk_level == "HIGH":
                        st.markdown(f'<span class="status-high">{risk_level} RISK</span>', unsafe_allow_html=True)
                    elif risk_level == "MEDIUM":
                        st.markdown(f'<span class="status-medium">{risk_level} RISK</span>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<span class="status-low">{risk_level} RISK</span>', unsafe_allow_html=True)
    
    with col2:
        st.subheader("Risk Assessment")
        
        # Risk factors
        st.markdown("### Key Risk Indicators")
        
        risk_factors = [
            ("Contract Value", "High" if amount > 5000000 else "Medium" if amount > 1000000 else "Low"),
            ("Timeline", "Urgent" if "emergency" in description.lower() else "Normal"),
            ("Supplier History", "New" if "new" in supplier.lower() else "Established"),
            ("Geographic Risk", "Low" if country == "Pakistan" else "Medium")
        ]
        
        for factor, status in risk_factors:
            if status in ["High", "Urgent", "New"]:
                st.error(f"{factor}: {status}")
            elif status == "Medium":
                st.warning(f"{factor}: {status}")
            else:
                st.success(f"{factor}: {status}")

with tab3:
    st.header("Bill Services")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Citizen Bill Lookup")
        
        st.markdown("""
        <div class="metric-card">
            <h3>Quick Bill Check</h3>
            <p>Enter your CNIC to view all pending bills and payment history.</p>
        </div>
        """, unsafe_allow_html=True)
        
        cnic = st.text_input("CNIC Number", placeholder="42101-1234567-1")
        
        if st.button("Search Bills", type="primary"):
            if cnic:
                with st.spinner("Searching for bills..."):
                    time.sleep(1)
                    
                    # Sample bill data
                    bills_data = {
                        "42101-1234567-1": {
                            "name": "Ahmed Ali Khan",
                            "bills": [
                                {"type": "Electricity", "amount": 3420, "due_date": "2024-01-15", "status": "Pending"},
                                {"type": "Water", "amount": 890, "due_date": "2024-01-20", "status": "Paid"},
                                {"type": "Gas", "amount": 1567, "due_date": "2024-01-25", "status": "Pending"}
                            ]
                        },
                        "42201-2345678-2": {
                            "name": "Fatima Sheikh",
                            "bills": [
                                {"type": "Electricity", "amount": 2876, "due_date": "2024-01-18", "status": "Paid"},
                                {"type": "Property Tax", "amount": 15600, "due_date": "2024-02-01", "status": "Pending"}
                            ]
                        }
                    }
                    
                    if cnic in bills_data:
                        citizen = bills_data[cnic]
                        st.success(f"Found records for: **{citizen['name']}**")
                        
                        for bill in citizen['bills']:
                            with st.expander(f"{bill['type']} - ${bill['amount']}"):
                                col_bill1, col_bill2, col_bill3 = st.columns(3)
                                with col_bill1:
                                    st.write(f"**Amount:** ${bill['amount']}")
                                with col_bill2:
                                    st.write(f"**Due Date:** {bill['due_date']}")
                                with col_bill3:
                                    if bill['status'] == 'Pending':
                                        st.error(f"**Status:** {bill['status']}")
                                    else:
                                        st.success(f"**Status:** {bill['status']}")
                    else:
                        st.error("No citizen found with this CNIC")
            else:
                st.warning("Please enter a CNIC number")
    
    with col2:
        st.subheader("Payment Analytics")
        
        # Payment statistics
        payment_stats = pd.DataFrame({
            'Payment Method': ['Online', 'Bank', 'Cash', 'Mobile'],
            'Percentage': [45, 30, 15, 10]
        })
        
        fig = px.pie(payment_stats, values='Percentage', names='Payment Method',
                    title="Payment Methods Distribution")
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        <div class="metric-card">
            <h3>Payment Tips</h3>
            <p>• Pay online for instant confirmation</p>
            <p>• Set up auto-pay to avoid late fees</p>
            <p>• Check bills monthly for accuracy</p>
            <p>• Keep payment receipts for records</p>
        </div>
        """, unsafe_allow_html=True)

with tab4:
    st.header("AI Assistant")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Main chat box wrapper
        st.markdown("""
        <div style="
            background: white;
            border: 2px solid #e5e7eb;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            margin-bottom: 1rem;
        ">
        """, unsafe_allow_html=True)
        
        st.subheader("Chat with GovAI Assistant")
        
        # Chat container
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Display chat history
        for message in st.session_state.chat_history:
            if message['type'] == 'user':
                st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bot-message">{message["content"]}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Chat input section
        st.markdown('<div style="margin-top: 1rem;">', unsafe_allow_html=True)
        user_input = st.text_input("Type your message...", placeholder="How can I help you today?", key="chat_input", label_visibility="collapsed")
        
        col_send, col_clear = st.columns([3, 1])
        
        with col_send:
            send_button = st.button("Send", type="primary", use_container_width=True)
        
        with col_clear:
            if st.button("Clear", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)  # Close main chat box
        
        # Only process when button is clicked AND there's text
        if send_button and user_input and user_input.strip():
            # Add user message
            st.session_state.chat_history.append({
                'type': 'user',
                'content': user_input
            })
            
            # Generate bot response with advanced logic
            with st.spinner("Thinking..."):
                time.sleep(0.5)
                response = get_chatbot_response(user_input, st.session_state.selected_language)
            
            # Add bot response
            st.session_state.chat_history.append({
                'type': 'bot',
                'content': response
            })
            
            st.rerun()
    
    with col2:
        st.subheader("Quick Help")
        
        st.markdown("""
        <div class="metric-card">
            <h3>🔍 Try These Commands</h3>
            <p><strong>Check Bill:</strong></p>
            <p>• "Check my bill 35202-1234567-1"</p>
            <p>• "Show bill for BILL-123456"</p>
            <br>
            <p><strong>Verify CNIC:</strong></p>
            <p>• "Verify 35202-1234567-1"</p>
            <p>• "CNIC verification"</p>
            <br>
            <p><strong>Get Help:</strong></p>
            <p>• "Show FAQs"</p>
            <p>• "How to pay bill?"</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="metric-card">
            <h3>💳 Sample Test Data</h3>
            <p><strong>Test CNICs:</strong></p>
            <p>• 35202-1234567-1 (Ahmed Khan)</p>
            <p>• 42101-9876543-2 (Sara Ali)</p>
            <p>• 33101-5678901-2 (Hassan Raza)</p>
            <br>
            <p><strong>Test Bills:</strong></p>
            <p>• BILL-123456 (Water Bill)</p>
            <p>• Any valid CNIC (generates bill)</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="metric-card">
            <h3>✨ Features</h3>
            <p>✅ Instant Bill Checking</p>
            <p>✅ CNIC Verification</p>
            <p>✅ Comprehensive FAQs</p>
            <p>✅ Complaint Filing</p>
            <p>✅ Emergency Contacts</p>
            <p>✅ English & اردو Support</p>
            <p>✅ 24/7 AI Assistant</p>
        </div>
        """, unsafe_allow_html=True)



# Simple Footer
st.markdown("---")
st.markdown("""
<div class="footer-modern">
    <h3>GovAI Platform</h3>
    <p style="color: #6b7280; margin-top: 0.5rem;">
        AI-Powered Government Services | Secure & Transparent | Multilingual Support
    </p>
    <p style="color: #9ca3af; font-size: 0.9rem; margin-top: 0.5rem;">
        © 2025 GovAI Platform. All rights reserved.
    </p>
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    pass