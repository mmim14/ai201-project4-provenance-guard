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
