# Анализ тем, стиля и вовлечённости

def extract_topics(text):
    tech = ['api', 'database', 'server', 'code', 'software', 'bug', 'feature']
    business = ['revenue', 'customer', 'sales', 'marketing', 'strategy', 'growth']
    support = ['help', 'issue', 'problem', 'error', 'troubleshoot', 'fix']
    text = text.lower()
    topics = []
    if any(w in text for w in tech):
        topics.append('technical')
    if any(w in text for w in business):
        topics.append('business')
    if any(w in text for w in support):
        topics.append('support')
    return topics or ['general']

def analyze_communication_style(messages):
    if not messages:
        return 'neutral'
    last = messages[-3:]
    user_msgs = [m for m in last if m['role'] == 'user']
    if not user_msgs:
        return 'neutral'
    avg = sum(len(m['content']) for m in user_msgs) / len(user_msgs)
    if avg > 200:
        return 'detailed'
    if avg < 50:
        return 'concise'
    return 'balanced'

def calculate_engagement_score(messages):
    users = [m for m in messages if m['role'] == 'user']
    return min(len(users) * 10, 100) if users else 0 