from sklearn.utils import resample
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from sklearn.naive_bayes import MultinomialNB
import numpy as np
from sklearn.model_selection import GridSearchCV




def upsampling(df):
    train_majority = df[df.label == 0]
    train_minority = df[df.label == 1]
    train_minority_upsampled = resample(train_minority,
                                        replace=True,
                                        n_samples=len(train_majority),
                                        random_state=123)
    return pd.concat([train_minority_upsampled, train_majority])

def downsampling(df):
    train_majority = df[df.label == 0]
    train_minority = df[df.label == 1]
    train_majority_downsampled = resample(train_majority,
                                          replace=True,
                                          n_samples=len(train_minority),
                                          random_state=123)
    return pd.concat([train_majority_downsampled, train_minority])


def apply_SGDClassifier_pipeline(df, params=None, test=None):

    vect_name = 'vect'
    transf_name = 'tfidf'
    class_name = 'clf_svm'

    if params:
        pipeline_sgd = Pipeline([
            (vect_name, CountVectorizer(**process_grid_params(params, vect_name))),
            (transf_name,  TfidfTransformer(**process_grid_params(params, transf_name))),
            (class_name, SGDClassifier(**process_grid_params(params, class_name))),
        ])
    else:
        pipeline_sgd = Pipeline([
            (vect_name, CountVectorizer()),
            (transf_name,  TfidfTransformer()),
            (class_name, SGDClassifier()),
        ])

    X_train, X_test, y_train, y_test = train_test_split(df['tweet'],
                                                        df['label'],
                                                        random_state=13)
    model = pipeline_sgd.fit(X_train, y_train)
    y_predict = model.predict(X_test)

    f1_score_value = f1_score(y_test, y_predict)
    print("F1 score for SGDClassifier : {0}".format(f1_score_value))
    if test is not None:
        test_new = test.copy()
        test_new['label'] = model.predict(test['tweet'])
        return test_new, model
    return model


def apply_MultinomialNB_pipeline(df, params=None, test=None):

    vect_name = 'vect'
    transf_name = 'tfidf'
    class_name = 'clf'
    if params:
        pipeline_nb = Pipeline([
            (vect_name, CountVectorizer(**process_grid_params(params, vect_name))),
            (transf_name,  TfidfTransformer(**process_grid_params(params, transf_name))),
            (class_name, MultinomialNB(**process_grid_params(params, class_name))),
    ])
    else:
        pipeline_nb = Pipeline([
            (vect_name, CountVectorizer()),
            (transf_name,  TfidfTransformer()),
            (class_name, MultinomialNB()),
    ])

    X_train, X_test, y_train, y_test = train_test_split(df['tweet'],
                                                        df['label'],
                                                        random_state=13)
    model = pipeline_nb.fit(X_train, y_train)
    y_predict = model.predict(X_test)
    f1_score_value = f1_score(y_test, y_predict)
    print("F1 score for MultinomialNB : {0}".format(f1_score_value))
    if test is not None:
        test_new = test.copy()
        test_new['label'] = model.predict(test['tweet'])
        return test_new, model
    return model


def apply_grid(model, df, params_dict):
    X_train, X_test, y_train, y_test = train_test_split(df['tweet'], df['label'], random_state=13)
    gs_clf_svm = GridSearchCV(model, params_dict)
    gs_clf_svm = gs_clf_svm.fit(X_train, y_train)
    print(gs_clf_svm.best_score_)
    return gs_clf_svm.best_params_


def get_params_for_SGDClassifier(vect_name, transf_name, class_name):
    return {vect_name+'__ngram_range': [(1, 1), (1, 2)],
            transf_name+'__use_idf': (True, False),
            class_name+'__alpha': (1e-2, 1e-3),
            class_name+'__loss': ['hinge', 'log', 'perceptron'],
            class_name+'__n_iter_no_change': (3, 4, 5, 6, 7), }


def get_params_for_MultinomialNB(vect_name, transf_name, class_name):
    return {vect_name+'__ngram_range': [(1, 1), (1, 2)],
            transf_name+'__use_idf': (True, False),
            class_name+'__alpha': (1e-2, 1e-3), }


def process_grid_params(params, entity_name):
    processed_params = {}
    for key, value in params.items():
        if key.startswith(entity_name):
            processed_params[key[(len(entity_name)+2):]] = value

    return processed_params

