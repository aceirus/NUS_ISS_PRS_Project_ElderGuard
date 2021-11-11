# Manual Feature Extraction
from urllib.parse import urlparse
import tldextract
import joblib
import numpy as np
from config import *
import joblib


'''
'tot_url_length', 'netloc_length', 'path_length', 'fd_length', 'suffix_length',
'num_subdomains', 'domain-', 'url-', 'path-', 'url_',
'path_', 'count_dir', 'path_fs_.', 'count@', 'count?',
'count%', 'count.', 'count=', 'count-http_inpath', 'count-https_inpath', 
'count-www_inpath', 'count-digits', 'count-letters'
'''

def parse_url(url):
    try:
        no_scheme = not url.startswith('https://') and not url.startswith('http://')
        if no_scheme:
            parsed_url = urlparse(f"http://{url}")
            return {
                "scheme": None, # not established a value for this
                "netloc": parsed_url.netloc,
                "path": parsed_url.path,
                "params": parsed_url.params,
                "query": parsed_url.query,
                "fragment": parsed_url.fragment,
            }
        else:
            parsed_url = urlparse(url)
            return {
                "scheme": parsed_url.scheme,
                "netloc": parsed_url.netloc,
                "path": parsed_url.path,
                "params": parsed_url.params,
                "query": parsed_url.query,
                "fragment": parsed_url.fragment,
            }
    except:
        return None


def tld_extract(url):
    # extract subdomain, domain, and domain suffix from url
    # if item == '', fill with '<empty>'
    subdomain, domain, domain_suffix = (None if extracted == '' else extracted for extracted in tldextract.extract(url))
    return {"subdomain": subdomain, "domain": domain, "suffix": domain_suffix}


def get_num_subdomains(netloc: str) -> int:
    subdomain = tldextract.extract(netloc).subdomain
    if subdomain == "":
        return 0
    return subdomain.count('.') + 1


def digit_count(url):
    digits = 0
    for i in url:
        if i.isnumeric():
            digits = digits + 1
    return digits


def letter_count(url):
    letters = 0
    for i in url:
        if i.isalpha():
            letters = letters + 1
    return letters


def manual_feature_extraction(url):
    parseurl = parse_url(url)
    tldurl = tld_extract(url)

    tot_url_length = len(url)
    netloc_length = len(parseurl['netloc'])
    path_length = len(parseurl['path'])

    fd_length = 0 if '/' not in parseurl['path'] else len(parseurl['path'].split('/')[1])

    suffix_length = 0 if tldurl['suffix'] is None else len(tldurl['suffix'])

    num_subdomains = get_num_subdomains(parseurl['netloc'])

    count_dir = parseurl['path'].count("/")
    path_fsdot = parseurl['path'].count(".")

    path_ = parseurl['path'].count("_")
    domaindesk = parseurl['netloc'].count("-")
    pathdesk = parseurl['path'].count("-")

    countat = url.count("@")
    countquest = url.count("?")
    countpercent = url.count("%")
    countdot = url.count(".")
    counteq = url.count("=")
    urldesk = url.count("-")
    countunderscore = url.count("_")

    count_https_inpath = parseurl['path'].count("https")
    count_http_inpath = parseurl['path'].count("https")
    count_www_inpath = parseurl['path'].count("www")

    countdigits = digit_count(url)
    countletters = letter_count(url)

    mf_arr = np.array(
        [tot_url_length, netloc_length, path_length, fd_length, suffix_length, num_subdomains, domaindesk, urldesk,
         pathdesk, countunderscore, path_, count_dir, path_fsdot, countat, countquest, countpercent, countdot,
         counteq, count_http_inpath, count_https_inpath, count_www_inpath, countdigits, countletters])

    mf_arr_reshp = np.reshape(mf_arr,(1,-1))
    #scaler_filename = 'malurl_module/models/Scaler23.jlib'
    scaler = joblib.load(scaler_filename)
    mf_arr_scale = scaler.transform(mf_arr_reshp)

    return mf_arr_scale