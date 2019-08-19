from sklearn.feature_extraction.text import CountVectorizer
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Dense, Embedding, LSTM
from sklearn.model_selection import train_test_split
from keras.utils.np_utils import to_categorical
import numpy as np
import pandas as pd


def train_model(df):

    max_fatures = 30000
    tokenizer = Tokenizer(nb_words=max_fatures, split=' ')
    df.dropna(inplace=True)
    df.tweet = df.tweet.astype(str)
    df.label = df.label.astype(int)

    df = df[df['label'] != 2]
    df['label'] = np.where(df['label'] > 3, 1, 0)

    tokenizer.fit_on_texts(df['tweet'].values)
    X1 = tokenizer.texts_to_sequences(df['tweet'].values)
    X1 = pad_sequences(X1)
    Y1 = pd.get_dummies(df['label']).values
    X1_train, X1_test, Y1_train, Y1_test = train_test_split(X1, Y1, random_state=42)
    print(X1_train.shape, Y1_train.shape)
    print(X1_test.shape, Y1_test.shape)

    embed_dim = 150
    lstm_out = 200

    model = Sequential()
    model.add(Embedding(max_fatures, embed_dim, input_length=X1.shape[1], dropout=0.2))
    model.add(LSTM(lstm_out, dropout_U=0.2, dropout_W=0.2))
    model.add(Dense(2, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    print(model.summary())

    batch_size = 32
    model.fit(X1_train, Y1_train, nb_epoch=10, batch_size=batch_size, verbose=2)

    score, acc = model.evaluate(X1_test, Y1_test, verbose=2, batch_size = batch_size)
    print("score: %.2f" % (score))
    print("acc: %.2f" % (acc))

    pos_cnt, neg_cnt, pos_correct, neg_correct = 0, 0, 0, 0
    for x in range(len(X1_test)):

        result = model.predict(X1_test[x].reshape(1, X1_test.shape[1]), batch_size=1, verbose=2)[0]

        if np.argmax(result) == np.argmax(Y1_test[x]):
            if np.argmax(Y1_test[x]) == 0:
                neg_correct += 1
            else:
                pos_correct += 1

        if np.argmax(Y1_test[x]) == 0:
            neg_cnt += 1
        else:
            pos_cnt += 1

    print("pos_acc", pos_correct/pos_cnt*100, "%")
    print("neg_acc", neg_correct/neg_cnt*100, "%")
