# CONFIGURATION FOR PHISHING URL MODULE
# MODELS FILEPATH
logRegCV = 'phishing_module/models/logreg_cv.pkl'
adaBoostCV = 'phishing_module/models/ad_cv_86_94.pkl'
adaBoostTF = 'phishing_module/models/ad_tfidf_85_93.pkl'
nbCV = 'phishing_module/models/nb_cv.pkl'
nbTF = 'phishing_module/models/nb_tf.pkl'

scalerPkl = 'phishing_module/models/scaler.pkl'
tfidfPkl = 'phishing_module/models/tfidf_v.pkl'
cvPkl = 'phishing_module/models/cv.pkl'


# CONFIGURATION FOR MALICIOUS URL MODULE
# MODELS FILEPATH
dt_mal_model = 'malurl_module/models/DecisionTreeClassifier.jlib'
adb_mal_model = 'malurl_module/models/AdaBoostClassifier.jlib'
rf_mal_model = 'malurl_module/models/RandomForestClassifier.jlib'
scaler_filename = 'malurl_module/models/Scaler23.jlib'


# CONFIGURATION FOR SPAM TEXT MODULE
# MODELS FILEPATH
nb_cv_model = 'spam_text_module/models/NB_CV.pickle'
knn_mfd_model = 'spam_text_module/models/knn_mfd.pickle'
svm_tfidf_model = 'spam_text_module/models/SVM_tfidf.pickle'
spam_CNN_model = 'spam_text_module/models/Spam_Clsfr_CNN.hdf5'

# PARAMETERS FILEPATH
tokenizer = 'spam_text_module/parameters/bowtokenizer.pickle'
embglove = 'spam_text_module/parameters/embeddingsglove.pickle'
scaler = 'spam_text_module/parameters/minmaxscale.csv'
spam_words = 'spam_text_module/parameters/top20spamwords.txt'

# OTHER CONSTANTS
spam_threshold = 0.5
