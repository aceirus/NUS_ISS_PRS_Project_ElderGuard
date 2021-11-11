"""
Malicious URL Prediction
"""
import joblib
from malurl_module.mal_url_feature import *
from config import *

def mal_predict_url(url_list):
    predMal_result = {}
    thres = 0.55
    #bad=0, good=1
    for pred_url in url_list:
        if str(pred_url).lower().startswith(tuple(['https', 'http'])):
            pred_url = pred_url.replace("https://", "", 1)
            pred_url = pred_url.replace("http://", "", 1)

        # 1. Extract Features
        manualFeature = manual_feature_extraction(pred_url)

        # 2. Load Models
        #dt_mal_model = 'malurl_module/models/DecisionTreeClassifier.jlib'
        dt_mal = joblib.load(dt_mal_model)
        #adb_mal_model = 'malurl_module/models/AdaBoostClassifier.jlib'
        adb_mal = joblib.load(adb_mal_model)
        #rf_mal_model = 'malurl_module/models/RandomForestClassifier.jlib'
        rf_mal = joblib.load(rf_mal_model)

        # 3. Predict
        # print("\n", pred_url)
        # print(dt_mal.predict_proba(manualFeature), knn_mal.predict_proba(manualFeature))

        # Probability of malicious url
        dt_mal_pred = dt_mal.predict_proba(manualFeature)[0][1]
        adb_mal_pred = adb_mal.predict_proba(manualFeature)[0][1]
        rf_mal_pred = rf_mal.predict_proba(manualFeature)[0][0]

        # Ensemble Model Averaging
        pred = ((dt_mal_pred + rf_mal_pred + adb_mal_pred)/3) >= thres

        #If pred True then is badURL
        predMal = "Bad" if pred else "Good"

        predMal_result[pred_url] = predMal

    return predMal_result