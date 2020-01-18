from sklearn.utils import resample
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from sklearn.naive_bayes import MultinomialNB
import time
from twitter.utils.text_utils import tweet_clenear_for_scikit_learn
from sklearn.model_selection import GridSearchCV
from sklearn.externals import joblib
from twitter.utils.common_utils import get_resource_path, get_config
import os
import logging
import configparser



def train_model_scikit(train):

    log = logging.getLogger("app." + __name__)
    config = get_config()

    text_col = config['DATASET']['TEXT_COL']
    label_col = config['DATASET']['SENTIMENT_COL']
    reduced_size = int(config['DATASET']['DATASET_SIZE'])

    train = train.dropna()
    train = train[train[label_col].isin(['0', '1'])]

    train_ref = tweet_clenear_for_scikit_learn(train, text_col)

    log.info("train df after cleaning")
    log.info(train_ref.describe())
    log.info(train_ref.head(5))

    train_clean, test_clean = train_ref[:int((reduced_size/3) *2)], train_ref[int(reduced_size/3):]

    model_SVN = apply_SGDClassifier_pipeline(train_clean)

    model_MNB = apply_MNB(train_clean)

    start = time.time()
    params_svn = apply_grid(model_SVN, train_clean,
                           get_params_for_SGDClassifier('vect', 'tfidf', 'clf_svm'))
    end = time.time()
    log.info("Grid execution time for SGDClassifier is {0}".format((end - start)))
    model_SVN = apply_SGDClassifier_pipeline(train_clean, params_svn, test_clean)


    params_nb = apply_grid(model_MNB, train_clean,
                           get_params_for_MultinomialNB('vect', 'tfidf', 'clf'))
    end = time.time()
    print("Grid execution time for MultinomialNB is {0}, params are {1}"
          .format((end - start), params_nb))
    model_MNB = apply_MNB(train_clean, params_nb, test_clean)

    return model_SVN, model_MNB



def upsampling(df):

    log = logging.getLogger("app." + __name__)

    log.info("inside upsampling")
    log.info(df.count())
    train_majority = df[df.label == 0]
    train_minority = df[df.label == 1]
    log.info("train_majority")
    log.info(train_majority.count())
    log.info("train_minority")
    log.info(train_minority.count())
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

    log = logging.getLogger("app." + __name__)
    config = get_config()
    text_col = config['DATASET']['TEXT_COL']
    label_col = config['DATASET']['SENTIMENT_COL']

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

    X_train, X_test, y_train, y_test = train_test_split(df[text_col],
                                                        df[label_col],
                                                        train_size=0.75,
                                                        test_size=0.25,
                                                        random_state=101)

    model = pipeline_sgd.fit(X_train, y_train)
    y_predict = model.predict(X_test)
    f1_score_value = f1_score(y_test, y_predict)
    log.info("F1 score for SGDClassifier : {0}".format(f1_score_value))

    if test is not None:
        test_new = test.copy()
        test_new[label_col] = model.predict(test[text_col])
        f1_score_value = f1_score(test[label_col], test_new[label_col])
        log.info("F1 score for SGDClassifier on test data: {0}".format(f1_score_value))
    return model


def apply_MNB(df, params=None, test=None):

    log = logging.getLogger("app." + __name__)

    config = get_config()
    text_col = config['DATASET']['TEXT_COL']
    label_col = config['DATASET']['SENTIMENT_COL']

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

    X_train, X_test, y_train, y_test = train_test_split(df[text_col],
                                                        df[label_col],
                                                        random_state=13)
    model = pipeline_nb.fit(X_train, y_train)
    y_predict = model.predict(X_test)
    f1_score_value = f1_score(y_test, y_predict)
    log.info("F1 score for MultinomialNB : {0}".format(f1_score_value))
    if test is not None:
        test_new = test.copy()
        test_new[label_col] = model.predict(test[text_col])
        f1_score_value = f1_score(test[label_col], test_new[label_col])
        log.info("F1 score for SGDClassifier on test data: {0}".format(f1_score_value))
    return model


def apply_grid(model, df, params_dict):

    log = logging.getLogger("app." + __name__)
    config = get_config()
    text_col = config['DATASET']['TEXT_COL']
    label_col = config['DATASET']['SENTIMENT_COL']

    X_train, X_test, y_train, y_test = train_test_split(df[text_col], df[label_col], random_state=13)
    gs_clf_svm = GridSearchCV(model, params_dict)
    gs_clf_svm = gs_clf_svm.fit(X_train, y_train)

    log.info("Grid search best params: {}".format(gs_clf_svm.best_params_))
    log.info("Grid search best estimator: {}".format(gs_clf_svm.best_estimator_))
    log.info("Grid search best index: {}".format(gs_clf_svm.best_index_))
    log.info("Grid search best score: {}".format(gs_clf_svm.best_score_))

    return gs_clf_svm.best_params_


def get_params_for_SGDClassifier(vect_name, transf_name, class_name):
    return {vect_name+'__ngram_range': [(1, 1), (1, 2)],
            transf_name+'__use_idf': (True, False),
            class_name+'__alpha': (1e-2, 1e-3),
            class_name+'__loss': ['hinge', 'log', 'perceptron'],
            class_name+'__n_iter_no_change': (4, 5, 6), }


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


def save_model_scikit(model, filename):
    joblib.dump(model, filename)


def read_model_scikit(filename):
    model = joblib.load(filename)
    return model