# Spam Text Message Predictor

# Initialize Library and Setup
from spam_text_module import utils
import tensorflow as tf
import pickle
import config


def predict_spam(rawtext, thres):
    # Step 1: Extract Features
    tokens, sents = utils.text_preprocess(rawtext)

    mfd = utils.extract_mfd(rawtext, tokens)
    cv, tfidf, idx = utils.extract_bow(sents)

    # Step 2: Load models
    # Naive Bayes - CountVectorizer
    file = open(config.nb_cv_model, 'rb')
    nb_cv = pickle.load(file)
    file.close()

    # SVM - TfIdf Vectorizer
    file = open(config.svm_tfidf_model, 'rb')
    svm_tfidf = pickle.load(file)
    file.close()

    # Knn - Manually Designed Features
    file = open(config.knn_mfd_model, 'rb')
    knn_mfd = pickle.load(file)
    file.close()

    # Self-Trained Word Embeddings CNN Model (30 word of vectors of 50 dimension)
    file = config.spam_CNN_model
    selftrained_cnn = tf.keras.models.load_model(file)

    # Step 3: Predict
    nb_pred = (nb_cv.predict_proba([cv])[0][1] > thres) * 1
    svm_pred = (svm_tfidf.predict_proba([tfidf])[0][1] > thres) * 1
    knn_pred = (knn_mfd.predict_proba([mfd])[0][1] > thres) * 1
    cnn30x50_pred = (selftrained_cnn.predict([idx])[0][0] > thres) * 1

    # Step 4: Ensemble Model Results (Majority Vote)
    pred = ((nb_pred + svm_pred + knn_pred + cnn30x50_pred) / 4) >= 0.5

    # return pred
    return pred
