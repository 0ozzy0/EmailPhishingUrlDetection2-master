import concurrent.futures
import ipaddress
import re
import pandas as pd
import urllib.request
from bs4 import BeautifulSoup
import socket
from googlesearch import search
import requests
import whois
from datetime import datetime, date
import time
import datetime
from dateutil.parser import parse as date_parse


USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
headers = {"user-agent" : USER_AGENT}


def generate_data_set(url):

    data_set = [9,9,9,9,9,9,9,9,9]



    try:
        response = requests.get(url, headers = headers)
        soup = BeautifulSoup(response.text, 'html.parser')
    except:
        response = ""
        soup = -999

    domain = re.findall(r"://([^/]+)/?", url)[0]
    if re.match(r"^www.",domain):
            domain = domain.replace("www.","")

    #site_name = url.split("www.")[-1].split("//")[-1].split(".")[0]

    whois_response = None
    try:
        whois_response = whois.whois(domain)
    except:
        pass


    rank_checker_response = requests.post("https://www.checkpagerank.net/index.php", {
            "name": domain
        })

    try:
        global_rank = int(re.findall(r"Global Rank: ([0-9]+)", rank_checker_response.text)[0])
    except:
        global_rank = -1




    #shortining services
    match=re.search('bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|'
                    'yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|'
                    'short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|'
                    'doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|'
                    'db\.tt|qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|'
                    'q\.gs|is\.gd|po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|'
                    'x\.co|prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|tr\.im|link\.zip\.net',url)
    if match:
        #print("shortining service -1")
        data_set[0] = -1
    else:
        #print("shortining service 1")
        data_set[0] = 1


    # Prefix suffix
    if re.findall(r"-", domain):
        #print("Prefix suffix -1")
        #print("suffix bulundu")
        data_set[1] = -1
    else:
        #print("Prefix suffix 1")
        data_set[1] = 1

    # subdomains existence

    if len(re.findall("\.", domain)) ==1 :
        #print("subdomains 1")
        data_set[2] = 1
    elif len(re.findall("\.", domain)) == 2:
        #print("subdomains 0")
        data_set[2] = 0
    else:
        #print("subdomains -1")
        data_set[2] = -1

    #SSLfinalstate (https in url)



    try:
        creation_date = (whois_response.creation_date)
        today = time.strftime('%Y-%m-%d')
        today = datetime.datetime.strptime(today, '%Y-%m-%d')
        if type(creation_date) == list:
            site_age = abs((creation_date[0] - today).days)
        if type(creation_date) == datetime.datetime:
            site_age = abs((creation_date-today).days)
        #print("site age: " +str(site_age))


        if not re.findall(r"^https://", url):
             #print("https -1")
             data_set[3] = -1
        elif re.findall(r"^https://", url) and site_age > 365:
            data_set[3] = 1
            #print("https 1")
        else:
            #print("https 0")
            data_set[3] = 0

    except Exception as e:
        pass
        "print(e)"


    # url of anchor
    percentage = 0
    i = 0
    unsafe=0
    if soup == -999:
        #print("url of anchor -1")
        data_set[4] = -1
    else:
        for a in soup.find_all('a', href=True):

            if "#" in a['href'] or "javascript" in a['href'].lower() or "mailto" in a['href'].lower() or not (url in a['href'] or domain in a['href']):
                #print(a["href"])
                unsafe = unsafe + 1
            i = i + 1

        try:
            percentage = unsafe / float(i) * 100
            if percentage < 31.0:
                #print("url of anchor 1")
                data_set[4] = 1
            elif ((percentage >= 31.0) and (percentage < 67.0)):
                #print("url of anchor 0")
                data_set[4] = 0
            else:
                #print("url of anchor -1")
                data_set[4] = -1


        except:
            #print("url of anchor 1")
            data_set[4] = -1


    # links in tags
    i=0
    success =0
    if soup == -999:
        #print("link in tags -1")
        data_set[5] = -1
    else:
        for link in soup.find_all('link', href= True):
           dots=[x.start(0) for x in re.finditer('../venv', link['href'])]
           if url in link['href'] or domain in link['href'] or len(dots)==1:
              success = success + 1
           i=i+1

        for script in soup.find_all('script', src= True):
           dots=[x.start(0) for x in re.finditer('../venv', script['src'])]
           if url in script['src'] or domain in script['src'] or len(dots)==1 :
              success = success + 1
           i=i+1
        try:
            percentage = success / float(i) * 100
            if percentage < 17.0:
                #print("link in tags 1")
                data_set[5] = 1
            elif ((percentage >= 17.0) and (percentage < 81.0)):
                #print("link in tags 0")
                data_set[5] = 0
            else:
                #print("link in tags -1")
                data_set[5] = -1
        except:
            #print("link in tags 1")
            data_set[5] = -1



    # age of domain
    if response == "":
        #print("age of domain -1")
        data_set[6] = -1
    else:
        try:
            # creation_date = whois_response.creation_date[0].strftime("%Y")
            creation_date = whois_response.creation_date[0]

        except:
            pass
        try:
            today = time.strftime('%Y-%m-%d')
            today = datetime.datetime.strptime(today, '%Y-%m-%d')
            site_age = abs((creation_date - today).days)
            #print("site age: " + str(site_age))

            if site_age >= 720:
                #print("age of domain 1")
                data_set[6] = 1
            else:
                #print("age of domain -1")
                data_set[6] = -1
        except:
            #print("age of domain -1")
            data_set[6] = -1


    #Dns record
    dns = 1
    try:
        d = whois.whois(domain)
    except:
        dns=-1

    if dns == -1:
        #print("Dns Record -1")
        data_set[7] = -1
    else:
        data_set[7] = 1

    #web traffic
    try:
        rank = BeautifulSoup(urllib.request.urlopen("http://data.alexa.com/data?cli=10&dat=s&url=" + url).read(), "xml").find("REACH")['RANK']

        #print("web traffic : " +str(rank))
        if (int(rank)<100000):
            #print("web traffic 1")
            data_set[8] = 1
        elif (int(rank) > 100000):
            #print("web traffic 0")
            data_set[8] = 0
        else:
            data_set[8] = -1
    except TypeError:
        #print("web traffic -1")
        data_set[8] = -1

    return data_set



