from nltk.stem.snowball import SnowballStemmer
import re
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')


snowballstemmer = SnowballStemmer("english")
stopwords = stopwords.words('english')

def tweets_cleaner(tweet):
    semiclean_text = tweet
    semiclean_text = re.sub(r'@[A-Za-z0-9_]+','',semiclean_text)
    semiclean_text = re.sub(r"http\S+", "", semiclean_text)
    semiclean_text = re.sub(r"[0-9]*", "", semiclean_text)
    semiclean_text = re.sub(r"(”|“|-|\+|`|#|,|;|\|)*", "", semiclean_text)
    semiclean_text = re.sub(r"&amp", "", semiclean_text)
    semiclean_text = semiclean_text.lower()
    return semiclean_text


def tokenization_and_stem(sentence):

    total_token_ls = []
    total_snowballstemmer_token_ls = []
    token_ls = []
    snowballstemmer_token_ls = []
    tokens = nltk.word_tokenize(sentence)
    for token in tokens:
        if token not in stopwords:
            #token_ls.append(token)
            snowballstemmer_token_ls.append(snowballstemmer.stem(token))
    #total_token_ls.append(token_ls)
    total_snowballstemmer_token_ls.append(snowballstemmer_token_ls)
    return back_to_clean_sent(total_snowballstemmer_token_ls)
    #return back_to_clean_sent(total_token_ls), back_to_clean_sent(total_snowballstemmer_token_ls)



def back_to_clean_sent(token_ls):
    """
    In order to perform sentiment analysis,
    here we put the words back into sentences.
    """
    clean_sent_ls = []
    for word_ls in token_ls:
        clean_sent = ""
        for word in word_ls:
            clean_sent += (word + " ")
        clean_sent_ls.append(clean_sent)
    return clean_sent_ls


def tweet_clenear_for_scikit_learn(df, col):

    df_clean = df.copy()
    df_clean[col] = df_clean[col].str.lower()
    df_clean[col] = df_clean[col].apply(lambda elem: tweets_cleaner(elem))
    df_clean[col] = df_clean[col].apply(lambda elem: tokenization_and_stem(elem)[0])
    # df_clean[col] = df_clean[col].apply(lambda elem: re.sub(r"(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|^rt|http.+?",
    #                                             "", elem))

    return df_clean
