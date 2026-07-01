# ai201-project4-provenance-guard

## What It Is
A backend system that any creative sharing platform plug into to classify submitted content, score confidence in that classification, surface a transparency label to users, and handles appeals from creators who believe they have been misclassified 

## Confidence Score & Transparency Label
    - A confidence score of 100% means it's completely AI.
    - A confidence score of 0 means, it's completely human. 
    - Uncertainty cases are between 40%-60%. 
### Labels:
    - High-Confidence Human: the system is fairly sure the content is created by a human. Scores from 0.0 to 4.0 is in this category. 
    - Uncertain: The system are not sure if the text is human created or AI generated. Confidence score between 4.0 and 6.0. 
    - High-Confidence AI: the model is fairly sure the content is AI generated. Score from 6.0 to 1.0 is in this category. 


For more transparency, I will display the score to the user and explain what the confidence score is. A 65% confidence score is different than a 95% confidence score. 


## Signals

1. Semantic (detection signal)
2. Stylometruc heuristics: vocabulary diversity, punctuation density, or sentence length variation

## Rate Limiting
    - uses Flask limiter
    - the limits should allow real user to submit request without much interruption, prevent spam, and not flood the system and consume a lot of API calls.
        - The model llama-3.3-70b-versatile that I'm using has 30 requests per minute limit for free tier. 
        - Limit 1: 5 submission per minute sounds reasonable as a human won't probably enter more than 5 submission in a minute 
        - Limit 2: 20 submissions per hour to protect my free-tier API limits and so other users could also use it without breaking the pipeline. Too many calls will return an 429 error ("Too Many Requests") from Groq. 

## False positive
A false positive would be labeling a human’s work as AI-generated. 

A false negative would be labeling a AI-generated work human.

In our system, a false positive is much worse than a false negative. 
