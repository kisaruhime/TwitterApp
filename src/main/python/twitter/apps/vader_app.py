from twitter.utils.postgres_utils import get_ids_text, insert_sentiment, insert_clean_text
from twitter.utils.text_utils import tokenization_and_stem, tweets_cleaner
from twitter.utils.vader_utils import prcss_text


class VaderApp:

    def __init__(self):
        pass

    def run(self):

        cursor = get_ids_text()

        original_text = cursor.fetchall()
        for id, text in original_text:

            print("Original text : {0}".format(text))

            ttl_sbstmr_token_ls = tokenization_and_stem(tweets_cleaner(text))

            #insert_clean_text(ttl_sbstmr_token_ls[0], id)

            org_text_snt, org_text_score = prcss_text(str(ttl_sbstmr_token_ls))

            insert_sentiment(org_text_snt,
                             org_text_score, id, "vader_score_origin", "vader_type_origin")

            # ttl_token_ls_snt, ttl_token_ls_score = \
            #     prcss_text(str(ttl_token_ls))
            #
            # insert_sentiment(ttl_token_ls_snt,
            #                  ttl_token_ls_score, id, "vader_score_token", "vader_type_token")

            ttl_sbstmr_token_ls_snt, total_sbstmr_token_ls_score = \
                prcss_text(str(ttl_sbstmr_token_ls))

            insert_sentiment(ttl_sbstmr_token_ls_snt,
                             total_sbstmr_token_ls_score, id, "vader_score_stemmer", "vader_type_stemmer")


if __name__ == "__main__":
    app = VaderApp()
    app.run()