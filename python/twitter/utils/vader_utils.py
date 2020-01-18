from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from nltk import tokenize

analyser = SentimentIntensityAnalyzer()


def sentiment_analyzer_scores(sentence):
    score = analyser.polarity_scores(sentence)
    return score


def divide_text(text):
    sentences = tokenize.sent_tokenize(text)
    return sentences


def get_sentiment(scores):
    if scores['compound'] >= 0.05:
        sentiment = "positive"
        score = scores['compound']
    elif scores['compound'] <= -0.05:
        sentiment = "negative"
        score = scores['compound']
    else:
        sentiment = "neutral"
        score = scores['compound']
    return sentiment, score


# def process_text(text, id):
#     connection = get_connection()
#     sentences = divide_text(text)
#     for sentence in sentences:
#         scores = sentiment_analyzer_scores(sentence)
#         sentiment, score = get_sentiment(scores)
#         insert_sentiment(sentiment, score, id, connection)
#     print("All lines have benn processed")


def prcss_text(text):
    if isinstance(text, list):
        text = str(text)
    sentences = divide_text(text)
    for sentence in sentences:
        scores = sentiment_analyzer_scores(sentence)
        sentiment, score = get_sentiment(scores)
    return sentiment, score
