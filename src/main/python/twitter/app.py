from twitter.utils.postgres_utils import get_ids_text, insert_sentiment, insert_clsf_sentiment
from twitter.utils.scikit_learn_utils import train_model
from twitter.utils.text_utils import tokenization_and_stem, tweets_cleaner
from twitter.utils.vader_utils import prcss_text
import os.path
import pandas as pd


def vader_run():

    cursor = get_ids_text()

    original_text = cursor.fetchall()
    for id, text in original_text:

        print("Original text : {0}".format(text))
        ttl_token_ls, ttl_sbstmr_token_ls = tokenization_and_stem(tweets_cleaner(text))

        org_text_snt, org_text_score = prcss_text(str(ttl_token_ls))

        insert_sentiment(org_text_snt,
                         org_text_score, id, "vader_score_origin", "vader_type_origin")

        ttl_token_ls_snt, ttl_token_ls_score = \
            prcss_text(str(ttl_token_ls))

        insert_sentiment(ttl_token_ls_snt,
                         ttl_token_ls_score, id, "vader_score_token", "vader_type_token")

        ttl_sbstmr_token_ls_snt, total_sbstmr_token_ls_score = \
            prcss_text(str(ttl_sbstmr_token_ls))

        insert_sentiment(ttl_sbstmr_token_ls_snt,
                         total_sbstmr_token_ls_score, id, "vader_score_stemmer", "vader_type_stemmer")


def get_resource_path():
    my_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.abspath(os.path.join(my_path, os.pardir))


def scikit_learn_run():

    train_path = os.path.join(get_resource_path(), "twitter\\resources\\train.csv")
    train = pd.read_csv(train_path)
    test_path = os.path.join(get_resource_path(), "twitter\\resources\\test.csv")
    test = pd.read_csv(test_path)

    model_MNB = train_model(train, test)

    cursor = get_ids_text()

    original_text = cursor.fetchall()
    for id, text in original_text:
        clean_text = tweets_cleaner(text)
        clean_text = [clean_text]
        sentiment = model_MNB.predict(clean_text)
        insert_clsf_sentiment(sentiment[0], id, 'svmclassifier_sentiment', 'svmclassifier_mark')


def run():
    vader_run()
    scikit_learn_run()