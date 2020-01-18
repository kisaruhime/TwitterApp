import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Dense, Embedding, LSTM
from sklearn.model_selection import train_test_split
from keras.utils.np_utils import to_categorical
from keras.models import model_from_json
import re

from twitter.utils.common_utils import get_config
from twitter.utils.text_utils import tweet_clenear_for_lstm_learn
import logging


def train_model_lstm(df, max_features=5000, embed_dim=150, lstm_out=200, test_size=0.40, nb_epoch=3, batch_size=40):

    log = logging.getLogger("app." + __name__)
    config = get_config()

    text_col = config['DATASET']['TEXT_COL']
    label_col = config['DATASET']['SENTIMENT_COL']

    train = tweet_clenear_for_lstm_learn(df, text_col)

    #train = transform_data(df)

    tokenizer = Tokenizer(nb_words=max_features, split=' ')

    log.info("Positive sentiments count {0}".format(train[train[label_col] == 1].count()))
    log.info("Negative sentiments count {0}".format(train[train[label_col] == 0].count()))

    # print("Positive sentiments count {0}".format(train[train['Sentiment'] == 'Positive'].count()))
    # print("Negative sentiments count {0}".format(train[train['Sentiment'] == 'Negative'].count()))

    X, X_train, X_validation, X_test, Y_train, Y_validation, Y_test = get_splitted_data(train, tokenizer, test_size)

    model = get_LSTM_model(max_features, embed_dim, X, lstm_out)

    model.fit(X_train, Y_train, nb_epoch=nb_epoch, batch_size=batch_size, verbose=1)

    score, acc = model.evaluate(X_test, Y_test, verbose=2, batch_size=batch_size)

    log.info("score: %.2f" % (score))
    log.info("acc: %.2f" % (acc))

    validate_result(X_validation, Y_validation, model, X_test)

    return model



def transform_data(df):

    df = df.sample(frac=0.8, random_state=200)
    #df = df[:400000]
    df.label = df.label.replace(4, 1)
    df.label = df.label.replace(1, "Positive")
    df.label = df.label.replace(0, "Negative")

    df['tweet'] = df['tweet'].apply(lambda x: x.lower())
    df['tweet'] = df['tweet'].apply((lambda x: re.sub('[^a-zA-z0-9\s]', '', x)))

    for idx, row in df.iterrows():
        row[0] = row[0].replace('rt', ' ')
    return df


def get_splitted_data(df, tokenizer, test_size):

    log = logging.getLogger("app." + __name__)

    config = get_config()

    text_col = config['DATASET']['TEXT_COL']
    label_col = config['DATASET']['SENTIMENT_COL']

    tokenizer.fit_on_texts(df[text_col].values)
    X = tokenizer.texts_to_sequences(df[text_col].values)
    X = pad_sequences(X)
    Y = pd.get_dummies(df[label_col]).values

    log.info("X shape {0}".format(X.shape))
    log.info("X first element: {}".format(X[0]))

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=test_size, random_state=17)

    X_validation, X_test_true, Y_validation, Y_test_true = \
        train_test_split(X_test, Y_test, test_size=test_size, random_state=19)

    log.info("X train shape {0}, Y train shape {1}".format(X_train.shape, Y_train.shape))
    log.info("X test shape {0}, Y test shape {1}".format(X_test.shape, Y_test.shape))

    log.info("X train true shape {0}, Y train true shape {1}".format(X_test_true.shape, Y_test_true.shape))
    log.info("X validation shape {0}, Y validation shape {1}".format(X_validation.shape, Y_validation.shape))

    return X, X_train, X_validation, X_test_true, Y_train, Y_validation, Y_test_true


def get_LSTM_model(max_features, embed_dim, X, lstm_out):

    log = logging.getLogger("app." + __name__)

    model = Sequential()
    model.add(Embedding(max_features, embed_dim, input_length=X.shape[1], dropout=0.2))
    model.add(LSTM(lstm_out, dropout_U=0.2, dropout_W=0.2))
    model.add(Dense(2, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    log.info(model.summary())
    return model

def validate_result(X_validate, Y_validate, model, X_test):

    log = logging.getLogger("app." + __name__)

    pos_cnt, neg_cnt, pos_correct, neg_correct = 0, 0, 0, 0
    for x in range(len(X_validate)):

        result = model.predict(X_validate[x].reshape(1, X_test.shape[1]), batch_size=1, verbose=2)[0]

        if np.argmax(result) == np.argmax(Y_validate[x]):
            if np.argmax(Y_validate[x]) == 0:
                neg_correct += 1
            else:
                pos_correct += 1

        if np.argmax(Y_validate[x]) == 0:
            neg_cnt += 1
        else:
            pos_cnt += 1

    log.info("pos_acc", pos_correct/pos_cnt*100, "%")
    log.info("neg_acc", neg_correct/neg_cnt*100, "%")


def save_model_lstm(model, model_path, weights_path):

    log = logging.getLogger("app." + __name__)

    model_json = model.to_json()
    # file_model_name = model_path
    # file_wright_name = weights_path
    # file_model_name = path+"model_lstm.json"
    # file_wright_name = path+"wights_lstm.h5"
    with open(model_path, "w") as json_file:
        json_file.write(model_json)
    # serialize weights to HDF5
    model.save_weights(weights_path)
    log.info("Saved model lstm on disk")

def load_model_lstm(model_path, weights_path):

    log = logging.getLogger("app." + __name__)

    # file_model_name = model_path
    # file_wright_name = weights_path
    # file_model_name = path+"model_lstm.json"
    # file_wright_name = path+"wights_lstm.h5"
    json_file = open(model_path, 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights(weights_path)
    log.info("Loaded model lstm from disk")
    return loaded_model
