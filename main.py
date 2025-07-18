import streamlit as st
import json
import time
import hashlib
from datetime import datetime
from analyzer import extract_topics, analyze_communication_style, calculate_engagement_score
from ai_client import get_smart_response
from ui import create_conversation_insights, render_conversation_flow
from dotenv import load_dotenv
import uuid

load_dotenv()

# --- Chat management helpers ---
def get_new_chat_id():
    return str(uuid.uuid4())[:8]

def get_chat_title(messages):
    if not messages:
        return "New Chat"
    for msg in messages:
        if msg['role'] == 'user' and msg['content'].strip():
            return msg['content'][:30] + ("..." if len(msg['content']) > 30 else "")
    return "Chat"

# --- Main app ---
def main():
    st.set_page_config(
        page_title="Valerya's Personal Assistant",
        page_icon="🌟",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        * { font-family: 'Inter', sans-serif; }
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            padding: 2rem;
            border-radius: 20px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            border: 1px solid rgba(255, 255, 255, 0.18);
        }
        .conversation-flow {
            display: flex;
            flex-direction: column;
            gap: 1rem;
            max-height: 500px;
            overflow-y: auto;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        .message-bubble {
            max-width: 80%;
            padding: 12px 16px;
            border-radius: 18px;
            position: relative;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            animation: slideIn 0.3s ease-out;
        }
        .user-bubble {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            align-self: flex-end;
            margin-left: auto;
        }
        .assistant-bubble {
            background: rgba(255, 255, 255, 0.9);
            color: #2c3e50;
            align-self: flex-start;
            border-left: 4px solid #3498db;
        }
        .thinking-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #7f8c8d;
            font-style: italic;
        }
        .pulse-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #3498db;
            animation: pulse 1.5s infinite;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulse {
            0%, 100% { opacity: 0.4; }
            50% { opacity: 1; }
        }
        .insight-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
            margin: 0.5rem 0;
        }
        .typing-indicator {
            background: #ecf0f1;
            border-radius: 18px;
            padding: 12px 16px;
            margin: 0.5rem 0;
            width: fit-content;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- Chat state ---
    if 'chats' not in st.session_state:
        st.session_state.chats = {}
    if 'current_chat_id' not in st.session_state:
        chat_id = get_new_chat_id()
        st.session_state.current_chat_id = chat_id
        st.session_state.chats[chat_id] = {
            'messages': [],
            'analytics': {
                'response_times': [],
                'message_lengths': [],
                'topics_discussed': {},
                'user_engagement_score': 0,
                'conversation_depth': 0
            },
            'user_profile': {
                'communication_style': 'balanced',
                'expertise_level': 'beginner',
                'preferred_response_length': 'medium',
                'language': 'en'  # default language is English
            }
        }

    chats = st.session_state.chats
    current_chat_id = st.session_state.current_chat_id
    chat = chats[current_chat_id]

    # --- Sidebar ---
    with st.sidebar:
        st.header("🗂️ Chats")
        if st.button("➕ New Chat"):
            new_id = get_new_chat_id()
            st.session_state.chats[new_id] = {
                'messages': [],
                'analytics': {
                    'response_times': [],
                    'message_lengths': [],
                    'topics_discussed': {},
                    'user_engagement_score': 0,
                    'conversation_depth': 0
                },
                'user_profile': {
                    'communication_style': 'balanced',
                    'expertise_level': 'beginner',
                    'preferred_response_length': 'medium',
                    'language': 'en'
                }
            }
            st.session_state.current_chat_id = new_id
            st.rerun()
        st.markdown("**Select chat:**")
        for cid, cdata in chats.items():
            title = get_chat_title(cdata['messages'])
            if st.button(title, key=f"chat_{cid}"):
                st.session_state.current_chat_id = cid
                st.rerun()
        st.header("⚙️ Adaptation Settings")
        style = st.selectbox(
            "Communication style",
            ['detailed', 'concise', 'balanced'],
            index=['detailed', 'concise', 'balanced'].index(chat['user_profile']['communication_style'])
        )
        chat['user_profile']['communication_style'] = style
        st.info("The assistant adapts to your style!")
        st.header("📊 Conversation Analytics")
        create_conversation_insights(chat)
        if st.button("📈 Download analytics"):
            export_data = {
                "conversation_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "total_messages": len(chat['messages']),
                    "conversation_id": current_chat_id
                },
                "messages": chat['messages'],
                "analytics_summary": chat['analytics'],
                "user_profile": chat['user_profile']
            }
            st.download_button(
                "📊 Download analysis",
                json.dumps(export_data, indent=2),
                file_name=f"valerya_personal_assistant_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

    st.markdown("""
    <div class="main-header">
    <h1>🌟 Valerya's Personal Assistant</h1>
    <p>Adaptive AI assistant with analytics</p>
    <small>Streamlit + OpenAI + user behavior analysis</small>
    </div>
    """, unsafe_allow_html=True)

    render_conversation_flow(chat['messages'])
    if user_input := st.chat_input("💬 Type your message..."):
        start_time = time.time()
        topics = extract_topics(user_input)
        for topic in topics:
            chat['analytics']['topics_discussed'][topic] = chat['analytics']['topics_discussed'].get(topic, 0) + 1
        chat['user_profile']['communication_style'] = analyze_communication_style(
            chat['messages'] + [{"role": "user", "content": user_input}]
        )
        chat['analytics']['user_engagement_score'] = calculate_engagement_score(
            chat['messages']
        )
        user_message = {
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "metadata": {
                "topics": topics,
                "length": len(user_input),
                "engagement_boost": min(10, len(user_input) // 20)
            }
        }
        chat['messages'].append(user_message)
        with st.empty():
            st.markdown("""
            <div class="thinking-indicator">
                <div class="pulse-dot"></div>
                <div class="pulse-dot" style="animation-delay: 0.5s;"></div>
                <div class="pulse-dot" style="animation-delay: 1s;"></div>
                <span>Valerya's Personal Assistant is thinking...</span>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(1.2)
        api_messages = [{"role": msg["role"], "content": msg["content"]} for msg in chat['messages'][-10:]]
        # Передаём язык в get_smart_response через user_profile
        response = get_smart_response(
            api_messages,
            chat['user_profile'],
            chat['analytics']
        )
        response_time = time.time() - start_time
        chat['analytics']['response_times'].append(response_time)
        assistant_message = {
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "insights": {
                "topics": topics,
                "adapted_style": chat['user_profile']['communication_style'],
                "response_time": round(response_time, 2)
            }
        }
        chat['messages'].append(assistant_message)
        st.rerun()

if __name__ == "__main__":
    main() 