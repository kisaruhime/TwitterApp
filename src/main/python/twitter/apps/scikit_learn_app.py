import pandas as pd
import os.path
from twitter.utils.scikit_learn_utils import train_model
from twitter.utils.postgres_utils import get_ids_text, insert_clsf_sentiment
from twitter.utils.text_utils import tweets_cleaner


class ScikitLearnApp:
    def __init__(self):
        pass

    def get_resource_path(self):
        my_path = os.path.abspath(os.path.dirname(__file__))
        return os.path.abspath(os.path.join(my_path, os.pardir))

    def run(self):

        train_path = os.path.join(self.get_resource_path(), "resources\\train.csv")
        train = pd.read_csv(train_path)
        test_path = os.path.join(self.get_resource_path(), "resources\\test.csv")
        test = pd.read_csv(test_path)

        model_MNB = train_model(train, test)

        cursor = get_ids_text()

        original_text = cursor.fetchall()
        for id, text in original_text:
            clean_text = tweets_cleaner(text)
            clean_text = [clean_text]
            sentiment = model_MNB.predict(clean_text)
            insert_clsf_sentiment(sentiment[0], id, 'svmclassifier_sentiment', 'svmclassifier_mark')

        # start = time.time()
        #
        # params_svm = sklearn.apply_grid(model_SGDClassifier, train_upsampled,
        #                                  sklearn.get_params_for_SGDClassifier('vect', 'tfidf', 'clf_svm'))
        #
        # end = time.time()
        #
        # print("Grid execution time for SGDClassifier is {0}".format(end - start))
        #
        # test_svm, model_SGDClassifier = sklearn.apply_SGDClassifier_pipeline(train_upsampled,
        #
        #                                                                                 params_svm, test_clean)


if __name__ == "__main__":
    app = ScikitLearnApp()
    app.run()


