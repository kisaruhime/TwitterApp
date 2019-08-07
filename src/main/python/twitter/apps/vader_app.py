from twitter.utils.postgres_utils import execute_query, insert_sentiment
from twitter.utils.text_utils import tokenization_and_stem, tweets_cleaner
from twitter.utils.vader_utils import process_text_without_postgres


class VaderApp:

    def __init__(self):
        pass

    def run(self):

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

if __name__ == "__main__":
    app = VaderApp()
    app.run()