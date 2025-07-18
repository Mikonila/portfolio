from analyzer import SmartResponseAnalyzer

def test_extract_topics():
    assert SmartResponseAnalyzer.extract_topics('API and database error') == ['technical', 'support']
    assert SmartResponseAnalyzer.extract_topics('Customer growth and sales') == ['business']
    assert SmartResponseAnalyzer.extract_topics('Hello world!') == ['general']

def test_analyze_communication_style():
    msgs = [
        {'role': 'user', 'content': 'Short.'},
        {'role': 'user', 'content': 'Another short.'},
        {'role': 'user', 'content': 'Third.'}
    ]
    assert SmartResponseAnalyzer.analyze_communication_style(msgs) == 'concise'
    msgs = [
        {'role': 'user', 'content': 'A'*250},
        {'role': 'user', 'content': 'B'*220},
        {'role': 'user', 'content': 'C'*210}
    ]
    assert SmartResponseAnalyzer.analyze_communication_style(msgs) == 'detailed'

def test_calculate_engagement_score():
    msgs = [{'role': 'user', 'content': 'Hi'} for _ in range(5)]
    assert SmartResponseAnalyzer.calculate_engagement_score(msgs) == 50
    assert SmartResponseAnalyzer.calculate_engagement_score([]) == 0 