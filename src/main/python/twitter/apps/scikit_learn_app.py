import pandas as pd
import os.path
from twitter.utils.text_utils import tweet_clenear_for_scikit_learn
import twitter.utils.scikit_learn_utils as sklearn
import time



class ScikitLearnApp:
    def __init__(self):
        pass

    def get_resource_path(self):
        my_path = os.path.abspath(os.path.dirname(__file__))
        return os.path.abspath(os.path.join(my_path, os.pardir))

    def run(self):

        train_path = os.path.join(self.get_resource_path(), "resources\\train.csv")

        train = pd.read_csv(train_path)

        print("Training Set:" % train.columns, train.shape, len(train))

        test_path = os.path.join(self.get_resource_path(), "resources\\test.csv")

        test = pd.read_csv(test_path)

        print("Test Set:" % test.columns, test.shape, len(test))

        train_clean = tweet_clenear_for_scikit_learn(train, "tweet")

        test_clean = tweet_clenear_for_scikit_learn(test, "tweet")

        train_upsampled = sklearn.upsampling(train_clean)

        print("Upsampled tweets value count " + str(train_upsampled['label'].value_counts()))

        print("Results from MultinomialNB")

        model_MultinomialNB = sklearn.apply_MultinomialNB_pipeline(train_upsampled)

        print("Result from SGDClassifier")

        model_SGDClassifier = sklearn.apply_SGDClassifier_pipeline(train_upsampled)

        print("Results from applying Grid for MultinomialNB")

        start = time.time()

        params_nb = sklearn.apply_grid(model_MultinomialNB, train_upsampled,
                                       sklearn.get_params_for_MultinomialNB('vect', 'tfidf', 'clf'))

        end = time.time()

        print("Grid execution time for MultinomialNB is {0}".format(end - start))

        test_nb, model_MultinomialNB = sklearn.apply_MultinomialNB_pipeline(train_upsampled,

                                                                                       params_nb, test_clean)
        print("Result labels from MultinomialNB after Grid upgrade")

        print(test_nb.head(5))

        start = time.time()

        params_svm = sklearn.apply_grid(model_SGDClassifier, train_upsampled,
                                        sklearn.get_params_for_SGDClassifier('vect', 'tfidf', 'clf_svm'))

        end = time.time()

        print("Grid execution time for SGDClassifier is {0}".format(end - start))

        test_svm, model_SGDClassifier = sklearn.apply_SGDClassifier_pipeline(train_upsampled,

                                                                                        params_svm, test_clean)

        print("Result labels from SGDClassifier after Grid upgrade")

        print(test_svm.head(5))



if __name__ == "__main__":
    app = ScikitLearnApp()
    app.run()


