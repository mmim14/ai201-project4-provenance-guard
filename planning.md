## Confidence Score & Transparency Label
    - A confidence score of 100% means it's completely AI.
    - A confidence score of 0 means, it's completely human. 
    - Uncertainty cases are between 40%-60%. 
### Labels:
    - High-Confidence Human: the system is confident that the content is created by a human. Scores from 0% to 40% is in this category. 
    - Uncertain: The system is not sure if the text is human created or AI generated. Confidence score between 40% and 60% is in this category.  
    - High-Confidence AI: the model is confident that the content is AI generated. Score from 6.0 to 1.0 is in this category. 


For more transparency, I will display the score to the user and explain what the confidence score is. A 65% confidence score is different than a 95% confidence score. 


## Signals

1. Semantic (detection signal)
2. Stylometruc heuristics: vocabulary diversity, punctuation density, or sentence length variation


## Architecture
Required feature: 
(1) Content Submission Endpoint: The user submits a payload containing raw text and a creator_id to the /submit endpoint. 
    - POST to /submit endpoint
    - the backend receives the payload, validates the input, and generate a uuid to track the text
(2) Multi-Signal Detection Pipeline: 
    - Semantic analysis: The raw text is passed to function that call Groq API using llama-3.3-70b-versatile model. The LLM evaluates the contex, tone, and sematics, and then returns a classification score between 0 and 1. 0 is human, and 1 is AI. The function should be asynchronous, so we could run another function for the structural signal
    - Structural Statistics: at the same time, a local Python module analyzes the text to calculate its stylometric heuristics. It should compute type token ratio to find vocabulary diversity, punctuation density, and sentence length variance. It calculates these metrics into a score between 0 and 1. 
(3) Confidence Scoring with Uncertainty:
    - The confidence score is sent to an aggregator system that calculates a weighted average giving 50% weight to LLM semantic and 50% weight to structural heuristics to produce a final confidence score. 
(4) Transparency Label:
    - the score is compared against the system's threshold. A score from 0.0 to 4.0 is high-confidence humman. A score between 4.0 and 6.0 is uncertain. The score from 6.0 to 1.0 is high-confidence AI. 
    - before sending the response to the user, the system should audit it 
    - The system should construct a JSON response contained the content, the confidence score (in percentage), the overall attibution verdict, and the plain-language transparency label text 
 (5) Appeals Workflow:
 
 (6) Rate Limiting
 
 (7) Audit Log:
    - Log the response before sending response to the user. The system should compile JSON strcutured entry containing the timestamp, uuid, creator_id, both signal scores separately, final combined score, and the intitial status ["classified"]. This should be saved to a JSON file. 

    




