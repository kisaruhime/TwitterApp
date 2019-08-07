from twitter.utils.postgres_utils import execute_query, insert_sentiment, insert_clsf_sentiment, insert_clean_text
from twitter.utils.scikit_learn_utils import upsampling, apply_MultinomialNB_pipeline, apply_SGDClassifier_pipeline, \
    apply_grid, get_params_for_MultinomialNB, get_params_for_SGDClassifier
from twitter.utils.text_utils import tokenization_and_stem, tweets_cleaner, tweet_clenear_for_scikit_learn
from twitter.utils.vader_utils import process_text_without_postgres
import os.path
import pandas as pd
import time


def vader_run():
    cursor = execute_query("SELECT id, original_text FROM replies_from_dm_me_your_cats_friends ")

    original_text = cursor.fetchall()
    for id, text in original_text:

        print("Original text : {0}".format(text))
        total_token_ls, total_snowballstemmer_token_ls = tokenization_and_stem(tweets_cleaner(text))

        origin_text_sentiment, origin_text_score = process_text_without_postgres(str(total_token_ls))

        insert_sentiment(origin_text_sentiment,
                         origin_text_score, id, "vader_score_origin", "vader_type_origin")

        total_token_ls_sentiment, total_token_ls_score = \
            process_text_without_postgres(str(total_token_ls))

        insert_sentiment(total_token_ls_sentiment,
                         total_token_ls_score, id, "vader_score_token", "vader_type_token")

        total_snowballstemmer_token_ls_sentiment, total_snowballstemmer_token_ls_score = \
            process_text_without_postgres(str(total_snowballstemmer_token_ls))

        insert_sentiment(total_snowballstemmer_token_ls_sentiment,
                         total_snowballstemmer_token_ls_score, id, "vader_score_stemmer", "vader_type_stemmer")


def get_resource_path():
    my_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.abspath(os.path.join(my_path, os.pardir))


def scikit_learn_run():



    train_path = os.path.join(get_resource_path(), "twitter\\resources\\train.csv")

    train = pd.read_csv(train_path)

    print("Training Set:" % train.columns, train.shape, len(train))

    test_path = os.path.join(get_resource_path(), "twitter\\resources\\test.csv")

    test = pd.read_csv(test_path)

    print("Test Set:" % test.columns, test.shape, len(test))

    train_clean = tweet_clenear_for_scikit_learn(train, "tweet")

    test_clean = tweet_clenear_for_scikit_learn(test, "tweet")

    train_upsampled = upsampling(train_clean)

    print("Upsampled tweets value count " + str(train_upsampled['label'].value_counts()))

    print("Results from MultinomialNB")

    model_MultinomialNB = apply_MultinomialNB_pipeline(train_upsampled)

    print("Result from SGDClassifier")

    model_SGDClassifier = apply_SGDClassifier_pipeline(train_upsampled)

    print("Results from applying Grid for MultinomialNB")

    start = time.time()

    params_nb = apply_grid(model_MultinomialNB, train_upsampled,
                                       get_params_for_MultinomialNB('vect', 'tfidf', 'clf'))

    end = time.time()

    print("Grid execution time for MultinomialNB is {0}".format(end - start))

    test_nb, model_MultinomialNB = apply_MultinomialNB_pipeline(train_upsampled,
                                                                            params_nb, test_clean)
#    print("Result labels from MultinomialNB after Grid upgrade")

#    print(test_nb.head(5))

    cursor = execute_query("SELECT id, original_text FROM replies_from_dm_me_your_cats_friends ")

    original_text = cursor.fetchall()
    for id, text in original_text:
        clean_text = tweets_cleaner(text)
      #  insert_clean_text(clean_text, id, 'clean_after_python_text')
        clean_text = [clean_text]
        sentiment = model_MultinomialNB.predict(clean_text)
        insert_clsf_sentiment(sentiment[0], id, 'nbclassifier_sentiment', 'nbclassifier_mark')


    start = time.time()

    params_svm = apply_grid(model_SGDClassifier, train_upsampled,
                                        get_params_for_SGDClassifier('vect', 'tfidf', 'clf_svm'))

    end = time.time()

    print("Grid execution time for SGDClassifier is {0}".format(end - start))

    test_svm, model_SGDClassifier = apply_SGDClassifier_pipeline(train_upsampled,

                                                                             params_svm, test_clean)

    cursor = execute_query("SELECT id, original_text FROM replies_from_dm_me_your_cats_friends ")

    original_text = cursor.fetchall()
    for id, text in original_text:
        clean_text = tweets_cleaner(text)
        clean_text = [clean_text]
        sentiment = model_SGDClassifier.predict(clean_text)
        insert_clsf_sentiment(sentiment[0], id, 'svmclassifier_sentiment', 'svmclassifier_mark')



def run():
    vader_run()
    scikit_learn_run()