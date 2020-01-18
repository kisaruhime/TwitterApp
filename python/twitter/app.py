from twitter.utils.postgres_utils import get_ids_text, insert_sentiment, insert_clsf_sentiment
from twitter.utils.scikit_learn_utils import train_model_scikit, save_model_scikit, read_model_scikit
from twitter.utils.text_utils import tokenization_and_stem, tweets_cleaner
from twitter.utils.vader_utils import prcss_text
from twitter.utils.lstm_utils import save_model_lstm, train_model_lstm, load_model_lstm
from twitter.utils.common_utils import get_config
import os.path
import pandas as pd
import os
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
import numpy as np
import logging
import logging.handlers

import configparser


def vader_run(user):

    log = logging.getLogger("app." + __name__)
    config = get_config()
    vader_score_col = config['POSTGRES']['VADER_SCORE_COL']
    # vader_score_col = config['POSTGRES']['VADER_SCORE_COL']
    vader_sentiment_col = config['POSTGRES']['VADER_SENTIMENT_COL']

    cursor = get_ids_text(user)

    original_text = cursor.fetchall()
    for id, text in original_text:

        log.info('Original id:{}, cleaned text: {}'.format(id, text))

        ttl_token_ls = tokenization_and_stem(text)
        ttl_token_ls_snt, ttl_token_ls_score = \
            prcss_text(ttl_token_ls)

        log.info('For id: {} vader app score: {} and sentiment: {}'.format(id, ttl_token_ls_score, ttl_token_ls_snt))

        insert_sentiment(user, ttl_token_ls_snt,
                         ttl_token_ls_score, id, vader_score_col, vader_sentiment_col)


def get_resource_path():
    my_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.abspath(os.path.join(my_path, os.pardir))


def scikit_learn_run(user, model_exists=False):

    log = logging.getLogger("app." + __name__)
    config = get_config()

    # train_path = os.path.join(get_resource_path(), config['DATASET']['FILE_LOC'])
    train_path = os.path.join(get_resource_path(), config['DATASET']['TEST_LOC'])
    #train_path = os.path.join(get_resource_path(), "twitter\\resources\\Sentiment-Analysis-Dataset.csv")
    headers = ['Sentiment', 'id', 'date', 'query', 'user', 'SentimentText']
    train = pd.read_csv(train_path, error_bad_lines=False, names=headers, encoding="latin")
    #train = train.rename(columns={"Sentiment": "label", "SentimentText": "tweet"})
    text_col = config['DATASET']['TEXT_COL']
    label_col = config['DATASET']['SENTIMENT_COL']
    train = train[[text_col, label_col]]
    reduced_size = int(config['DATASET']['DATASET_SIZE'])
    train = train.sample(frac=1)
    train = train[:reduced_size]

    train = train.replace({label_col: 4}, 1)

    log.info("train df summary: ")
    log.info(train.describe(percentiles=[.20, .40, .60, .80]))

    model_svn_path = os.path.join(get_resource_path(), config['MODELS']['SCIKIT_MODEL_SVN'])
    model_mb_path = os.path.join(get_resource_path(), config['MODELS']['SCIKIT_MODEL_MB'])

    if not model_exists:
        model_SVN, model_MNB = train_model_scikit(train)
        save_model_scikit(model_SVN, model_svn_path)
        save_model_scikit(model_MNB, model_mb_path)
    else:
        model_SVN = read_model_scikit(model_svn_path)
        model_MNB = read_model_scikit(model_mb_path)

    cursor = get_ids_text(user)
    original_text = cursor.fetchall()
    svn_score_col = config['POSTGRES']['SVN_SCORE_COL']
    svn_sentiment_col = config['POSTGRES']['SVN_SENTIMENT_COL']
    mb_score_col = config['POSTGRES']['MB_SCORE_COL']
    mb_sentiment_col = config['POSTGRES']['MB_SENTIMENT_COL']

    for id, text in original_text:
        clean_text = [text]
        sentiment_svn = model_SVN.predict(clean_text)
        sentiment_mb = model_MNB.predict(clean_text)
        log.info("SVN Sentiment for text: {} is {}".format(text, sentiment_svn))
        log.info("MB Sentiment for text: {} is {}".format(text, sentiment_svn))
        insert_clsf_sentiment(user, sentiment_svn[0], id, svn_sentiment_col, svn_score_col)
        insert_clsf_sentiment(user, sentiment_mb[0], id, mb_sentiment_col, mb_score_col)

def process_user(user, model, max_features=5000):

    log = logging.getLogger("app." + __name__)
    config = get_config()

    cursor = get_ids_text(user)
    tweets = cursor.fetchall()
    tokenizer = Tokenizer(nb_words=max_features, split=' ')
    for id, clean_text in tweets:

        clean_text = [clean_text]
        clean_text_serias = pd.Series(clean_text)
        frame = {'text': clean_text_serias}
        df = pd.DataFrame(frame)
        tokenizer.fit_on_texts(df["text"].values)
        X = tokenizer.texts_to_sequences(df['text'].values)
        X = pad_sequences(X)
        log.info("Model LSTM summary: {}".format(model.summary()))
        log.info("Model input shape {0}".format(model.layers[0].input_length))
        X = np.resize(X, (1, model.layers[0].input_length))
        result = model.predict(X, batch_size=1, verbose=2)
        log.info("Result: {}".format(result))
        lstm_score_col = config['POSTGRES']['LSTM_SCORE_COL']
        lstm_sentiment_col = config['POSTGRES']['LSTM_SENTIMENT_COL']

        sentiment = 0 if result[0][0] >= 0.5 else 1
        insert_clsf_sentiment(user, sentiment, id, lstm_sentiment_col, lstm_score_col)


def lstm_run(user, model_exists=False):

    log = logging.getLogger("app." + __name__)
    config = get_config()
    train_path = os.path.join(get_resource_path(), config['DATASET']['TEST_LOC'])
    headers = ['Sentiment', 'id', 'date', 'query', 'user', 'SentimentText']

    # train_path = os.path.join(get_resource_path(), "twitter\\resources\\Sentiment-Analysis-Dataset.csv")

    train = pd.read_csv(train_path, error_bad_lines=False, names=headers, encoding="latin")
    # train = train.rename(columns={"Sentiment": "label", "SentimentText": "tweet"})
    text_col = config['DATASET']['TEXT_COL']
    label_col = config['DATASET']['SENTIMENT_COL']
    train = train[[text_col, label_col]]
    reduced_size = int(config['DATASET']['DATASET_SIZE'])
    train = train.sample(frac=1)
    train = train[:reduced_size]

    train = train.replace({label_col: 4}, 1)

    log.info(train.head(5))
    log.info(train.dtypes)

    model_path = os.path.join(get_resource_path(), config['MODELS']['LSTM_MODEL_LOC'])
    weights_path = os.path.join(get_resource_path(), config['MODELS']['LSTM_WEIGHTS_LOC'])
    # model_path = os.path.join(get_resource_path(), "twitter\\resources\\")

    if not model_exists:
        model_LSTM = train_model_lstm(train)
        save_model_lstm(model_LSTM, model_path, weights_path)
    else:
        model_LSTM = load_model_lstm(model_path, weights_path)

    process_user(user, model_LSTM)


def define_logger():

    logging.getLogger().setLevel(logging.NOTSET)

    # Add stdout handler, with level INFO

    # console = logging.StreamHandler(sys.stdout)
    # console.setLevel(logging.INFO)
    # formater = logging.Formatter('%(name)-13s: %(levelname)-8s %(message)s')
    # console.setFormatter(formater)
    # logging.getLogger().addHandler(console)

    # Add file rotating handler, with level DEBUG

    rotatingHandler = logging.handlers.RotatingFileHandler(filename='resources\\logs\\rotating.log', mode='w+',
                                                           maxBytes=100000, backupCount=5)
    rotatingHandler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    rotatingHandler.setFormatter(formatter)
    logging.getLogger().addHandler(rotatingHandler)





def run():
    # user1 = os.environ['USER1']
    # user2 = os.environ['USER2']
    user1, user2 = "John00053383", "Karl75202714"

    define_logger()

    log = logging.getLogger("app." + __name__)

    # log.info("Program started, Vader App:")
    #
    # vader_run(user1)
    # vader_run(user2)

    # log.info("Scikit App:")

    # scikit_learn_run(user1)
    # scikit_learn_run(user2)

    # scikit_learn_run(user1, model_exists=True)
    # scikit_learn_run(user2, model_exists=True)

    log.info("LSTM App:")

#    lstm_run(user1)

    lstm_run(user1, model_exists=True)
    lstm_run(user2, model_exists=True)
