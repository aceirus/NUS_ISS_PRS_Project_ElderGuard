"""
URL Prediction
"""

import pickle
from phishing_module.url_feature import *
from config import *


def predict_url(url_list):
    pred_result = {}
    thres = 0.65
    ##bad=0, good=1
    for pred_url in url_list:
        if str(pred_url).lower().startswith(tuple(['https', 'http'])):
            pred_url = pred_url.replace("https://", "", 1)
            pred_url = pred_url.replace("http://", "", 1)

        # 1. Extract Features
        # manualFeature = manual_feature_extraction(pred_url)
        cvFeature, tfidfFeature = nltk_feature_extraction(pred_url)

        # 2. Load Models
        nb_cv = pickle.load(open(nbCV, 'rb'))
        nb_tf = pickle.load(open(nbTF, 'rb'))
        adaboost_cv = pickle.load(open(adaBoostCV, 'rb'))
        adaboost_tfidf = pickle.load(open(adaBoostTF, 'rb'))
        logreg_cv = pickle.load(open(logRegCV, 'rb'))

        # # 3. Predict
        # Probability of predict 0, ie bad url
        nb_cvpred = nb_cv.predict_proba(cvFeature)[0][0]
        nb_tfpred = nb_tf.predict_proba(tfidfFeature)[0][0]
        adaboost_cvpred = adaboost_cv.predict_proba(cvFeature)[0][0]
        adaboost_tfidfpred = adaboost_tfidf.predict_proba(tfidfFeature)[0][0]
        logreg_cvpred = logreg_cv.predict_proba(cvFeature)[0][0]

        # Combine the probability of bad url (Weighted)
        predThreshold = ((nb_cvpred * 0.2) + (nb_tfpred * 0.2) +
                         (adaboost_cvpred * 0.2) +(adaboost_tfidfpred * 0.2) +
                         (logreg_cvpred * 0.2))
        pred = predThreshold >= thres

        # If pred True then is badURL
        predM = "Bad" if pred else "Good"
        pred_result[pred_url] = predM

        print("\n", pred_url)
        print(nb_cv.predict(cvFeature), nb_tf.predict(tfidfFeature),
              adaboost_cv.predict(cvFeature), adaboost_tfidf.predict(tfidfFeature),
              logreg_cv.predict(cvFeature))
        print(nb_cv.predict_proba(cvFeature), nb_tf.predict_proba(tfidfFeature),
              adaboost_cv.predict_proba(cvFeature), adaboost_tfidf.predict_proba(tfidfFeature),
              logreg_cv.predict_proba(cvFeature))
        print("Pred Threshold: ", predThreshold, predM)

    return pred_result
