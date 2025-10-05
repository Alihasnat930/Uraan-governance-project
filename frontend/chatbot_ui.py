#!/usr/bin/env python3
"""
GovAI Citizen Chatbot UI - Streamlit Interface
"""

import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd

API_BASE_URL = "http://localhost:8080"

def main():
    st.set_page_config(
        page_title="GovAI Citizen Services",
        page_icon="🏛️",
        layout="wide"
    )
    
    st.title("🏛️ GovAI Citizen Services")
    st.markdown("**Government AI Assistant**")
    
    # Language selection
    col1, col2 = st.columns([3, 1])
    with col2:
        language = st.selectbox(
            "Language",
            ["english", "urdu"],
            format_func=lambda x: "English" if x == "english" else "Urdu"
        )
    
    # Sidebar
    with st.sidebar:
        st.header("👤 User Information")
        user_cnic = st.text_input("CNIC Number", placeholder="42101-1234567-1")
        
        if st.button("Check My Bills"):
            if user_cnic:
                check_user_bills(user_cnic)
            else:
                st.error("Please enter CNIC number")
    
    # Chat interface
    st.header("💬 Chat with Government Assistant")
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(chat["user_message"])
        with st.chat_message("assistant"):
            st.write(chat["bot_response"])
    
    # Chat input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        with st.chat_message("user"):
            st.write(user_input)
        
        with st.chat_message("assistant"):
            response = send_chat_message(user_input, user_cnic, language)
            if response:
                st.write(response["response"])
                st.session_state.chat_history.append({
                    "user_message": user_input,
                    "bot_response": response["response"],
                    "intent": response["intent"],
                    "language": response["language"]
                })
            else:
                st.error("Sorry, I couldn't process your request.")

def send_chat_message(message: str, user_id: str = "default_user", language: str = "english"):
    try:
        response = requests.post(
            f"{API_BASE_URL}/assistant",
            json={"message": message, "user_id": user_id, "language": language},
            timeout=10
        )
        return response.json() if response.status_code == 200 else None
    except:
        return None

def check_user_bills(cnic: str):
    try:
        response = requests.post(
            f"{API_BASE_URL}/bill-inquiry",
            json={"cnic": cnic},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            st.success(f"Welcome {data['user']['name']}!")
            
            if data['bills']:
                bills_df = pd.DataFrame(data['bills'])
                st.dataframe(bills_df)
                st.metric("Total Amount", f"Rs. {data['total_amount']:,.2f}")
            else:
                st.info("No bills found.")
        else:
            st.error("User not found.")
    except:
        st.error("Connection error.")

if __name__ == "__main__":
    main()