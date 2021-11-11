# A helper functions which takes raw text as input and return preprocessed tokens of text:
# Initiate Library Setup

import numpy as np
import pandas as pd
import re
import fnmatch
import pickle

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

from tensorflow.keras.preprocessing.sequence import pad_sequences

import config


# 0) Text Preprocessing
# Takes a raw text as input and return pre-processed text in list of tokens and combined tokens in one sentence.
def text_preprocess(rawtext):
    # Initialization
    stopwordsdic = stopwords.words('english')  # stopwords dictionary
    customstopwords = ['u', 'ur']
    lemmatizer = WordNetLemmatizer()

    # Text Preprocess
    ptext = rawtext.lower()  # Lower Casing
    ptext = ptext.strip()  # Strip off excess spacing in the end of message
    ptext = re.sub(r'\d+', '', ptext)  # Remove all number
    ptext = re.sub('[^A-Za-z0-9]+', ' ', ptext)  # Remove punctuations
    ptext = word_tokenize(ptext)  # Tokenization
    ptext = [word for word in ptext if word not in stopwordsdic]  # Remove stopwords
    ptext = [word for word in ptext if word not in customstopwords]  # Remove custom stopwords
    tokens = [lemmatizer.lemmatize(word) for word in ptext]  # Lemmatization
    sents = ' '.join(tokens)
    return tokens, sents  # list of tokens, combined tokens in a text sentence


# 1) Manually Designed Features
# Takes raw text as input and return the extracted manually designed features.
def extract_mfd(rawtext, tokens):
    # Initialize
    math_symbol = 0
    special_symbol = 0
    uppercase_word = 0
    phone_num = 0
    spam_word = 0
    math_symbol_list = ["+", "-", "/", "^", "<", ">"]
    special_symbol_list = ["!", "@", "$", "~", "#", "&", "*"]
    phone_format_list = ["*xxxxx*", "*xxxx-xxxx*", "*xxxxxxxx*", "*+xx-xxxx-xxxx*"]

    # Count Math Symbols (Apply on raw text)
    for symbol in math_symbol_list:
        math_symbol += rawtext.count(symbol)

    # Count Special Symbols (Apply on raw text)
    for symbol in special_symbol_list:
        special_symbol += rawtext.count(symbol)

    # Count Number of Upper-case Word (Apply on raw text)
    utext = rawtext.strip()
    utext = re.sub(r'\d+', '', utext)
    utext = re.sub('[^A-Za-z0-9]+', ' ', utext)
    utext = word_tokenize(utext)
    for word in utext:
        uppercase_word += word.isupper()

    # Indicator if phone number exists in text (Apply on raw text)
    utext = re.sub(r'\d', 'x', rawtext)
    for num in phone_format_list:
        if fnmatch.fnmatch(utext, num):
            phone_num = 1
            break

    # Count Number of Occurrence of 20 Common Spam Words (Apply on preprocessed list of tokens)
    top20_spam_words = np.loadtxt(config.spam_words, dtype=str)
    for word in tokens:
        spam_word += word in top20_spam_words

    # Count Number of Words (Apply on preprocessed list of tokens)
    num_word = len(tokens)

    # Feature Map
    feature_map = np.array([math_symbol, special_symbol, uppercase_word, phone_num, spam_word, num_word])

    # Normalization
    minmax_scaler = pd.read_csv(config.scaler, index_col=0)
    min_scale = minmax_scaler['Min']
    max_scale = minmax_scaler['Max']
    mfd_feature = np.array((feature_map - min_scale)/(max_scale - min_scale))

    return mfd_feature


# 2) Bag-of-Words(BoW) CountVectorizer, TfIdfVectorizer and Word Sequencing Index
def extract_bow(sentence):
    # Load Trained Tokenizer
    file = open(config.tokenizer, 'rb')
    tk = pickle.load(file)
    file.close()

    # CountVectorizer
    cv_feature = tk.texts_to_matrix([sentence], mode='count').ravel()

    # TfIdfVectorizer
    tfidf_feature = tk.texts_to_matrix([sentence], mode='tfidf').ravel()

    # Word Sequencing Index (With padding)
    text_length = 30
    padding_mode = 'post'
    idx_feature = tk.texts_to_sequences([sentence])
    idx_feature = pad_sequences(idx_feature, maxlen=text_length, padding=padding_mode).ravel()
    idx_feature = idx_feature.reshape(-1, text_length)

    return cv_feature, tfidf_feature, idx_feature
