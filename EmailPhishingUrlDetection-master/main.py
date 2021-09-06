import imaplib
import re
import threading
import getpass
from datetime import datetime, date, timedelta
import MachineLearning as RF
import FakeDomains as FD
import time
import email
import tldextract
from win10toast import ToastNotifier


user_wish = int(input("Kendiniz URL girmek istiyorsanız 1, Emaillerinizdeki URL'ler test edilsin istiyorsanız 2 yazınız: "))
user_continue = 1

if user_wish == 1:
    while user_continue == 1:
        machine_learning = 1
        link = input("Lütfen URL giriniz: ")
        try:
            if not re.match(r"^https?", link):
                url = "http://" + link
        except:
            print("Lütfen geçerli bir url giriniz!!!")
            break
        try:
            domain = re.findall(r"://([^/]+)/?", link)[0]
        except:
            print("Lütfen geçerli bir url giriniz!!!")
            break

        if re.match(r"^www.", domain):
            domain = domain.replace("www.", "")
        if (RF.randomForestChecker(link) == link + " Kriter Testinden Geçemedi!!!"):
            print(link + " Kriter Testinden Geçemedi!!!")
            machine_learning = 0
        else:
            print(link + " Kriter Testinde Temiz Çıktı")

        if machine_learning != 0 and FD.fakeDomainChecker(domain) != 0:
            print(domain + " domain adresi sahte olabilir !!")

        user_continue=int(input("Başka bir url ile devam etmek istiyorsanız 1, işlemi sonlandırmak istiyorsanız 2 yazınız: "))


elif user_wish == 2:
    email_user = input("Lütfen Email Adresini Giriniz: ")
    email_pass = getpass.getpass(prompt='Lütfen Şifrenizi Giriniz: ')

    print("Dünün ve bugünün okunmamış mailleri değerlendirilecek.")

    url_checked_list = []
    mydic = [  {"urls" : [], "sender" : ""} ]

    toaster = ToastNotifier()

    def connect_email_account():
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        try:
            mail.login(email_user, email_pass)
            mail.select("inbox")
            return mail

        except Exception as e:
                 print("Mail adresinize bağlanırken bir hata oluştu. Lütfen kullanıcı adınızı ve şifrenizi kontrol ediniz.")
                 print("Eğer bilgilerinizi doğru girdiğinizden eminseniz, erişim sağlayabilmek için eğer varsa mail hesabınızın iki faktörlü korumasını iptal ediniz.")
                 exit()

    def find_links():
        yesterday = (date.today() - timedelta(1)).strftime("%d-%b-%Y")
        typ, search_data = connect_email_account().search(None, '(UNSEEN)', '(SENTSINCE {0})'.format(yesterday))
        search_data = search_data[0].split()

        for emailid in search_data:
            temp_dic = {"urls":[], "sender":""}
            resp, data = connect_email_account().fetch(emailid, '(UID BODY[TEXT])')
            _, b = connect_email_account().fetch(emailid, '(RFC822)')
            _, c = b[0]
            text = str(data[0][1])
            email_message = email.message_from_bytes(c)
            regex1 = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
            for index, link in enumerate(re.finditer(regex1, text)):
                if link.group() not in temp_dic["urls"]:
                    temp_dic["urls"].append(link.group())
            temp_dic["sender"] = email_message["from"]
            mydic.append(temp_dic)

    def the_function(dictionary):
        mail_checked_list = []
        i = 0
        for url in dictionary["urls"]:
            if not re.match(r"^https?", url):
                url = "http://" + url
            extracted = tldextract.extract(url)
            extracted_name = "{}".format(extracted.domain)
            if extracted_name and extracted_name.lower() not in dictionary["sender"] and "usercontent" not in extracted_name and "png" not in url and "email" not in url and "jpeg" not in url and "\\r\\" not in url:
                if FD.fakeDomainChecker(extracted_name) != 0:
                    if extracted_name not in url_checked_list:
                        url_checked_list.append(extracted_name)
                        i += 1
                        if (RF.randomForestChecker(url) == url + " Kriter Testinden Geçemedi!!!"):
                            print("Bir mailinizde tespit edilen " +url +" Kriter Testinden Geçemedi!!!")
                            respond = RF.randomForestChecker(url)
                            toaster.show_toast(respond)
                            mail_checked_list.append(dictionary["sender"])
            """             
            else:
                if FD.fakeDomainChecker(extracted_name) != 0 and "usercontent" not in extracted_name:
                    print(extracted_name +" domain adresi sahte olabilir!!")
                    toaster.show_toast(extracted_name +" domain adresi sahte olabilir!!")
                    mail_checked_list.append(dictionary["sender"]) """
        if dictionary["sender"] != None and "@" in dictionary["sender"] and dictionary["sender"] in mail_checked_list and extracted_name not in url:
            print("Maili gönderen " + dictionary["sender"])

    while 0 < 1:
        find_links()
        threads = []
        for dictionary in mydic:
            t = threading.Thread(target=the_function(dictionary))
            threads.append(t)
            t.start()

        for thread in threads:
            thread.join()
        time.sleep(60)

else:
    print("Lütfen geçerli bir seçenek giriniz!!!")