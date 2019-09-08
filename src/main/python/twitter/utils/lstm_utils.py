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


def train_model(df, max_features=5000, embed_dim=150, lstm_out=200, test_size=0.40, nb_epoch=1, batch_size=40):

    train = transform_data(df)

    tokenizer = Tokenizer(nb_words=max_features, split=' ')

    print("Positive sentiments count {0}".format(train[train['sentiment'] == 'Positive'].count()))
    print("Negative sentiments count {0}".format(train[train['sentiment'] == 'Negative'].count()))

    X, X_train, X_validation, X_test, Y_train, Y_validation, Y_test = get_splitted_data(train, tokenizer, test_size)

    model = get_LSTM_model(max_features, embed_dim, X, lstm_out)

    model.fit(X_train, Y_train, nb_epoch=nb_epoch, batch_size=batch_size, verbose=1)

    score, acc = model.evaluate(X_test, Y_test, verbose=2, batch_size=batch_size)

    print("score: %.2f" % (score))
    print("acc: %.2f" % (acc))

    validate_result(X_validation, Y_validation, model, X_test)

    return model



def transform_data(df):

    df = df.sample(frac=0.8, random_state=200)
    df = df[:400000]
    df.sentiment = df.sentiment.replace(4, 1)
    df.sentiment = df.sentiment.replace(1, "Positive")
    df.sentiment = df.sentiment.replace(0, "Negative")

    df['text'] = df['text'].apply(lambda x: x.lower())
    df['text'] = df['text'].apply((lambda x: re.sub('[^a-zA-z0-9\s]', '', x)))

    for idx, row in df.iterrows():
        row[0] = row[0].replace('rt', ' ')
    return df


def get_splitted_data(df, tokenizer, test_size):


    tokenizer.fit_on_texts(df['text'].values)
    X = tokenizer.texts_to_sequences(df['text'].values)
    X = pad_sequences(X)
    Y = pd.get_dummies(df['sentiment']).values

    print("X shape {0}".format(X.shape))

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=test_size, random_state=17)

    X_validation, X_test_true, Y_validation, Y_test_true = \
        train_test_split(X_test, Y_test, test_size=test_size, random_state=19)

    print("X train shape {0}, Y train shape {1}".format(X_train.shape, Y_train.shape))
    print("X test shape {0}, Y test shape {1}".format(X_test.shape, Y_test.shape))

    print("X train true shape {0}, Y train true shape {1}".format(X_test_true.shape, Y_test_true.shape))
    print("X validation shape {0}, Y validation shape {1}".format(X_validation.shape, Y_validation.shape))

    return X, X_train, X_validation, X_test_true, Y_train, Y_validation, Y_test_true


def get_LSTM_model(max_features, embed_dim, X, lstm_out):

    model = Sequential()
    model.add(Embedding(max_features, embed_dim, input_length=X.shape[1], dropout=0.2))
    model.add(LSTM(lstm_out, dropout_U=0.2, dropout_W=0.2))
    model.add(Dense(2, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    print(model.summary())
    return model

def validate_result(X_validate, Y_validate, model, X_test):

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

    print("pos_acc", pos_correct/pos_cnt*100, "%")
    print("neg_acc", neg_correct/neg_cnt*100, "%")


def save_model(model, path):
    model_json = model.to_json()
    file_model_name = path+"model_lstm.json"
    file_wright_name = path+"wights_lstm.h5"
    with open(file_model_name, "w") as json_file:
        json_file.write(model_json)
    # serialize weights to HDF5
    model.save_weights(file_wright_name)
    print("Saved model to disk")

def load_model(path):
    # load json and create model
    file_model_name = path+"model_lstm.json"
    file_wright_name = path+"wights_lstm.h5"
    json_file = open(file_model_name, 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights(file_wright_name)
    print("Loaded model from disk")
    return loaded_model
