import streamlit as st
import plotly.graph_objects as go
from analyzer import extract_topics
from typing import List, Dict, Any

def create_conversation_insights(chat):
    """Shows real-time conversation analytics for the given chat."""
    analytics = chat['analytics']
    if not chat['messages']:
        return
    col1, col2, col3 = st.columns(3)
    with col1:
        engagement_score = analytics['user_engagement_score']
        st.metric(
            "Engagement Score",
            f"{engagement_score}%",
            delta=f"+{min(10, len(chat['messages']))}" if len(chat['messages']) > 2 else None
        )
    with col2:
        avg_response_time = sum(analytics['response_times']) / len(analytics['response_times']) if analytics['response_times'] else 0
        st.metric("Avg Response Time", f"{avg_response_time:.1f}s")
    with col3:
        conversation_depth = len(set(topic for topics in [extract_topics(msg['content']) for msg in chat['messages']] for topic in topics))
        st.metric("Topic Diversity", conversation_depth)
    if len(chat['messages']) > 4:
        message_lengths = [len(msg['content']) for msg in chat['messages']]
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=message_lengths,
            mode='lines+markers',
            name='Message Length',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8)
        ))
        fig.update_layout(
            title="Conversation Flow Analysis",
            xaxis_title="Message Number",
            yaxis_title="Message Length (characters)",
            height=300,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

def render_conversation_flow(messages: List[Dict[str, Any]]):
    """Displays user and assistant messages as bubbles."""
    st.markdown('<div class="conversation-flow">', unsafe_allow_html=True)
    for message in messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="message-bubble user-bubble">
                <strong>You</strong> • {message.get('timestamp', '')}<br>
                {message['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="message-bubble assistant-bubble">
                <strong>🌟 Personal Assistant</strong> • {message.get('timestamp', '')}<br>
                {message['content']}
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True) 