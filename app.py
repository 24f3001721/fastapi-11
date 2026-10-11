from fastapi import FastAPI
from pydantic import BaseModel
import re

app = FastAPI()


class SentimentRequest(BaseModel):
    sentences: list[str]


POSITIVE_WORDS = {
    "love", "loved", "like", "great", "excellent", "amazing",
    "awesome", "good", "happy", "wonderful", "fantastic",
    "best", "beautiful", "enjoy", "enjoyed", "perfect",
    "brilliant", "delightful", "excited", "pleased", "helpful",
    "thank", "thanks", "nice", "superb", "recommend", "win",
    "successful", "glad", "hopeful", "impressive"
}

NEGATIVE_WORDS = {
    "hate", "hated", "terrible", "awful", "bad", "sad",
    "horrible", "worst", "poor", "disappointing", "disappointed",
    "angry", "upset", "annoyed", "frustrated", "failed",
    "failure", "broken", "useless", "ugly", "wrong", "problem",
    "problems", "pain", "painful", "scared", "fear", "fearful",
    "unhappy", "miserable", "regret", "boring", "rude",
    "difficult", "sorry", "dislike", "unfortunately"
}

NEGATIONS = {
    "not", "never", "no", "hardly", "isn't", "wasn't",
    "don't", "doesn't", "didn't", "can't", "couldn't",
    "won't", "wouldn't"
}


def classify_sentiment(sentence: str) -> str:
    words = re.findall(r"\b[\w']+\b", sentence.lower())

    positive = 0
    negative = 0
    negate_next = False

    for word in words:
        if word in NEGATIONS:
            negate_next = True
            continue

        if word in POSITIVE_WORDS:
            if negate_next:
                negative += 1
            else:
                positive += 1
            negate_next = False

        elif word in NEGATIVE_WORDS:
            if negate_next:
                positive += 1
            else:
                negative += 1
            negate_next = False

        elif word in {"very", "really", "extremely", "absolutely"}:
            continue
        else:
            # Do not let unrelated words consume a negation.
            continue

    if positive > negative:
        return "happy"
    elif negative > positive:
        return "sad"
    return "neutral"


@app.post("/sentiment")
def analyze_sentiment(request: SentimentRequest):
    results = [
        {
            "sentence": sentence,
            "sentiment": classify_sentiment(sentence)
        }
        for sentence in request.sentences
    ]

    return {"results": results}