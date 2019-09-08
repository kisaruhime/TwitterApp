from twitter.utils.lstm_utils import train_model, save_model,load_model
import os
import pandas as pd
from twitter.utils.postgres_utils import get_ids_text, insert_clsf_sentiment
from twitter.utils.text_utils import tweets_cleaner

class LSTMApp:
    def __init__(self):
        pass

    def get_resource_path(self):
        my_path = os.path.abspath(os.path.dirname(__file__))
        return os.path.abspath(os.path.join(my_path, os.pardir))

    def run(self):
        train_path = os.path.join(self.get_resource_path(), "resources\\training.csv")
        cols = ["sentiment", "ids", "date", "flag", "user", "text"]
        train = pd.read_csv(train_path, encoding='latin1', names=cols)
        # Keeping only the neccessary columns
        train = train[['text', 'sentiment']]
        # header = ["label", "ids", "date", "flag", "user", "tweet"]
        # train = pd.read_csv(train_path, encoding='latin-1', error_bad_lines=False, names=header)
        print(train.head())
        print(train.dtypes)

        model_path = os.path.join(self.get_resource_path(), "resources\\")
        model = load_model(model_path)
        #save_model(model, model_path)

        cursor = get_ids_text()

        original_text = cursor.fetchall()
        for id, text in original_text:
            clean_text = tweets_cleaner(text)
            clean_text = [clean_text]
            sentiment = model.predict(clean_text)
            print(clean_text)
            print(sentiment)



if __name__ == "__main__":
    app = LSTMApp()
    app.run()