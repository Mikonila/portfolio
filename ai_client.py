import openai
import os
from typing import List, Dict, Any

# Ключ и модель берём из .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def get_adaptive_system_prompt(user_profile: Dict[str, Any], conversation_context: Dict[str, Any]) -> str:
    """Формирует системный промпт на основе профиля пользователя и контекста."""
    base_prompt = (
        "You are Valerya's Personal Assistant, an advanced conversational AI for customer success."
    )
    style_adapt = {
        'detailed': "Give detailed, step-by-step answers with examples.",
        'concise': "Be brief and to the point, but helpful.",
        'balanced': "Balance brevity and detail."
    }
    context_info = ""
    if conversation_context.get('dominant_topics'):
        topics = ', '.join(conversation_context['dominant_topics'])
        context_info = f"The conversation has focused on: {topics}. Adjust accordingly."
    language_info = ""
    if user_profile.get('language') == 'en':
        language_info = "Always reply in English, regardless of the user's input language."
    return f"{base_prompt}\n{style_adapt.get(user_profile['communication_style'], '')}\n{context_info}\n{language_info}"

def get_smart_response(
    messages: List[Dict[str, str]],
    user_profile: Dict[str, Any],
    analytics: Dict[str, Any]
) -> str:
    """Генерирует ответ AI с учётом профиля пользователя и аналитики."""
    if not OPENAI_API_KEY:
        return "OPENAI_API_KEY not found. Please add it to .env."
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        context = {
            'dominant_topics': list(analytics['topics_discussed'].keys())[:3],
            'engagement_level': analytics['user_engagement_score']
        }
        system_prompt = get_adaptive_system_prompt(user_profile, context)
        if analytics['user_engagement_score'] > 70:
            system_prompt += "\nThe user is highly engaged — feel free to ask clarifying questions."
        # Приводим сообщения к нужному формату для OpenAI
        formatted_messages = []
        for msg in messages:
            if msg['role'] in ('user', 'assistant', 'system'):
                formatted_messages.append({'role': msg['role'], 'content': msg['content']})
        all_messages = [{'role': 'system', 'content': system_prompt}] + formatted_messages
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=all_messages,
            temperature=0.7,
            max_tokens=600,
            presence_penalty=0.1,
            frequency_penalty=0.1
        )
        content = response.choices[0].message.content
        return str(content) if content else ""
    except Exception as e:
        return f"Error: {str(e)[:50]}..." 