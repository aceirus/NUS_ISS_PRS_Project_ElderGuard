import re
from flask import Flask, request, make_response, jsonify
import requests
import config
from spam_text_module import predict_spam as spam
from phishing_module import predict_url as phish
from malurl_module import mal_predict_url as malurl

app = Flask(__name__)

@app.route("/")
def home_view():
    return "<h1>Welcome to ElderGuard</h1>"

def extraction(msg):
    msg_list = msg.split()
    text_list = []
    url_list = []
    sw_tup_prot = tuple(['https', 'http', 'www'])
    regex = "[a-zA-Z0-9@:%._\\+~#?&//=]{2,256}\\.[a-z]" + "{2,6}\\b([-a-zA-Z0-9@:%._\\+~#?&//=]*)"
    p = re.compile(regex)
    for word in msg_list:
        if str(word).lower().startswith(sw_tup_prot) or re.search(p, word):
            if word.endswith("."):
                word = word[:-1]
            print(word)
            if "://" in word:
                word = word.split('://')[1]
            url_list.append(word)
        else:
            text_list.append(word)

    text_string = ' '.join([str(elem) for elem in text_list])

    return text_string, url_list


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    request_data = request.get_json(force=True, silent=True)
    text_string, url_list = extraction(request_data['txt'])
    # send text_string to spam/ham model and output text_predict
    # to call function
    text_result = str(int(spam.predict_spam(text_string, config.spam_threshold)))

    # send url_string to url model and output url_predict
    # to call function
    urlphish_result = phish.predict_url(url_list) # return dict
    urlmalicious_result = malurl.mal_predict_url(url_list)

    if "Bad" in urlphish_result.values() or "Bad" in urlmalicious_result.values():
        url_result = "1"
    else:
        url_result = "0"

    # send text_result and url_result to get the final result
    if text_result == "1" or url_result == "1":
        final_result = "1"
    else:
        final_result = "0"

    safe_text_string = 'The text message is safe!'
    unsafe_text_string = 'The text message is not safe!'
    phishing_holder_string = 'Phishing link(s) detected: '
    malicious_holder_string = 'Malicious link(s) detected: '
    # Determine result string to print
    if text_result == "0" and url_result == "0":
        result_string = safe_text_string
    elif text_result == "1" and url_result == "0":
        result_string = unsafe_text_string
    elif text_result == "1" and url_result == "1":
        result_string = unsafe_text_string
        if "Bad" in urlphish_result.values():
            phish_result = []
            for link in urlphish_result.keys():
                if urlphish_result[link] == 'Bad':
                    phish_result.append(link)
            result_string = result_string + ' ' + phishing_holder_string + ', '.join(phish_result)
        if "Bad" in urlmalicious_result.values():
            mali_result = []
            for link in urlmalicious_result.keys():
                if urlmalicious_result[link] == 'Bad':
                    mali_result.append(link)
            result_string = result_string + ' ' + malicious_holder_string + ', '.join(mali_result)
    elif text_result == "0" and url_result == "1":
        result_string = safe_text_string
        if "Bad" in urlphish_result.values():
            phish_result = []
            for link in urlphish_result.keys():
                if urlphish_result[link] == 'Bad':
                    phish_result.append(link)
            result_string = result_string + ' ' + phishing_holder_string + ', '.join(phish_result)
        if "Bad" in urlmalicious_result.values():
            mali_result = []
            for link in urlmalicious_result.keys():
                if urlmalicious_result[link] == 'Bad':
                    mali_result.append(link)
            result_string = result_string + ' ' + malicious_holder_string + ', '.join(mali_result)


    return jsonify(text=result_string,
                   # text_predict=text_result,
                   # urlphish_predict=urlphish_result,
                   # urlmalicious_predict=urlmalicious_result,
                   final_predict=final_result)

# url=['www.channelnewsasia.com', 'nus.com', 'www.google.com', "chicagoofficefurniture.com/chicagoofficefurniture/"
#      'https://www.pawthereum.claim-rewards-stake.com/metamask/import.html',
#      'https://ontvangst-tarief-protocol.xyz/home/sorteercentrum/postnl/postNL-3S92869038192.php',
#      'http://klaimeventgarena21.duckdns.o', 'westerncentermuseum.org/plugins/tmp/sp.php']
# print(phish.predict_url(url))
# # print(malurl.mal_predict_url(url))