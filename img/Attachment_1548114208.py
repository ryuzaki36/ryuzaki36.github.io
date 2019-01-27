from datetime import datetime, timedelta
import re
import os, random, requests, string, sys, time
from PyQt5.QtCore import pyqtSlot, QThread, Qt
from PyQt5.QtGui import QIcon, QGuiApplication
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton, QWidget, QAction, QTabWidget, QVBoxLayout,
                             QGroupBox, QHBoxLayout, QLineEdit, QMessageBox, QLabel, QProgressBar, QTextEdit,
                             QCheckBox, QSizePolicy)
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.proxy import *
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from concurrent.futures import ThreadPoolExecutor
import itertools
import string
import subprocess

def install_package(package):
    subprocess.call([sys.executable, '-m', 'pip', 'install', package], shell=True)

try:
    import imapclient
except ImportError:
    print('imap client not installed .. installing')
    install_package('imapclient')

try:
    import pyzmail
except ImportError:
    print('pyzmail not installed .. installing')
    install_package('pyzmail36')

##########################################
# ADDED CONSTANTS.
##########################################
api_key = 'd18517cba749889ef4ae726dac739591'
captcha_file = 'captcha.jpg'
REG_LINK = 'https://www.amazon.com/ap/register?_encoding=UTF8&openid.assoc_handle=usflex&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2Fgp%2Fyourstore%2Fhome%3Fie%3DUTF8%26ref_%3Dnav_newcust'
SIGNIN_LINK = 'https://www.amazon.com/ap/signin?openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_ya_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&&openid.pape.max_auth_age=0'
AMAZON_STORE = 'https://www.amazon.com/shops/Greatlowprices1'
TEMP_PRD = ['https://www.amazon.com/iPhone-X-Case/dp/B07MJTZH92/ref=sr_1_1?ie=UTF8&qid=1545717782&sr=8-1&keywords=iphone+x+case&node=3081461011',
    'https://www.amazon.com/iPhone-X-Case/dp/B07M7YG11G/ref=sr_1_1?ie=UTF8&qid=1545717782&sr=8-1&keywords=iphone+x+case&node=3081461011']
MAIL_USER = 'jkosoyan95309_catchall@jkosoyan95309.ipage.com'
MAIL_PASS = 'Fiverr11!'
SIGNIN_FILE = 'SIGNIN.txt'
ACCOUNT_FILE = 'ACCOUNTS.txt'
PHONE_AND_ACCESORIES = 'https://www.amazon.com/s/ref=sr_nr_n_8?fst=as%3Aoff&rh=n%3A9414313011%2Ck%3Aiphone+x+case&keywords=iphone+x+case&ie=UTF8&qid=1547662172&rnid=2941120011'
##########################################

enableCaptchaRegistration = True

try:
    with open("proxy.txt", "r") as f:
        proxy_list = f.read().strip().split("\n")
except FileNotFoundError:
    input("proxy.txt file not found please create the file and save the proxy list in it...")
    exit()

try:
    with open(SIGNIN_FILE) as f:
        signin_accounts = f.read().strip().split("\n")
except FileNotFoundError:
    signin_accounts = []
    input(f'WARNING: {SIGNIN_FILE} file not found .. (sign in mode wont work in this case)\npress enter to continue')


desktop_agents = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0']


def random_headers():
    return {'User-Agent': random.choice(desktop_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}


def get_random_name():
    global first_name, last_name
    r = requests.get('http://www.fakenamegenerator.com/gen-female-us-us.php', headers=random_headers())
    c = r.content
    soup = BeautifulSoup(c, 'lxml')
    name = soup.find('h3').text
    name = name.replace('.', '')
    first_name, last_name = name.split(" ")[0], name.split(" ")[-1]
    name = name.replace(" ", "")
    return name


def get_random_partner():
    r = requests.get('http://www.fakenamegenerator.com/gen-male-us-us.php', headers=random_headers())
    c = r.content
    soup = BeautifulSoup(c, 'lxml')
    name = soup.find('h3').text
    name = name.replace('.', '')
    first_name, last_name = name.split(" ")[0], name.split(" ")[-1]
    address = re.sub("\s\s+|\n+", " ", soup.find("div", attrs={"class": "adr"}).text.strip())
    zip_code = re.search("[A-Z][A-Z] (\d\d\d\d\d)", address).group(1)
    state = re.search("[A-Z][A-Z]", address).group()
    city = re.search("(\w+),", address).group(1)
    phone = re.search("\d\d\d-\d\d\d-\d\d\d", str(soup)).group()
    female_name = get_random_name()
    return name, female_name, first_name, last_name, address, city, state, zip_code, phone

def get_confirmation_link_register(email):
    try:
        print(f'Fetching vefification email ', end='', flush=True)
        imap = imapclient.IMAPClient('imap.ipage.com', ssl=True)
        imap.login(MAIL_USER, MAIL_PASS)
        imap.select_folder('INBOX', readonly=True)
        uids = imap.search('SUBJECT "Amazon password assistance" UNSEEN TO %s'%(email))
        
        if len(uids) == 0:
            print('No Email Fetched. ...')
            #uids = imap.search('SUBJECT "Your Amazon verification code" UNSEEN TO %s'%(email))
            #time.sleep(2)
            #if len(uids) == 0:
             #   get_confirmation_link(email)
        else:
            #print('uids len ', uids)
            msg = imap.fetch(uids, ['BODY[]'])
            msg_ = pyzmail.PyzMessage.factory(msg[uids[-1]][b'BODY[]'])

            data =  msg_.html_part.get_payload().decode(msg_.html_part.charset)
            soup = BeautifulSoup(data, 'html.parser')
            res = soup.find('p', class_='otp').text.strip()
            imap.logout()
            print(f'{res}')
            return res
    except Exception as ex:
        print(f'Exception in email retrieval ..: {ex}')

def get_confirmation_link_signin(email):
    try:
        print(f'Fetching vefification email ', end='', flush=True)
        imap = imapclient.IMAPClient('imap.ipage.com', ssl=True)
        imap.login(MAIL_USER, MAIL_PASS)
        imap.select_folder('INBOX', readonly=True)
        uids = imap.search('SUBJECT "Your Amazon verification code" UNSEEN TO %s'%(email))
        
        if len(uids) == 0:
            print('No Email Fetched. ...')
            #uids = imap.search('SUBJECT "Your Amazon verification code" UNSEEN TO %s'%(email))
            #time.sleep(2)
            #if len(uids) == 0:
             #   get_confirmation_link(email)
        else:
            #print('uids len ', uids)
            msg = imap.fetch(uids, ['BODY[]'])
            msg_ = pyzmail.PyzMessage.factory(msg[uids[-1]][b'BODY[]'])

            data =  msg_.html_part.get_payload().decode(msg_.html_part.charset)
            soup = BeautifulSoup(data, 'html.parser')
            res = soup.find('p', class_='otp').text.strip()
            imap.logout()
            print(f'{res}')
            return res
    except Exception as ex:
        print(f'Exception in email retrieval ..: {ex}')



#####################################################################################
# TWO FUNCTION ADDED
#   1. DOWNLOAD IMAGE
#   2. SOLVE CAPTCHA
#   3.GET RANDOM PARTNER
####################################################################################
def solve_captcha(filename, api_key):
    print('Solving captcha ...')
    try:
        captcha = 'default'
        in_url = 'http://2captcha.com/in.php'
        res_url = 'http://2captcha.com/res.php'
        data = {'key': api_key, 'method': 'post'}
        files = {'file': open(filename, 'rb')}
        r = requests.post(in_url, files=files, data=data)
        if r.status_code == requests.codes.ok:
            print('Request OK')
            if '|' in r.text:
                id_ = r.text.split('|')[-1]
                time.sleep(15)
                r2 = requests.get(f'{res_url}?key={api_key}&action=get&id={id_}')
                if r2.status_code == requests.codes.ok:
                    if 'OK' in r2.text:
                       captcha =  r2.text.split('|')[-1]
    except Exception as ex:
        print(f'Exception occured while solving captcha: {ex}')
        print('Trying again ..')
        captcha = solve_captcha()

    if (captcha == 'default'):
        print('failed to fetch captcha from server..returning default')

    return captcha

########################################################################################
def download_image(url, image_file_name='captcha.jpg'):
    print('[+] Downloading captcha image ..')
    print('URL: {}'.format(url))

    try:
        r = requests.get(url, stream=True)
        r.raise_for_status()
    except requests.exceptions.ConnectionError:
        print()
        print('[x] Unable to download captcha image, please ensure internet connection!')
        exit_()
    else:
        if r.status_code != 200:
            print()
            print('[x] Unable to download image, please image address')
            exit_()
        else:
            # downlaod the image
            img_handle = open(image_file_name, 'wb')
            for chunk in r.iter_content(1000):
                img_handle.write(chunk)
            img_handle.close()
            print('[+] Image Download Success.')
            time.sleep(1)
    return True
#######################################################################################
def get_random_partner1(threadNum):
    print(f'[Instance {threadNum}]:Fetching random name ..')
    r = requests.get('http://www.fakenamegenerator.com/gen-female-us-us.php', headers=random_headers())
    c = r.content
    soup = BeautifulSoup(c, 'lxml')
    name = soup.find('h3').text
    name = name.replace('.', '')
    first_name, last_name = name.split(" ")[0], name.split(" ")[-1]
    address = re.sub("\s\s+|\n+", " ", soup.find("div", attrs={"class": "adr"}).text.strip())
    zip_code = re.search("[A-Z][A-Z] (\d\d\d\d\d)", address).group(1)
    state = re.search("[A-Z][A-Z]", address).group()
    city = re.search("(\w+),", address).group(1)
    phone = re.search("\d\d\d-\d\d\d-\d\d\d", str(soup)).group()
    rr = soup.find('div', class_='extra').find_all('dl')
    for i, dl in enumerate(rr):
        if 'Expires' in dl.find('dt').text:
            expiration = dl.find('dd').text.strip()
            card_number = rr[i-1].find('dd').text.strip()
            break
    else:
        expiration = 'NoExpiration'

    female_name = get_random_name()
    print(f'Done fetching name.')
    return name, female_name, first_name, last_name, address, city, state, zip_code, phone, expiration, card_number
#######################################################################################


def create_wedding_list(browser, threadNum):
    try:
        name, female_name, first_name, last_name, address, city, state, zip_code, phone = get_random_partner()
        browser.get("https://www.amazon.com/wedding/new-registry?associateId=&associateSubId=")
        browser.find_element_by_name('firstNamePartner1').send_keys(first_name)
        browser.find_element_by_name('surnamePartner1').send_keys(last_name)
        browser.find_element_by_name('firstNamePartner2').send_keys(female_name)
        browser.find_element_by_name('surnamePartner2').send_keys(female_name)

        browser.find_element_by_name('address-ui-widgets-enterAddressFullName').send_keys(name)
        browser.find_element_by_name('address-ui-widgets-enterAddressLine1').send_keys(address[:-5])
        browser.find_element_by_name('address-ui-widgets-enterAddressLine2').send_keys(address[-5:])

        browser.find_element_by_name('address-ui-widgets-enterAddressCity').send_keys(city)
        browser.find_element_by_name('address-ui-widgets-enterAddressStateOrRegion').send_keys(state)
        browser.find_element_by_name('address-ui-widgets-enterAddressPostalCode').send_keys(zip_code)
        browser.find_element_by_name('address-ui-widgets-enterAddressPhoneNumber').send_keys(phone)

        #event_month = Select(browser.find_element_by_id('wr-cm-event-date-month'))
        #event_month.select_by_value(str(random.randint(0, 11)))
        browser.execute_script(f"document.getElementById('wr-cm-event-date-month').selectedIndex = {str(random.randint(2, 11))}")
        time.sleep(2)

        #event_day = Select(browser.find_element_by_id('wr-cm-event-date-day'))
        #event_day.select_by_value(str(random.randint(1, 25)))

        browser.execute_script(f"document.getElementById('wr-cm-event-date-day').selectedIndex = {str(random.randint(4, 25))}")
        time.sleep(2)

        #event_year = Select(browser.find_element_by_id('wr-cm-event-date-year'))
        #event_year.select_by_value(str(random.randint(2019, 2020)))

        browser.execute_script(f"document.getElementById('wr-cm-event-date-year').selectedIndex = {str(random.randint(2, 4))}")
        time.sleep(2)


        browser.find_element_by_name('weddingCity').send_keys(city)
        print('Starting to selecting state')
        time.sleep(2)
        #event_state = Select(browser.find_element_by_id('wr-cm-event-state'))
        #event_state.select_by_value("NY")
        browser.execute_script(f"document.getElementById('wr-cm-event-state').selectedIndex = {str(random.randint(1, 5))}")
        time.sleep(2)

        ##########################################################################################
        ### ADDED CODE.
        #

        # click the add address button
        browser.find_element_by_xpath('//*[@id="address-ui-widgets-enterAddressFormContainer"]/span/span/input').click()
        time.sleep(5)

        # solve the captcha
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        cap = soup.find('img', {'id': 'wr-cr-captcha-image'})
        if cap is not None:
            captcha_image_file = 'wedding-list-captcha-thread-' + str(threadNum) + '.jpg'
            img_res = download_image(cap.get('src'), captcha_image_file)
            if img_res:
                captcha = solve_captcha(captcha_image_file, api_key)

        print(f'Captcha solved! {captcha}')
        
        # send captcha to box.
        browser.find_element_by_id('wr-cr-captcha-input-box').send_keys(captcha)    

        #
        ###
        ########################################################################################
        time.sleep(2)

        # Adding address again.  
        browser.find_element_by_xpath('//*[@id="address-ui-widgets-enterAddressFormContainer"]/span/span/input').click()
        time.sleep(2)
        # first click
        try:
            print('Trying first click')
            browser.find_elements_by_class_name('a-button-input')[-1].click()
        except Exception as ex:
            print(f'Exception in while clicking submit wedding 1')

        time.sleep(2)

        #time.sleep(4)
        print('Trying second click')

        btn = browser.find_elements_by_class_name('a-button-input')[-1]

        browser.execute_script('arguments[0].click();', btn)
        time.sleep(2)


        try:
            browser.find_element_by_link_text('No Thanks').click()
        except Exception:
            print('No Thanks button on wedding list')      

    except Exception as ex:
        print(f'Exception occured in wedding list: {ex}')



def insert_into_table(keyword, rank, url):
    print("Shaddy url skipped...")
    # payload = {'keyword': keyword,'rank': rank,'url': url,'submit': 'submit'}
    # requests.post('http://curlas.com/amazon.php', data=payload)


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Amazon Bot v1.3'
        self.left = 100
        self.top = 100
        self.width = 800
        self.height = 600
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.table_widget = MyTableWidget(self)
        self.setCentralWidget(self.table_widget)
        self.show()

def save_account(proxy, username, password, threadNum=0):
    threadIndex = threadNum
    print(f'[Instance {threadIndex}]:Saving Account: ({username}:{password})')
    with open(ACCOUNT_FILE, 'a') as handle:
        handle.write(':'.join([username, password]) + '\n')

def gen_password():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))


def sign_in(browser, username, password, threadNum=0):
    threadIndex = threadNum
    try:
        browser.get(SIGNIN_LINK)
        time.sleep(2)

        browser.find_element_by_name('email').send_keys(username)
        browser.find_element_by_name('password').send_keys(password)
        submit  = browser.find_element_by_id('signInSubmit')
        browser.execute_script('arguments[0].click();', submit)
    except Exception as ex:
        print(f'{ex}')
        print(f'[Instance {threadIndex}]:The registration page did not load. Please check your proxy IP')
        print(f'[Instance {threadIndex}]:Quitting..')
        browser.quit()
        return False

    #input('Heello ...')

    # there's this new button
    #if '' in browser.title:
    if 'We will send you a code to ensure the security' in browser.page_source:
        browser.find_element_by_id('continue').click()


    if 'Sign In' in browser.title:
        # means we didnt proceed
        if 'Your password is incorrect' in browser.page_source:
            print(f'[Instance {threadIndex}]:Incorrect Password supplied to program')
            time.sleep(2)
            browser.quit()
            return False

        elif 'We cannot find an account with that email address' in browser.page_source:
            print(f'[Instance {threadIndex}]:Invalid Account supplied to program')
            time.sleep(2)
            browser.quit()
            return False

        elif 'enter the characters as they are shown in the image below.' in browser.page_source:
            while  True:
                browser.find_element_by_name('password').send_keys(password)
                
                #################################
                #we can check for captcha here.
                #################################
                soup = BeautifulSoup(browser.page_source, 'html.parser')
                cap = soup.find('img', {'id': 'auth-captcha-image'})

                if enableCaptchaRegistration:
                    captcha = None
                    if cap is not None:
                        print(f'[Instance {threadIndex}]:Registration CAPTCHA detected')
                        captcha_image_file = 'captcha-' + str(threadNum) + '.jpg'
                        img_res = download_image(cap.get('src'), captcha_image_file)
                        if img_res:
                            captcha = solve_captcha(captcha_image_file, api_key)

                        print(f'[Instance {threadIndex}]:Captcha received {captcha}')
                    
                        # send captcha to box.
                        print(f'[Instance {threadIndex}]:Entering captcha..')
                        browser.find_element_by_id('auth-captcha-guess').send_keys(captcha)  

                        submit  = browser.find_element_by_id('signInSubmit')
                        browser.execute_script('arguments[0].click();', submit)
                        time.sleep(3)
                        # check if captcha is still present
                        soup = BeautifulSoup(browser.page_source, 'html.parser')
                        capNew = soup.find('img', {'id': 'auth-captcha-image'})

                        if capNew is not None:
                            print(f'[Instance {threadIndex}]:CAPTCHA SOLVING FAILED.')
                            print(f'[Instance {threadIndex}]:Wrong captcha recieved by server.. ')
                            time.sleep(2)
                            #browser.quit()
                            #return False
                            continue
                        else:
                            break

                    #delete screenshot since captcha has been solved successfully
                    #os.remove(captcha_screenshot)
                    print(f'[Instance {threadIndex}]:Captcha solved successfully!')
                else:
                    if cap is not None:
                        print(f'[Instance {threadIndex}]:Oops. Registration CAPTCHA detected. Quitting..') 
                        time.sleep(2)
                        browser.quit()
                        return False

    
    if 'We will send you a code to ensure the security' in browser.page_source:
        browser.find_element_by_id('continue').click()
        
    #input('hello ..')
    ################################3
    # WE CAN CHECK FOR EMAIL VERIFICATION HERE
    ################################## 
    # CHECK IF EMAIL IS REQUIRED
    if 'Verify email address' in browser.page_source or 'Please confirm your identity' in browser.title:
        print(f'[Instance {threadIndex}]:########################################')
        print(f'[Instance {threadIndex}]:[x] Email verification required ')
        print(f'[Instance {threadIndex}]:#########################################')
        print('sleeping and Waiting for verification email ... ')
        time.sleep(25)
        verification_number = get_confirmation_link_signin(username)
        browser.find_element_by_name('code').send_keys(verification_number)
        #submit = browser.find_element_by_id('a-autoid-0-announce')
        #browser.execute_script('arguments[0].click();', submit)
        browser.execute_script('document.getElementsByTagName("form")[0].submit()')

        # input('Enterr to continue')
        #,time.sleep(5)
        if 'Sign In' in browser.title:
            print('RE -  Signing in (Required)')
            # sigh in again.
            sign_in(browser, username, password, threadNum)

            time.sleep(5)
        else:
            print('No sign in requested!')

    return True


def register_all(proxy, browser, threadNum=0):
    threadIndex = threadNum
    # done creating account
    name, female_name, first_name, last_name, address, city, state, zip_code, phone, date_r, card_number = get_random_partner1(threadNum)
    name = name.replace(" ", "")
    ##########################3##
    # REGISTER ACCOUNT
    ##############################
    print(f'[Instance {threadIndex}]:Creating account ..')
    browser.get(REG_LINK)
    time.sleep(2)
    try:
        browser.find_element_by_name('customerName').send_keys(name)
        username = name + '2019@hyeemail.com'
        password = gen_password()
        browser.find_element_by_name('email').send_keys(username)
        browser.find_element_by_name('password').send_keys(password)
        browser.find_element_by_name('passwordCheck').send_keys(password)
        browser.find_element_by_id('continue').click()
    except:
        print(f'[Instance {threadIndex}]:The registration page did not load. Please check your proxy IP')
        print(f'[Instance {threadIndex}]:Quitting..')
        browser.quit()
        return False
    time.sleep(5)

    # solve the captcha
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    cap = soup.find('img', {'id': 'auth-captcha-image'})

    if enableCaptchaRegistration:
        captcha = None
        if cap is not None:
            print(f'[Instance {threadIndex}]:Registration CAPTCHA detected')
            captcha_image_file = 'captcha-' + str(threadNum) + '.jpg'
            img_res = download_image(cap.get('src'), captcha_image_file)
            if img_res:
                captcha = solve_captcha(captcha_image_file, api_key)

            print(f'[Instance {threadIndex}]:Captcha received {captcha}')
        
            # send captcha to box.
            print(f'[Instance {threadIndex}]:Entering captcha..')
            browser.find_element_by_id('auth-captcha-guess').send_keys(captcha)  
            browser.find_element_by_name('password').send_keys(password)
            browser.find_element_by_name('passwordCheck').send_keys(password)

            #captcha_screenshot = f'instance-{threadIndex}-failed-captcha-{captcha}.png'
            #browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            #print(f'[Instance {threadIndex}]:Taking screenshot of entered captcha. Check entered-captcha-xxxx.png for captcha comparison')
            #browser.save_screenshot(captcha_screenshot)

            time.sleep(2)
            browser.find_element_by_id('continue').click()
        
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            capNew = soup.find('img', {'id': 'auth-captcha-image'})
            if capNew is not None:
                print(f'[Instance {threadIndex}]:CAPTCHA SOLVING FAILED.')
                print(f'[Instance {threadIndex}]:Wrong captcha recieved by server.. quitting')
                time.sleep(2)
                browser.quit()
                return False

            #delete screenshot since captcha has been solved successfully
            #os.remove(captcha_screenshot)
            print(f'[Instance {threadIndex}]:Captcha solved successfully!')
    else:
        if cap is not None:
            print(f'[Instance {threadIndex}]:Oops. Registration CAPTCHA detected. Quitting..') 
            time.sleep(2)
            browser.quit()
            return False
   


    # CHECK IF EMAIL IS REQUIRED
    if 'Verify email address' in browser.page_source or 'Please confirm' in browser.title:
        print(f'[Instance {threadIndex}]:########################################')
        print(f'[Instance {threadIndex}]:[x] Email verification required ')
        print(f'[Instance {threadIndex}]:#########################################')
        print('sleeping and Waiting for verification email ... ')
        time.sleep(15)
        verification_number = get_confirmation_link_register(username)
        browser.find_element_by_name('code').send_keys(verification_number)
        #submit = browser.find_element_by_id('a-autoid-0-announce')
        #browser.execute_script('arguments[0].click();', submit)
        browser.execute_script('document.getElementsByTagName("form")[0].submit()')

        # input('Enterr to continue')
        #,time.sleep(5)
        if 'Sign In' in browser.title:
            print('RE -  Signing in (Required)')
            # sigh in again.
            sign_in(browser, username, password, threadNum)

            time.sleep(5)
        else:
            print('No sign in requested!')

        #browser.quit()
        #return False

    # we can save the account here 
    save_account(proxy, username, password)
    ##############################
    # ADD ADDRESS AND CC
    ##############################
    



    ###########################
    # ADD PAYMENT
    ##########################
    

    
    ##############################
    time.sleep(2)
    return True

def create_wish_list(browser):
    #print('Visiting wishlist url')
    #browser.get('https://www.amazon.com/gp/registry/wishlist/ref=nav_wishlist_create?ie=UTF8&triggerElementID=createList')
    # click the add to list button instead
    time.sleep(5)
    print('Clicking add list button ...')
    wish_button = browser.find_element_by_name('submit.add-to-registry.wishlist')
    browser.execute_script('arguments[0].click();', wish_button)

    time.sleep(3)
     # selects public or public
    browser.find_element_by_xpath('//*[@id="WLNEW_privacy_public"]/span/input').click()
    time.sleep(1)
    # select type --> wish or shoplist
    browser.find_element_by_xpath('//*[@id="WLNEW_section_wlType"]/div[2]/div[2]/div/div/span/div/label').click()
    time.sleep(2)
    # submit the list
    wait = WebDriverWait(browser, 10)
    submit = wait.until(EC.visibility_of_element_located((By.XPATH, '//form[@action="/gp/registry/wishlist"]/div[2]/span[3]/span/span/input')))
    #submit = browser.find_element_by_xpath('//form[@action="/gp/registry/wishlist"]/div[2]/span[3]/span/span/input')
    browser.execute_script('arguments[0].click();', submit)
    time.sleep(2)
    browser.find_element_by_xpath('//button[contains(text(), "Continue shopping")]').click()
    time.sleep(2)

def create_shopping_list(browser):
    #print('Visiting shoppinglist url')
    #browser.get('https://www.amazon.com/gp/registry/wishlist/ref=nav_wishlist_create?ie=UTF8&triggerElementID=createList')
    time.sleep(5)
    print('Clicking add list button ...')
    wish_button = browser.find_element_by_name('submit.add-to-registry.wishlist')
    browser.execute_script('arguments[0].click();', wish_button)

    time.sleep(3)
     # selects public or public
    browser.find_element_by_xpath('//*[@id="WLNEW_privacy_public"]/span/input').click()
    time.sleep(2)
    # submit the list
    wait = WebDriverWait(browser, 10)
    submit = wait.until(EC.visibility_of_element_located((By.XPATH, '//form[@action="/gp/registry/wishlist"]/div[2]/span[3]/span/span/input')))
    #submit = browser.find_element_by_xpath('//form[@action="/gp/registry/wishlist"]/div[2]/span[3]/span/span/input')
    browser.execute_script('arguments[0].click();', submit)
    time.sleep(2)
    browser.find_element_by_xpath('//button[contains(text(), "Continue shopping")]').click()
    time.sleep(2)

def click_images(browser):
    # when in product page .
    print('Clicking product images ..')
    time.sleep(2)
    browser.find_element_by_id('landingImage').click()
    time.sleep(2)
    for i in range(20):
        try:
            time.sleep(2)
            browser.find_element_by_id(f'ivImage_{i}').click()
        except Exception as ex:
            print(f'Could not print more images')
            break

    # escape the box
    try:
        webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()
    except Exception as ex:
        print(f'[Instance {threadIndex}]:Could not use escape key for pop up ')

    print('Done clicking images.')

class MyTableWidget(QWidget):
    def add_from_groups(self, threadNum):
        threadIndex = threadNum
        textboxValue_username_events_one = self.textbox_username_events_search.toPlainText().split('\n')
        textboxValue_amazon_asin_one = self.textbox_amazon_asin_search.text()
        textboxValue_amazon_loop_one = self.textbox_amazon_loop_search.text()
        textboxValue_break_first_one = self.textbox_amazon_break_first_search.text()
        textboxValue_break_second_one = self.textbox_amazon_break_second_search.text()
        textboxValue_keyword_to_search_one = self.textbox_keyword_to_search_search.text()

        wishlist_enabled = self.acheck_wishlist.isChecked()
        giftlist_enabled = self.acheck_gift_list.isChecked()
        shoppinglist_enabled = self.acheck_shopping_list.isChecked()
        wedding_list_enabled = self.acheck_wedding_list.isChecked()
        ranking_enabled = self.acheck_gift_ranking.isChecked()

        signin_mode = self.acheck_signin_mode.isChecked()

        click_image_mode = self.acheck_click_image_mode.isChecked()



        progress_label = self.progressa_label
        progress = self.progressa

        total_count = int(textboxValue_amazon_loop_one)
        progress_label.setText("Current status: 0 / {}".format(total_count))
        progress.setMaximum(total_count)

        start_page = self.textbox_amazon_start_page_search.text()
        end_page = self.textbox_amazon_end_page_search.text()

        if start_page == '':
            start_page = 1
        else:
            start_page = int(start_page)

        if end_page == '':
            end_page = 400
        else:
            end_page = int(end_page)


        #if signin_mode:
        #   signin_accounts_iter = iter(signin_accounts)

        try:
            i = 0
            while 1:
                if i <= int(textboxValue_amazon_loop_one):
                    i = i + 1
                    print(f'[Instance {threadIndex}]:====================================================')
                    progress_label.setText("Current status: {} / {}".format(i, total_count))
                    progress.setValue(i)
                    proxy_address = random.choice(textboxValue_username_events_one)
                    random_sleep = random.randint(int(textboxValue_break_first_one), int(textboxValue_break_second_one))

                    if signin_mode:

                        try:
                            credential = signin_accounts.pop() 
                        except IndexError:
                            print(f'[Instance {threadIndex}]: Error: Ran out of sign in accounts')
                            return

                    #print(random_sleep)
                    ###############################################################
                    """
                    mproxy = proxy_address
                    proxy_host, proxy_port = mproxy.split(':')
                    driver_pref = webdriver.FirefoxProfile()
                    driver_pref.set_preference('network.proxy.type', 1)
                    driver_pref.set_preference('network.proxy.http', proxy_host)
                    driver_pref.set_preference('network.proxy.http_port', int(proxy_port))
                    driver_pref.set_preference('network.proxy.ssl', proxy_host)
                    driver_pref.set_preference('network.proxy.ssl_port', int(proxy_port))
                    driver_pref.update_preferences()
                    browser = webdriver.Firefox(firefox_profile=driver_pref)
                    ###################################################################
                    """
                    project_dir = os.path.dirname(__file__)
                    chromedriver_path = os.path.join(project_dir, 'chromedriver.exe')
                    chrome_options = webdriver.ChromeOptions()
                    chrome_options.add_argument('log-level=3')
                    #chrome_options.add_argument('--headless')
                    chrome_options.add_argument('--proxy-server=http://%s' % proxy_address)
                    browser = webdriver.Chrome(chromedriver_path, chrome_options=chrome_options)
                    
                    #########################################################################==
                    #name = get_random_name()
                    #browser.get('https://www.amazon.com/')

                    try:
                        if signin_mode:
                            print(f'Signing with credential: {credential}')
                            username, password = credential.split(':')
                            res = sign_in(browser, username, password, threadNum)
                            if not res:
                                continue
                        else:
                            # Sign in securely
                            res = register_all(proxy_address, browser,threadNum)
                            if not res:
                                continue
                        
                    except Exception as ex:
                        print(f'[Instance {threadIndex}]:Exception (in account creation): {ex}')
                        browser.quit()
                        continue
                    print(f'[Instance {threadIndex}]: In account ')
                    #+########################
                    ### CREATE LISTS ########
                    ####################@######
                    
                    
                    if wedding_list_enabled:
                        print(f'[Instance {threadIndex}]:Wedding list enabled: Starting.')
                        create_wedding_list(browser, threadNum)
                        print(f'[Instance {threadIndex}]:Done creating wedding list. Adding..')
                    """
                    if wishlist_enabled:
                        print(f'[Instance {threadIndex}]:Wish list enabled: Starting ..')
                        create_wish_list(browser)
                        print(f'[Instance {threadIndex}]:Done creating wish list')

                    if shoppinglist_enabled:
                        print(f'[Instance {threadIndex}]:Shopping list enabled: Starting ..')
                        create_shopping_list(browser)
                        print(f'[Instance {threadIndex}]:Done creating shopping list')
                    """
                    print(f'Starting search ..')

                    browser.find_element_by_id('twotabsearchtextbox').send_keys(textboxValue_keyword_to_search_one)
                    search_button = browser.find_element_by_class_name('nav-input')
                    browser.execute_script('arguments[0].click();', search_button)

                    time.sleep(1)

                    main_page_url = browser.current_url
                    print(f'[Instance {threadIndex}]:Main Page URL: {main_page_url}')
                    first_page = True
                    store_found = False
                    if start_page > 1:
                        start_page -= 1
                    print(f'[Instance {threadIndex}]:starting from page {start_page} to {end_page}')
                    for idx, pg in enumerate(itertools.cycle(range(start_page, end_page+1))):
                        # only start over the loop once .. stop on the second start over
                        if (idx//end_page) == 2:
                            break

                        if store_found:
                            break

                        if pg > 0:
                            main_page_url = PHONE_AND_ACCESORIES

                        if first_page:
                            print(f'[Instance {threadIndex}]:On first page, moving on!.')
                        else:
                            print(f'[Instance {threadIndex}]:Moving on to page: {pg}')
                            browser.get(main_page_url + '&page=' + str(pg))

                        

                        soup = BeautifulSoup(browser.page_source, 'lxml')
                        print(f'[Instance {threadIndex}]:Looking through products on page.')
                        for a in soup.find_all('a', attrs={'class': 's-access-detail-page'}):
                            products_from_store = a['href']
                            if textboxValue_amazon_asin_one in products_from_store:
                                store_found = True
                                print(f'[Instance {threadIndex}]:Found own product URL: {products_from_store}')
                                try:
                                    print(f'[Instance {threadIndex}]:Visiting product store. ..')
                                    browser.get(products_from_store)
                                except Exception as ex:
                                    print(f'[Instance {threadIndex}]:Exception: {ex}')
                                    print(f'[Instance {threadIndex}]:Visiting product store (Method 2) . ..')
                                    browser.get('https://www.amazon.com' + products_from_store)

                                print(f'[Instance {threadIndex}]:Done.')
                                time.sleep(1)
                                ##############################
                                # check the check boxes enabled.
                                ##############################
                                if click_image_mode:
                                    click_images(browser)

                                if giftlist_enabled:
                                    print(f'[Instance {threadIndex}]:Add to cart enabled, adding.')
                                    #print('No gift list implemented yet. will be converted to cart.')
                                    
                                    try:
                                        print(f'[Instance {threadIndex}]:Visiting product store. ..')
                                        browser.get(products_from_store)
                                    except Exception as ex:
                                        print(f'[Instance {threadIndex}]:Exception: {ex}')
                                        print(f'[Instance {threadIndex}]:Visiting product store (Method 2) . ..')
                                        browser.get('https://www.amazon.com' + products_from_store)
                                        
                                    try:
                                        time.sleep(2)
                                        cart = browser.find_element_by_name('submit.add-to-cart')
                                        browser.execute_script('arguments[0].click();', cart)
                                        print(f'[Instance {threadIndex}]:Added to cart!')
                                        time.sleep(2)
                                    except Exception as ex:
                                        print(f'[Instance {threadIndex}]:Exception (While adding cart): {ex}')

                                if shoppinglist_enabled:
                                    print(f'[Instance {threadIndex}]:shopping list enabled: Starting.')
                                    try:
                                        try:
                                            print(f'[Instance {threadIndex}]:Visiting product store. ..')
                                            browser.get(products_from_store)
                                        except Exception as ex:
                                            print(f'[Instance {threadIndex}]:Exception: {ex}')
                                            print(f'[Instance {threadIndex}]:Visiting product store (Method 2) . ..')
                                            browser.get('https://www.amazon.com' + products_from_store)
                                        #wishlist = browser.find_element_by_id('add-to-wishlist-button-submit')
                                        #browser.execute_script('arguments[0].click();', wishlist)
                                        #time.sleep(5)
                                        print(f'[Instance {threadIndex}]:Adding shopping list ..')
                                        create_shopping_list(browser)
                                        time.sleep(2)
                                        try:
                                            browser.find_element_by_xpath('//*[@id="wl-huc-post-create-msg"]/div/div[2]/span[2]/span/span/button').click()
                                        except Exception:
                                            print(f'[Instance {threadIndex}]:No button to escape.')
                                        print(f'[Instance {threadIndex}]:Added to shopping list')
                                    except Exception as ex:
                                        print(f'[Instance {threadIndex}]:Exception (While adding shopping list): {ex}')
                                        print(f'[Instance {threadIndex}]:No wishlist button')


                               
                                if wishlist_enabled:

                                    print(f'[Instance {threadIndex}]:Wishlist enabled, starting to add.')
                                    try:
                                        
                                        print(f'[Instance {threadIndex}]:Wish list enabled: Starting ..')
                                        create_wish_list(browser)
                                        print(f'[Instance {threadIndex}]:Done creating wish list')

                                        #wishlist = browser.find_element_by_id('add-to-wishlist-button-submit')
                                        #browser.execute_script('arguments[0].click();', wishlist)
                                        #time.sleep(5)
                                        try:
                                            browser.find_element_by_xpath('//*[@id="wl-huc-post-create-msg"]/div/div[2]/span[2]/span/span/button').click()
                                        except Exception:
                                            print(f'[Instance {threadIndex}]:No button to escape.')

                                        print(f'[Instance {threadIndex}]:Added to Wishlist')
                                    except NoSuchElementException as ex:
                                        print(f'[Instance {threadIndex}]:Exception: (during wishlist addition) => {ex}')
                                        print(f'[Instance {threadIndex}]:No wishlist button')

                                if wedding_list_enabled:
                                    print(f'[Instance {threadIndex}]:Wedding list enabled starting ..')
                                    time.sleep(5)
                                    try:
                                        try:
                                            browser.get(products_from_store)
                                        except Exception:
                                            browser.get('https://www.amazon.com' + products_from_store)

                                        wedding_list = browser.find_element_by_id('add-to-registry-wedding-button')
                                        browser.execute_script('arguments[0].click();', wedding_list)
                                        time.sleep(2)

                                        try:
                                            webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()
                                        except Exception as ex:
                                            print(f'[Instance {threadIndex}]:Could not use escape key for pop up ')

                                        print(f'[Instance {threadIndex}]:Added to Wedding list')
                                    except Exception as ex:
                                        print(f'[Instance {threadIndex}]:Exception (While adding wedding list): {ex}')

                                
                               

                                if ranking_enabled:
                                    print(f'[Instance {threadIndex}]:Ranking Enabled: Starting ..')
                                    soup = BeautifulSoup(browser.page_source, 'lxml')
                                    all_reviews = soup.find('div', attrs={'class': 'a-row a-spacing-large'}).find('a')['href']
                                    print(all_reviews)
                                    browser.get('https://www.amazon.com' + all_reviews)
                                    time.sleep(10)
                                    soup = BeautifulSoup(browser.page_source, 'lxml')
                                    a = soup.find_all('a', attrs={'id': 'a-autoid-8-announce'})
                                    print(len(a))
                                    b = i
                                    for i, an in enumerate(a):
                                        if i == b:
                                            print(an['href'])
                                            browser.get(an['href'])
                                    if b == len(a):
                                        if soup.find('li', attrs={'class': 'a-last'}):
                                            try:
                                                if soup.find('li', attrs={'class': 'a-last'}):
                                                    for i, an in enumerate(a):
                                                        if i == b:
                                                            browser.get(an['href'])
                                                        else:
                                                            for i, an in enumerate(a['href']):
                                                                if i == b:
                                                                    browser.get(an)
                                                    c = soup.find('li', attrs={'class': 'a-last'}).find('a')['href']
                                                    browser.get('https://www.amazon.com' + c)
                                            except:
                                                print(f'[Instance {threadIndex}]:no next button')

                                print(f'[Instance {threadIndex}]:sleeping for ' + str(random_sleep) + ' and quitting')
                                webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()
                                time.sleep(random_sleep)
                                print(f'[Instance {threadIndex}]:Quiting browser')
                                time.sleep(10)
                                browser.quit()
                                if first_page:
                                    print(f'[Instance {threadIndex}]:Your Product is on Page 1 already, Program will not rank anymore.')
                                break
                        # we are no more on first page.
                        first_page = False
                    # update the window
                    QGuiApplication.processEvents()
                    print('All page transversed!.')
                    browser.quit()    

        except Exception as ex:
            print(f'[Instance {threadIndex}]:Exception occur in main loop for tab 1: {ex}')
            
    def future_for_tab_1(self):
        textboxValue_instance_count_tab1 = self.textbox_instance_count_tab1.text()
        print(f'Launching {textboxValue_instance_count_tab1} instances..')
        futures = []
        with ThreadPoolExecutor(max_workers=float(textboxValue_instance_count_tab1)) as ex:
                i = 0
                while i < int(textboxValue_instance_count_tab1):
                    futures.append(ex.submit(self.add_from_groups, i+1))
                    i = i+1

        for future in futures:
            future.result()

    ###############################################################
    #   END OF TAB 1.
    ################################################################

    @pyqtSlot()
    def on_click_add_from_events(self, threadNum):
        threadIndex = threadNum
        textboxValue_username_events = self.textbox_username_events.toPlainText().split('\n')
        textboxValue_username_add_from_events = self.textbox_username_add_from_events.text()
        textboxValue_amazon_asin = self.textbox_amazon_asin.text()
        textboxValue_amazon_loop = self.textbox_amazon_loop.text()
        textboxValue_break_first = self.textbox_amazon_break_first.text()
        textboxValue_break_second = self.textbox_amazon_break_second.text()
        textboxValue_keyword_to_search = self.textbox_keyword_to_search.text()
        wishlist_enabled = self.bcheck_wishlist.isChecked()
        giftlist_enabled = self.bcheck_gift_list.isChecked()
        shoppinglist_enabled = self.bcheck_shopping_list.isChecked()
        wedding_list_enabled = self.bcheck_wedding_list.isChecked()
        ranking_enabled = self.bcheck_gift_ranking.isChecked()

        click_image_mode = self.bcheck_click_image_mode.isChecked()


        signin_mode = self.bcheck_signin_mode.isChecked()


        progress_label = self.progressb_label
        progress = self.progressb

        total_count = int(textboxValue_amazon_loop)
        progress_label.setText("Current status: 0 / {}".format(total_count))
        progress.setMaximum(total_count)

        #if signin_mode:
        #   signin_accounts_iter = iter(signin_accounts)
    
        try:
            i = 0
            while 1:
                if i <= int(textboxValue_amazon_loop):
                    i = i + 1
                    print(f'[Instance {threadIndex}]:====================================================')

                    progress_label.setText("Current status: {} / {}".format(i, total_count))
                    progress.setValue(i)
                    proxy_address = random.choice(textboxValue_username_events)
                    random_sleep = random.randint(int(textboxValue_break_first), int(textboxValue_break_second))
                    print(random_sleep)

                    if signin_mode:

                        try:
                            credential = signin_accounts.pop() 
                        except IndexError:
                            print(f'[Instance {threadIndex}]: Error: Ran out of sign in accounts')
                            return
                    ########################################3
                    """
                    mproxy = proxy_address
                    proxy_host, proxy_port = mproxy.split(':')
                    driver_pref = webdriver.FirefoxProfile()
                    driver_pref.set_preference('network.proxy.type', 1)
                    driver_pref.set_preference('network.proxy.http', proxy_host)
                    driver_pref.set_preference('network.proxy.http_port', int(proxy_port))
                    driver_pref.set_preference('network.proxy.ssl', proxy_host)
                    driver_pref.set_preference('network.proxy.ssl_port', int(proxy_port))
                    driver_pref.update_preferences()
                    browser = webdriver.Firefox(firefox_profile=driver_pref)
                    """

                    ###################################################################
                    project_dir = os.path.dirname(__file__)
                    chromedriver_path = os.path.join(project_dir, 'chromedriver.exe')
                    chrome_options = webdriver.ChromeOptions()
                    chrome_options.add_argument('log-level=3')
                    #chrome_options.add_argument('--headless')
                    chrome_options.add_argument('--proxy-server=http://%s' % proxy_address)
                    browser = webdriver.Chrome(chromedriver_path, chrome_options=chrome_options)
                    
                    #########################################################################==

                    ###################################################################
                    ### REGISTER SITE
                    #####################################################3


                    try:
                        if signin_mode:
                            print(f'Signing with credential: {credential}')
                            username, password = credential.split(':')
                            res = sign_in(browser, username, password, threadNum)
                            if not res:
                                continue
                        else:
                            # Sign in securely
                            res = register_all(proxy_address, browser,threadNum)
                            if not res:
                                continue
                    except Exception as ex:
                        print(f'[Instance {threadIndex}]:Exception (in account creation): {ex}')
                        browser.quit()
                        continue

                    #+########################
                    ### CREATE LISTS ########
                    ####################@######
                    if wedding_list_enabled:
                        print(f'[Instance {threadIndex}]:Wedding list enabled: Starting.')
                        create_wedding_list(browser, threadNum)
                        print(f'[Instance {threadIndex}]:Done creating wedding list. Adding..')
                    """

                    if wishlist_enabled:
                        print(f'[Instance {threadIndex}]:Wish list enabled: Starting ..')
                        create_wish_list(browser)
                        print(f'[Instance {threadIndex}]:Done creating wish list')

                    if shoppinglist_enabled:
                        print(f'[Instance {threadIndex}]:Shopping list enabled: Starting ..')
                        create_shopping_list(browser)
                        print(f'[Instance {threadIndex}]:Done creating shopping list')
                    """

                    browser.get(textboxValue_username_add_from_events)
                    browser.find_element_by_id('twotabsearchtextbox').send_keys(textboxValue_keyword_to_search)
                    browser.find_element_by_class_name('nav-input').click()
                    time.sleep(1)

                    soup = BeautifulSoup(browser.page_source, 'lxml')
                    for a in soup.find_all('a', href=True):
                        products_from_store = a['href']
                        try:
                            products_from_store = products_from_store.split('#')[0]
                        except Exception:
                            pass

                        if textboxValue_amazon_asin in products_from_store:
                            try:
                                print('Visiting product store ..')
                                browser.get(products_from_store)
                            except Exception:
                                browser.get('https://www.amazon.com' + products_from_store)

                            ##############################
                            # check the check boxes enabled.
                            ##############################
                            if click_image_mode:
                                click_images(browser)

                            if giftlist_enabled:
                                print(f'[Instance {threadIndex}]:Add to cart enabled, starting.')
                                #print('No gift list implemented yet. will be converted to cart.')
                                try:
                                    cart = browser.find_element_by_name('submit.add-to-cart')
                                    browser.execute_script('arguments[0].click();', cart)
                                    print(f'[Instance {threadIndex}]:Added to cart!')
                                    time.sleep(2)
                                except Exception as ex:
                                    print(f'[Instance {threadIndex}]:Exception (While adding cart): {ex}')


                           

                            if wedding_list_enabled:
                                try:
                                    try:
                                        browser.get(products_from_store)
                                    except Exception:
                                        browser.get('https://www.amazon.com' + products_from_store)

                                    wedding_list = browser.find_element_by_id('add-to-registry-wedding-button')
                                    browser.execute_script('arguments[0].click();', wedding_list)
                                    time.sleep(2)

                                    try:
                                        webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()
                                    except Exception as ex:
                                        print(f'[Instance {threadIndex}]:Could not use escape key for pop up ')

                                    print(f'[Instance {threadIndex}]:Added to Wedding list')
                                except Exception as ex:
                                    print(f'[Instance {threadIndex}]:Exception (While adding wedding list): {ex}')

                            if shoppinglist_enabled:
                                print(f'[Instance {threadIndex}]:Wedding list enabled: Starting.')
                                try:
                                    try:
                                        print(f'[Instance {threadIndex}]:Visiting product store. ..')
                                        browser.get(products_from_store)
                                    except Exception as ex:
                                        print(f'[Instance {threadIndex}]:Exception: {ex}')
                                        print(f'[Instance {threadIndex}]:Visiting product store (Method 2) . ..')
                                        browser.get('https://www.amazon.com' + products_from_store)

                                    print(f'[Instance {threadIndex}]:Adding wish list ..')
                                    create_shopping_list(browser)
                                    time.sleep(3)

                                    #browser.get(products_from_store)
                                    # click add list
                                    #wishlist = browser.find_element_by_id('add-to-wishlist-button-submit')
                                    # browser.execute_script('arguments[0].click();', wishlist)
                                    #time.sleep(5)
                                    # escape the pop up box.
                                    browser.find_element_by_xpath('//*[@id="wl-huc-post-create-msg"]/div/div[2]/span[2]/span/span/button').click()
                                    print(f'[Instance {threadIndex}]:Added to shopping list')
                                except Exception as ex:
                                    print(f'[Instance {threadIndex}]:Exception (While adding shopping list): {ex}')
                                    print(f'[Instance {threadIndex}]:No wishlist button')

                            if wishlist_enabled:
                                print(f'[Instance {threadIndex}]:Wishlist enabled, starting to add.')
                                try:
                                    print(f'[Instance {threadIndex}]:Adding wish list ..')
                                    create_wish_list(browser)
                                    time.sleep(3)
                                    try:
                                        browser.find_element_by_xpath('//*[@id="wl-huc-post-create-msg"]/div/div[2]/span[2]/span/span/button').click()
                                    except Exception:
                                        print(f'[Instance {threadIndex}]:No button to escape.')

                                    print(f'[Instance {threadIndex}]:Added to Wishlist')
                                except NoSuchElementException as ex:
                                    print(f'[Instance {threadIndex}]:Exception: (during wishlist addition) => {ex}')
                                    print(f'[Instance {threadIndex}]:No wishlist button')

                            if ranking_enabled:
                                print(f'[Instance {threadIndex}]:Ranking Enabled: Starting ..')
                                soup = BeautifulSoup(browser.page_source, 'lxml')
                                all_reviews = soup.find('div', attrs={'class': 'a-row a-spacing-large'}).find('a')['href']
                                print(all_reviews)
                                browser.get('https://www.amazon.com' + all_reviews)
                                time.sleep(10)
                                soup = BeautifulSoup(browser.page_source, 'lxml')
                                a = soup.find_all('a', attrs={'id': 'a-autoid-8-announce'})
                                print(len(a))
                                b = i
                                for i, an in enumerate(a):
                                    if i == b:
                                        print(an['href'])
                                        browser.get(an['href'])
                                if b == len(a):
                                    if soup.find('li', attrs={'class': 'a-last'}):
                                        try:
                                            if soup.find('li', attrs={'class': 'a-last'}):
                                                for i, an in enumerate(a):
                                                    if i == b:
                                                        browser.get(an['href'])
                                                    else:
                                                        for i, an in enumerate(a['href']):
                                                            if i == b:
                                                                browser.get(an)
                                                c = soup.find('li', attrs={'class': 'a-last'}).find('a')['href']
                                                browser.get('https://www.amazon.com' + c)
                                        except:
                                            print(f'[Instance {threadIndex}]:no next button')

                            print(f'[Instance {threadIndex}]:Sleeping for ' + str(random_sleep) + ' and quitting')
                            time.sleep(random_sleep)
                            browser.quit()
                            break
                        else:
                            print(f'[Instance {threadIndex}]:didnt find your ASIN number, check if it is correct: ' + textboxValue_amazon_asin)
                    QGuiApplication.processEvents()
                    continue
        except Exception as ex:
            print(f'[Instance {threadIndex}]:Exception occur in main loop for tab 2: {ex}')


    def future_for_tab_2(self):
        textboxValue_instance_count_tab2 = self.textbox_instance_count_tab2.text()
        print(f'Launching {textboxValue_instance_count_tab2} instances..')
        futures = []
        with ThreadPoolExecutor(max_workers=float(textboxValue_instance_count_tab2)) as ex:
                i = 0
                while i < int(textboxValue_instance_count_tab2):
                    futures.append(ex.submit(self.on_click_add_from_events, i+1))
                    i = i+1

        for future in futures:
            future.result()
            

    def click_ads(self):
        textboxValue_proxies_adclicker = self.textbox_proxy_adclicker.text().split(',')
        textboxValue_amazon_asin_adclicker = self.textbox_asin_adclicker.text()
        textboxValue_amazon_loop_adclicker = self.textbox_loop_adclicker.text()
        textboxValue_break_first_adclicker = self.textbox_break_first_adclicker.text()
        textboxValue_break_second_adclicker = self.textbox_break_second_adclicker.text()
        textboxValue_keyword_adclicker = self.textbox_keyword_adclicker.text()
        try:
            i = 0
            while 1:
                if i <= int(textboxValue_amazon_loop_adclicker):
                    i = i + 1
                    proxy_address = random.choice(textboxValue_proxies_adclicker)
                    random_sleep = random.randint(int(textboxValue_break_first_adclicker),
                                                  int(textboxValue_break_second_adclicker))
                    print(random_sleep)
                    project_dir = os.path.dirname(__file__)
                    chromedriver_path = os.path.join(project_dir, 'chromedriver.exe')
                    chrome_options = webdriver.ChromeOptions()
                    chrome_options.add_argument('log-level=3')
                    #chrome_options.add_argument('--headless')
                    chrome_options.add_argument('--proxy-server=http://%s' % proxy_address)
                    browser = webdriver.Chrome(chromedriver_path, chrome_options=chrome_options)
                    browser.get('https://www.amazon.com/')
                    try:
                        browser.find_element_by_id('twotabsearchtextbox').send_keys(textboxValue_keyword_adclicker)
                    except Exception:
                        print('Possibly met an error, qutting and starting over')
                        browser.quit()
                        continue

                    browser.find_element_by_class_name('nav-input').click()
                    print('Looking for ads...')
                    time.sleep(5)
                    elems = browser.find_elements_by_xpath('//a[@href]')
                    for elem in elems:
                        if textboxValue_amazon_asin_adclicker in elem.get_attribute('href'):
                            browser.get(elem.get_attribute('href'))
                            print('Ad Succesfully Clicked!')
                            browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                            print('Sleeping for ' + str(random_sleep) + ' seconds and Quitting')
                            time.sleep(random_sleep)
                            browser.quit()
                            break
                    else:
                        print('Ad is not found, please check your ASIN KEY')
                        browser.quit()
                        break

        except Exception as e:
            print(e)

    def rank_by_category(self, threadNum):
        index = threadNum
        threadIndex = threadNum
        textboxValue_proxies_categories = self.textbox_proxy_categories.toPlainText().split('\n')
        textboxValue_amazon_asin_categories = self.textbox_asin_categories.text()
        textboxValue_amazon_loop_categories = self.textbox_loop_categories.text()
        textboxValue_break_first_categories = self.textbox_break_first_categories.text()
        textboxValue_break_second_categories = self.textbox_break_second_categories.text()
        textboxValue_keyword_categories = self.textbox_keyword_categories.text()
        textboxValue_category_url = self.textbox_category_url.text()
        textboxValue_product_url = self.textbox_product_url.toPlainText()
        wishlist_enabled = self.check_wishlist.isChecked()
        giftlist_enabled = self.check_gift_list.isChecked()
        shoppinglist_enabled = self.check_shopping_list.isChecked()
        wedding_list_enabled = self.check_wedding_list.isChecked()
        ranking_enabled = self.check_ranking.isChecked()

        click_image_mode = self.ccheck_click_image_mode.isChecked()


        signin_mode = self.ccheck_signin_mode.isChecked()

        progress_label = self.progress_label
        progress = self.progress

        total_count = int(textboxValue_amazon_loop_categories)
        progress_label.setText("Current status: 0 / {}".format(total_count))
        progress.setMaximum(total_count)

        #if signin_mode:
        #   signin_accounts_iter = iter(signin_accounts)

        for i in range(1, int(textboxValue_amazon_loop_categories)):
            print(f'[Instance {index}]:====================================================')
            progress_label.setText("Current status: {} / {}".format(i, total_count))
            progress.setValue(i)

            proxy_address = random.choice(textboxValue_proxies_categories)
            random_sleep = random.randint(int(textboxValue_break_first_categories),
                                          int(textboxValue_break_second_categories))

            if signin_mode:
                try:
                    credential = signin_accounts.pop() 
                except IndexError:
                    print(f'[Instance {threadIndex}]: Error: Ran out of sign in accounts')
                    return
            """
            mproxy = proxy_address
            proxy_host, proxy_port = mproxy.split(':')
            driver_pref = webdriver.FirefoxProfile()
            driver_pref.set_preference('network.proxy.type', 1)
            driver_pref.set_preference('network.proxy.http', proxy_host)
            driver_pref.set_preference('network.proxy.http_port', int(proxy_port))
            driver_pref.set_preference('network.proxy.ssl', proxy_host)
            driver_pref.set_preference('network.proxy.ssl_port', int(proxy_port))
            driver_pref.update_preferences()
            browser = webdriver.Firefox(firefox_profile=driver_pref)
            """

            ###################################################################
                    
            project_dir = os.path.dirname(__file__)
            chromedriver_path = os.path.join(project_dir, 'chromedriver.exe')
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('log-level=3')
            #chrome_options.add_argument('--headless')
            chrome_options.add_argument('--proxy-server=http://%s' % proxy_address)
            browser = webdriver.Chrome(chromedriver_path, chrome_options=chrome_options)
            #########################################################################==

            ################################################################### 
           
            #name = get_random_name()
            try:
                ###################################################################
                ### REGISTER SITE
                #####################################################3


                try:
                    if signin_mode:
                        print(f'Signing with credential: {credential}')
                        username, password = credential.split(':')
                        res = sign_in(browser, username, password, threadNum)
                        if not res:
                            continue
                    else:
                        # Sign in securely
                        res = register_all(proxy_address, browser,threadNum)
                        if not res:
                            continue
                except Exception as ex:
                    print(f'[Instance {index}]:Exception (in account creation): {ex}')
                    browser.quit()
                    continue

                #+########################
                ### CREATE LISTS ########
                ####################@######
                if wedding_list_enabled:
                    print(f'[Instance {index}]:Wedding list enabled: Starting.')
                    create_wedding_list(browser, threadNum)
                    print(f'[Instance {index}]:Done creating wedding list. Adding..')
                """

                if wishlist_enabled:
                    print(f'[Instance {index}]:Wish list enabled: Starting ..')
                    create_wish_list(browser)
                    print(f'[Instance {index}]:Done creating wish list')

                if shoppinglist_enabled:
                    print(f'[Instance {index}]:Shopping list enabled: Starting ..')
                    create_shopping_list(browser)
                    print(f'[Instance {index}]:Done creating shopping list')
                """
                #####################################################3


                for product in textboxValue_product_url.split("\n"):
                    try:
                        print(f'[Instance {index}]:Visiting store: {product}')
                        browser.get(product)

                        ##############################
                        # check the check boxes enabled.
                        ##############################
                        if click_image_mode:
                            click_images(browser)

                        if giftlist_enabled:
                            print(f'[Instance {index}]:Add to cart enabled, starting.')
                            #print('No gift list implemented yet. will be converted to cart.')
                            try:
                                cart = browser.find_element_by_name('submit.add-to-cart')
                                browser.execute_script('arguments[0].click();', cart)
                                print('[Instance {index}]:Added to cart!')
                                time.sleep(2)
                            except Exception as ex:
                                print(f'[Instance {index}]:Exception (While adding cart): {ex}')


                        
                        if wedding_list_enabled:
                            try:
                                try:
                                    browser.get(product)
                                except Exception:
                                    browser.get('https://www.amazon.com' + product)
                                # CLICK THE WEDDING BUTTON.
                                wedding_list = browser.find_element_by_id('add-to-registry-wedding-button')
                                browser.execute_script('arguments[0].click();', wedding_list)
                                time.sleep(2)

                                try:
                                    webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()
                                except Exception as ex:
                                    print(f'[Instance {index}]:Could not use escape key for pop up ')

                                print(f'[Instance {index}]:Added to Wedding list')
                            except Exception as ex:
                                print(f'[Instance {index}]:Exception (While adding wedding list): {ex}')

                        if shoppinglist_enabled:
                            print(f'[Instance {index}]:shopping list enabled: Starting.')
                            try:
                                browser.get(product)

                                print(f'[Instance {threadIndex}]:Adding shopping list ..')
                                create_shopping_list(browser)
                                time.sleep(3)
                                print(f'[Instance {index}]:Added to shopping list')
                            except Exception as ex:
                                print(f'[Instance {index}]:Exception (While adding shopping list): {ex}')
                                print(f'[Instance {index}]:No wishlist button')

                        if wishlist_enabled:
                            print(f'[Instance {index}]:Wishlist enabled, starting.')
                            try:
                                print(f'[Instance {threadIndex}]:Adding wish list ..')
                                create_wish_list(browser)
                                time.sleep(3)
                                print(f'[Instance {index}]:Added to Wishlist')
                            except NoSuchElementException as ex:
                                print(f'[Instance {index}]:Exception: (during wishlist addition) => {ex}')


                        if ranking_enabled:
                            #print('Ranking enabled. Starting.... (Not implemented.)')
                            pass
                           
                
                    except Exception as ex:
                        print(f'[Instance {index}]:Exception occured in inner main while processing product: {ex}')
                
                # we are done.
                print(f'[Instance {index}]:Quiting browser ... ')
                time.sleep(5)
                browser.quit()       

            except Exception as ex:
                print(f'[Instance {index}]:Exception occured in main loop: {ex}')

            browser.quit()
            QGuiApplication.processEvents()

    def future_for_tab_4(self):
        textboxValue_instance_count = self.textbox_instance_count.text()
        print(f'Launching {textboxValue_instance_count} instances..')
        futures = []
        with ThreadPoolExecutor(max_workers=float(textboxValue_instance_count)) as ex:
                i = 0
                while i < int(textboxValue_instance_count):
                    futures.append(ex.submit(self.rank_by_category, i+1))
                    i = i+1

        for future in futures:
            future.result()


    def click_ads_no_proxy(self):
        textboxValue_amazon_asin_adclicker_no_proxy = self.textbox_asin_adclicker_no_proxy.text()
        textboxValue_amazon_loop_adclicker_no_proxy = self.textbox_loop_adclicker_no_proxy.text()
        textboxValue_break_first_adclicker_no_proxy = self.textbox_break_first_adclicker_no_proxy.text()
        textboxValue_break_second_adclicker_no_proxy = self.textbox_break_second_adclicker_no_proxy.text()
        textboxValue_keyword_adclicker_no_proxy = self.textbox_keyword_adclicker_no_proxy.text()
        print(textboxValue_amazon_asin_adclicker_no_proxy)
        try:
            i = 0
            while 1:
                if i <= int(textboxValue_amazon_loop_adclicker_no_proxy):
                    i = i + 1
                    print('Looking for a valid proxy... Please wait...')
                    print('PROXY FOUND!')
                    random_sleep = random.randint(int(textboxValue_break_first_adclicker_no_proxy),
                                                  int(textboxValue_break_second_adclicker_no_proxy))
                    print(random_sleep)
                    project_dir = os.path.dirname(__file__)
                    chromedriver_path = os.path.join(project_dir, 'chromedriver.exe')
                    chrome_options = webdriver.ChromeOptions()
                    chrome_options.add_argument('log-level=3')
                    #chrome_options.add_argument('--headless')
                    browser = webdriver.Chrome(chromedriver_path, chrome_options=chrome_options)
                    browser.get('https://www.amazon.com/')
                    try:
                        browser.find_element_by_id('twotabsearchtextbox').send_keys(
                            textboxValue_keyword_adclicker_no_proxy)
                    except Exception:
                        print('Possibly met an error, qutting and starting over')
                        browser.quit()
                        continue

                    browser.find_element_by_class_name('nav-input').click()
                    print('Looking for ads...')
                    time.sleep(5)
                    elems = browser.find_elements_by_xpath('//a[@href]')
                    for elem in elems:
                        if textboxValue_amazon_asin_adclicker_no_proxy in elem.get_attribute('href'):
                            browser.get(elem.get_attribute('href'))
                            print('Ad Succesfully Clicked!')
                            browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                            print('Sleeping for ' + str(random_sleep) + ' seconds and Quitting')
                            time.sleep(random_sleep)
                            browser.quit()
                            break
                    else:
                        print('Ad is not found, please check your ASIN KEY')
                        browser.quit()
                        break

        except Exception as e:
            print(e)

    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab4 = QWidget()
        self.tab5 = QWidget()
        self.tabs.resize(300, 200)
        self.tabs.addTab(self.tab1, 'Rank from Search')
        self.tabs.addTab(self.tab2, 'Rank by STORE URL')
        self.tabs.addTab(self.tab3, 'Ad-Clicker')
        self.tabs.addTab(self.tab4, 'Rank by Category/URL')
        self.tabs.addTab(self.tab5, 'Ad-Clicker-public-proxy')
        self.tab1.layout = QVBoxLayout(self)
        label = QLabel('Proxies:Ports', self.tab1)
        label.move(130, 40)
        label.resize(200, 20)

        

        ###
        # progress bar 
        #####
        self.progressa = QProgressBar(self.tab1)
        self.progressa.setGeometry(200, 20, 500, 20)
        self.progressa_label = QLabel('STATUS: Click on start to start processing', self.tab1)
        self.progressa_label.setGeometry(320, 42, 500, 20)
        #############################################3
        
        self.textbox_username_events_search = QTextEdit(self.tab1)
        self.textbox_username_events_search.setText("\n".join(proxy_list))
        self.textbox_username_events_search.move(130, 80)
        self.textbox_username_events_search.resize(280, 80)
         #############################################3

        #############################################3
        label = QLabel('Usernames:Password', self.tab1)
        label.move(630, 50)
        label.resize(200, 20)


        self.atextbox_signin_accounts = QTextEdit(self.tab1)
        self.atextbox_signin_accounts.setText("\n".join(signin_accounts))
        self.atextbox_signin_accounts.move(430, 80)
        self.atextbox_signin_accounts.resize(280, 80)
         #############################################3
        #
        
        label = QLabel('Starting Page:', self.tab1)
        label.move(130, 200)
        label.resize(200, 20)
        self.textbox_amazon_start_page_search = QLineEdit(self.tab1)
        self.textbox_amazon_start_page_search.move(240, 200)
        self.textbox_amazon_start_page_search.resize(60, 20)
        #-----------
        label = QLabel('Ending Page:', self.tab1)
        label.move(330, 200)
        label.resize(200, 20)
        self.textbox_amazon_end_page_search = QLineEdit(self.tab1)
        self.textbox_amazon_end_page_search.move(400, 200)
        self.textbox_amazon_end_page_search.resize(60, 20)
        #
        
        ###################################################
        label = QLabel('ASIN key:', self.tab1)
        label.move(130, 250)
        label.resize(200, 20)
        self.textbox_amazon_asin_search = QLineEdit(self.tab1)
        self.textbox_amazon_asin_search.setText('B07M7YG11G')
        self.textbox_amazon_asin_search.move(130, 280)
        self.textbox_amazon_asin_search.resize(280, 20)
        label = QLabel('How many times:', self.tab1)
        label.move(130, 310)
        label.resize(200, 20)
        self.textbox_amazon_loop_search = QLineEdit(self.tab1)
        self.textbox_amazon_loop_search.setText('5000')
        self.textbox_amazon_loop_search.move(130, 340)
        self.textbox_amazon_loop_search.resize(280, 20)
        label = QLabel('Break from:', self.tab1)
        label.move(130, 370)
        label.resize(200, 20)
        self.textbox_amazon_break_first_search = QLineEdit(self.tab1)
        self.textbox_amazon_break_first_search.setText('2')
        self.textbox_amazon_break_first_search.move(130, 400)
        self.textbox_amazon_break_first_search.resize(60, 20)
        label = QLabel('to:', self.tab1)
        label.move(240, 400)
        label.resize(200, 20)
        self.textbox_amazon_break_second_search = QLineEdit(self.tab1)
        self.textbox_amazon_break_second_search.setText('2')
        self.textbox_amazon_break_second_search.move(300, 400)
        self.textbox_amazon_break_second_search.resize(60, 20)
        label = QLabel('Keyword:', self.tab1)
        label.move(130, 430)
        label.resize(200, 20)
        self.textbox_keyword_to_search_search = QLineEdit(self.tab1)
        self.textbox_keyword_to_search_search.setText('iphone x case')
        self.textbox_keyword_to_search_search.move(130, 460)
        self.textbox_keyword_to_search_search.resize(200, 20)
        label = QLabel('Instances:', self.tab1)
        label.move(400, 430)
        label.resize(200, 20)
        self.textbox_instance_count_tab1 = QLineEdit(self.tab1)
        self.textbox_instance_count_tab1.setText('1')
        self.textbox_instance_count_tab1.move(400, 460)
        self.textbox_instance_count_tab1.resize(40, 20)

        self.button = QPushButton('Start Ranking Search', self)
        self.acheck_wishlist = QCheckBox("Add to Wishlist", self.tab1)
        self.acheck_wedding_list = QCheckBox("Add to Wedding List", self.tab1)
        self.acheck_shopping_list = QCheckBox("Add to Shopping List", self.tab1)
        self.acheck_gift_list = QCheckBox("Add to Cart", self.tab1)
        self.acheck_gift_ranking = QCheckBox("Rank Products", self.tab1)
        self.acheck_signin_mode = QCheckBox("Sign in mode.", self.tab1)
        self.acheck_signin_mode.setGeometry(480, 200, 480, 20)

        self.acheck_click_image_mode = QCheckBox("Click Image.", self.tab1)
        self.acheck_click_image_mode.setGeometry(600, 200, 480, 20)

        self.acheck_gift_ranking.setGeometry(400, 300, 480, 20)
        #self.acheck_gift_ranking.setChecked(True)
        self.acheck_gift_list.setGeometry(400, 380, 480, 20)
        self.acheck_gift_list.setChecked(True)
        self.acheck_shopping_list.setGeometry(400, 360, 480, 20)
        #self.acheck_shopping_list.setChecked(True)
        self.acheck_wishlist.setGeometry(400, 340, 500, 20)
        self.acheck_wishlist.setChecked(True)
        self.acheck_wedding_list.setGeometry(400, 320, 500, 20)
        self.acheck_wedding_list.setChecked(True)
        self.button.clicked.connect(self.future_for_tab_1)
        self.tab1.layout.addWidget(self.button, alignment=Qt.AlignBottom)
        self.tab1.setLayout(self.tab1.layout)
        self.tab2.layout = QVBoxLayout(self)
        label = QLabel('Proxies:Ports', self.tab2)
        label.move(130, 40)
        label.resize(200, 20)
        ###################3
        #
        ################33
        self.progressb = QProgressBar(self.tab2)
        self.progressb.setGeometry(200, 20, 500, 20)
        self.progressb_label = QLabel('STATUS: Click on start to start processing', self.tab2)
        self.progressb_label.setGeometry(320, 42, 500, 20)
        ###############
        self.textbox_username_events = QTextEdit(self.tab2)
        self.textbox_username_events.setText("\n".join(proxy_list))
        self.textbox_username_events.move(130, 70)
        self.textbox_username_events.resize(280, 80)
        self.textbox_username_events.resize(280, 80)

        #############################################3
        label = QLabel('Usernames:Password', self.tab2)
        label.move(630, 50)
        label.resize(200, 20)


        self.atextbox_signin_accounts = QTextEdit(self.tab2)
        self.atextbox_signin_accounts.setText("\n".join(signin_accounts))
        self.atextbox_signin_accounts.move(430, 80)
        self.atextbox_signin_accounts.resize(280, 80)
        #############################################3

        label = QLabel('Amazon Store url:', self.tab2)
        label.move(130, 190)
        label.resize(200, 20)
        self.textbox_username_add_from_events = QLineEdit(self.tab2)
        self.textbox_username_add_from_events.setText(AMAZON_STORE)
        self.textbox_username_add_from_events.move(130, 220)
        self.textbox_username_add_from_events.resize(280, 20)
        label = QLabel('ASIN key:', self.tab2)
        label.move(130, 250)
        label.resize(200, 20)
        self.textbox_amazon_asin = QLineEdit(self.tab2)
        self.textbox_amazon_asin.setText('B07L7DR9BW')
        self.textbox_amazon_asin.move(130, 280)
        self.textbox_amazon_asin.resize(280, 20)
        label = QLabel('How many times:', self.tab2)
        label.move(130, 310)
        label.resize(200, 20)
        self.textbox_amazon_loop = QLineEdit(self.tab2)
        self.textbox_amazon_loop.setText('5000')
        self.textbox_amazon_loop.move(130, 340)
        self.textbox_amazon_loop.resize(280, 20)
        label = QLabel('Break from:', self.tab2)
        label.move(130, 370)
        label.resize(200, 20)
        self.textbox_amazon_break_first = QLineEdit(self.tab2)
        self.textbox_amazon_break_first.setText('2')
        self.textbox_amazon_break_first.move(130, 400)
        self.textbox_amazon_break_first.resize(60, 20)
        label = QLabel('to:', self.tab2)
        label.move(240, 400)
        label.resize(200, 20)
        self.textbox_amazon_break_second = QLineEdit(self.tab2)
        self.textbox_amazon_break_second.setText('2')
        self.textbox_amazon_break_second.move(300, 400)
        self.textbox_amazon_break_second.resize(60, 20)

        # +++============================================
        self.bcheck_wishlist = QCheckBox("Add to Wishlist", self.tab2)
        self.bcheck_wedding_list = QCheckBox("Add to Wedding List", self.tab2)
        self.bcheck_shopping_list = QCheckBox("Add to Shopping List", self.tab2)
        self.bcheck_gift_list = QCheckBox("Add to Cart", self.tab2)
        self.bcheck_gift_ranking = QCheckBox("Rank Products", self.tab2)
        self.bcheck_signin_mode = QCheckBox("Sign in mode.", self.tab2)
        self.bcheck_signin_mode.setGeometry(400, 200, 480, 20)

        self.bcheck_click_image_mode = QCheckBox("Click Image.", self.tab2)
        self.bcheck_click_image_mode.setGeometry(600, 200, 480, 20)

        self.bcheck_gift_ranking.setGeometry(400, 300, 480, 20)
        self.bcheck_gift_list.setGeometry(400, 380, 480, 20)
        self.bcheck_shopping_list.setGeometry(400, 360, 480, 20)
        self.bcheck_wishlist.setGeometry(400, 340, 500, 20)
        self.bcheck_wedding_list.setGeometry(400, 320, 500, 20)
        #++++++++++++++++++++++++++++++++++++++++++++++++
        label = QLabel('Keyword:', self.tab2)
        label.move(130, 430)
        label.resize(200, 20)
        self.textbox_keyword_to_search = QLineEdit(self.tab2)
        self.textbox_keyword_to_search.setText('iphone x case')
        self.textbox_keyword_to_search.move(130, 460)
        self.textbox_keyword_to_search.resize(200, 20)
        label = QLabel('Instances:', self.tab2)
        label.move(400, 430)
        label.resize(200, 20)
        self.textbox_instance_count_tab2 = QLineEdit(self.tab2)
        self.textbox_instance_count_tab2.setText('1')
        self.textbox_instance_count_tab2.move(400, 460)
        self.textbox_instance_count_tab2.resize(40, 20)
        self.button = QPushButton('Start Ranking by ASIN', self)
        self.button.clicked.connect(self.future_for_tab_2)
        self.tab2.layout.addWidget(self.button, alignment=Qt.AlignBottom)
        self.tab2.setLayout(self.tab2.layout)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        self.tab3.layout = QVBoxLayout(self)
        label = QLabel('Proxies:Ports', self.tab3)
        label.move(130, 40)
        label.resize(200, 20)
        self.textbox_proxy_adclicker = QTextEdit(self.tab3)
        self.textbox_proxy_adclicker.move(130, 70)
        self.textbox_proxy_adclicker.resize(280, 80)
        label = QLabel('ASIN key:', self.tab3)
        label.move(130, 250)
        label.resize(200, 20)
        self.textbox_asin_adclicker = QLineEdit(self.tab3)
        self.textbox_asin_adclicker.move(130, 280)
        self.textbox_asin_adclicker.resize(280, 20)
        label = QLabel('How many times:', self.tab3)
        label.move(130, 310)
        label.resize(200, 20)
        self.textbox_loop_adclicker = QLineEdit(self.tab3)
        self.textbox_loop_adclicker.move(130, 340)
        self.textbox_loop_adclicker.resize(280, 20)
        label = QLabel('Break from:', self.tab3)
        label.move(130, 370)
        label.resize(200, 20)
        self.textbox_break_first_adclicker = QLineEdit(self.tab3)
        self.textbox_break_first_adclicker.move(130, 400)
        self.textbox_break_first_adclicker.resize(60, 20)
        label = QLabel('to:', self.tab3)
        label.move(240, 400)
        label.resize(200, 20)
        self.textbox_break_second_adclicker = QLineEdit(self.tab3)
        self.textbox_break_second_adclicker.move(300, 400)
        self.textbox_break_second_adclicker.resize(60, 20)
        label = QLabel('Keyword to search:', self.tab3)
        label.move(130, 430)
        label.resize(200, 20)
        self.textbox_keyword_adclicker = QLineEdit(self.tab3)
        self.textbox_keyword_adclicker.move(130, 460)
        self.textbox_keyword_adclicker.resize(200, 20)
        self.button = QPushButton('Start Clicking Ads', self)
        self.button.clicked.connect(self.click_ads)
        self.tab3.layout.addWidget(self.button, alignment=Qt.AlignBottom)
        self.tab3.setLayout(self.tab3.layout)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        self.tab4.layout = QVBoxLayout(self)
        label = QLabel('Proxies:Ports', self.tab4)
        label.move(130, 40)
        label.resize(200, 20)
        self.textbox_proxy_categories = QTextEdit(self.tab4)
        self.textbox_proxy_categories.setText("\n".join(proxy_list))
        self.textbox_proxy_categories.move(130, 70)
        self.textbox_proxy_categories.resize(280, 50)

        #############################################3
        label = QLabel('Usernames:Password', self.tab4)
        label.move(630, 50)
        label.resize(200, 20)


        self.ctextbox_signin_accounts = QTextEdit(self.tab4)
        self.ctextbox_signin_accounts.setText("\n".join(signin_accounts))
        self.ctextbox_signin_accounts.move(430, 80)
        self.ctextbox_signin_accounts.resize(280, 80)
        #############################################3

        label = QLabel('ASIN key:', self.tab4)
        label.move(130, 120)
        label.resize(200, 20)
        self.textbox_asin_categories = QLineEdit(self.tab4)
        self.textbox_asin_categories.move(130, 140)
        self.textbox_asin_categories.resize(280, 20)
        label = QLabel('How many times:', self.tab4)
        label.move(130, 180)
        label.resize(200, 20)
        self.textbox_loop_categories = QLineEdit(self.tab4)
        self.textbox_loop_categories.setText("5000")
        self.textbox_loop_categories.move(130, 200)
        self.textbox_loop_categories.resize(280, 20)
        label = QLabel('Keyword to search:', self.tab4)
        label.move(130, 230)
        label.resize(200, 20)
        self.textbox_keyword_categories = QLineEdit(self.tab4)
        self.textbox_keyword_categories.move(130, 260)
        self.textbox_keyword_categories.resize(200, 20)
        label = QLabel('Instances:', self.tab4)
        label.move(400, 230)
        label.resize(200, 20)
        self.textbox_instance_count = QLineEdit(self.tab4)
        self.textbox_instance_count.setText('1')
        self.textbox_instance_count.move(400, 260)
        self.textbox_instance_count.resize(50, 20)
        label = QLabel('Break from:', self.tab4)
        label.move(130, 300)
        label.resize(200, 20)
        self.textbox_break_first_categories = QLineEdit(self.tab4)
        self.textbox_break_first_categories.setText("2")
        self.textbox_break_first_categories.move(130, 330)
        self.textbox_break_first_categories.resize(60, 20)
        label = QLabel('to:', self.tab4)
        label.move(240, 330)
        label.resize(200, 20)
        self.textbox_break_second_categories = QLineEdit(self.tab4)
        self.textbox_break_second_categories.setText("3")
        self.textbox_break_second_categories.move(300, 330)
        self.textbox_break_second_categories.resize(60, 20)
        label = QLabel('Category URL:', self.tab4)
        label.move(130, 360)
        label.resize(200, 20)
        self.textbox_category_url = QLineEdit(self.tab4)
        self.textbox_category_url.move(130, 390)
        self.textbox_category_url.resize(200, 20)
        label = QLabel('Product URLs: Enter one URL each line', self.tab4)
        label.move(130, 420)
        label.resize(200, 20)
        self.textbox_product_url = QTextEdit(self.tab4)
        self.textbox_product_url.setText('\n'.join(TEMP_PRD))
        self.textbox_product_url.move(130, 450)
        self.textbox_product_url.resize(600, 80)
        self.button = QPushButton('Start Ranking Category/URL', self.tab4)
        self.button.setGeometry(400, 423, 220, 25)
        self.progress = QProgressBar(self.tab4)
        self.progress.setGeometry(200, 20, 500, 20)
        self.progress_label = QLabel('STATUS: Click on start to start processing', self.tab4)
        self.progress_label.setGeometry(320, 42, 500, 20)
        self.button.clicked.connect(self.future_for_tab_4)
        self.check_wishlist = QCheckBox("Add to Wishlist", self.tab4)
        self.check_wedding_list = QCheckBox("Add to Wedding List", self.tab4)
        self.check_shopping_list = QCheckBox("Add to Shopping List", self.tab4)
        self.check_gift_list = QCheckBox("Add to Gift List", self.tab4)
        self.check_ranking = QCheckBox("Rank Product", self.tab4)
        #===========================================
        self.ccheck_signin_mode = QCheckBox("Sign in mode.", self.tab4)
        self.ccheck_signin_mode.setGeometry(400, 200, 480, 20)

        self.ccheck_click_image_mode = QCheckBox("Click Image.", self.tab4)
        self.ccheck_click_image_mode.setGeometry(600, 200, 480, 20)
        ######################################################
        self.check_ranking.setGeometry(400, 300, 500, 20)
        self.check_gift_list.setGeometry(400, 380, 480, 20)
        self.check_gift_list.setChecked(True)
        self.check_shopping_list.setGeometry(400, 360, 480, 20)
        self.check_wishlist.setGeometry(400, 340, 500, 20)
        self.check_wishlist.setChecked(True)
        self.check_wedding_list.setGeometry(400, 320, 500, 20)
        self.check_wedding_list.setChecked(True)
        self.tab4.setLayout(self.tab4.layout)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        self.tab5.layout = QVBoxLayout(self)
        label = QLabel('ASIN key:', self.tab5)
        label.move(130, 90)
        label.resize(200, 20)
        self.textbox_asin_adclicker_no_proxy = QLineEdit(self.tab5)
        self.textbox_asin_adclicker_no_proxy.move(130, 120)
        self.textbox_asin_adclicker_no_proxy.resize(280, 20)
        label = QLabel('How many times:', self.tab5)
        label.move(130, 150)
        label.resize(200, 20)
        self.textbox_loop_adclicker_no_proxy = QLineEdit(self.tab5)
        self.textbox_loop_adclicker_no_proxy.move(130, 180)
        self.textbox_loop_adclicker_no_proxy.resize(280, 20)
        label = QLabel('Break from:', self.tab5)
        label.move(130, 210)
        label.resize(200, 20)
        self.textbox_break_first_adclicker_no_proxy = QLineEdit(self.tab5)
        self.textbox_break_first_adclicker_no_proxy.move(130, 240)
        self.textbox_break_first_adclicker_no_proxy.resize(60, 20)
        label = QLabel('to:', self.tab5)
        label.move(240, 210)
        label.resize(200, 20)
        self.textbox_break_second_adclicker_no_proxy = QLineEdit(self.tab5)
        self.textbox_break_second_adclicker_no_proxy.move(300, 240)
        self.textbox_break_second_adclicker_no_proxy.resize(60, 20)
        label = QLabel('Keyword to search:', self.tab5)
        label.move(130, 270)
        label.resize(200, 20)
        self.textbox_keyword_adclicker_no_proxy = QLineEdit(self.tab5)
        self.textbox_keyword_adclicker_no_proxy.move(130, 300)
        self.textbox_keyword_adclicker_no_proxy.resize(200, 20)
        self.button = QPushButton('Start Clicking Ads', self)
        self.button.clicked.connect(self.click_ads_no_proxy)
        self.tab5.layout.addWidget(self.button, alignment=Qt.AlignBottom)
        self.tab5.setLayout(self.tab5.layout)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
