from twitter.utils.lstm_utils import train_model
import os
import pandas as pd

class LSTMApp:
    def __init__(self):
        pass

    def get_resource_path(self):
        my_path = os.path.abspath(os.path.dirname(__file__))
        return os.path.abspath(os.path.join(my_path, os.pardir))

    def run(self):
        train_path = os.path.join(self.get_resource_path(), "resources\\training.csv")
        header = ["label", "ids", "date", "flag", "user", "tweet"]
        train = pd.read_csv(train_path, encoding='latin-1', error_bad_lines=False, names=header)
        print(train.head())
        print(train.dtypes)
        train_model(train)


if __name__ == "__main__":
    app = LSTMApp()
    app.run()