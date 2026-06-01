def process_questionnaire(responses):
    """
    Converts descriptive answers into numerical values.
    responses: dict mapping question to answer (e.g., {"q1": "Strongly Agree"})
    """
    scoring = {
        "Strongly Agree": 5,
        "Agree": 4,
        "Neutral": 3,
        "Disagree": 2,
        "Strongly Disagree": 1
    }
    
    numerical_responses = {}
    for key, value in responses.items():
        numerical_responses[key] = scoring.get(value, 3) # default to Neutral if unknown
        
    return numerical_responses
