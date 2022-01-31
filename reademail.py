from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import os.path
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64
import email
from bs4 import BeautifulSoup
from house import House
from datetime import datetime
from soldhouse import SoldHouse
import lxml
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from msedge.selenium_tools import Edge, EdgeOptions
from geopy.geocoders import ArcGIS
import time

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
dir_path = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(dir_path, "credentials.json")
TOKEN_FILE = os.path.join(dir_path, "token.pickle")

def get_gmail_service():

   creds = None
   # The file token.pickle stores the user's access and refresh tokens, and is
   # created automatically when the authorization flow completes for the first
   # time.
   if os.path.exists(TOKEN_FILE):
       with open(TOKEN_FILE, 'rb') as token:
           creds = pickle.load(token)
   # If there are no (valid) credentials available, let the user log in.
   if not creds or not creds.valid:
       if creds and creds.expired and creds.refresh_token:
           creds.refresh(Request())
       else:
           flow = InstalledAppFlow.from_client_secrets_file(
               CREDENTIALS_FILE, SCOPES)
           creds = flow.run_local_server(port=0)

       # Save the credentials for the next run
       with open(TOKEN_FILE, 'wb') as token:
           pickle.dump(creds, token)

   service = build('gmail', 'v1', credentials=creds)
   return service

def get_messages_list(svc, query):
    results = svc.users().messages().list(userId='me',labelIds = ['INBOX'],q=query, maxResults=500).execute()
    messages = results.get('messages', [])
    if not messages:
        return None
    else:
        return messages

def get_message_link(msg):
    msg_str = base64.urlsafe_b64decode(msg['raw'].encode('UTF-8'))
    mime_msg = email.message_from_bytes(msg_str)
    for part in mime_msg.walk():
        mime_msg.get_payload()
        if part.get_content_type() == 'text/html':
            html_body = base64.urlsafe_b64decode(part.get_payload().encode('UTF-8'))
            continue
    parsed_html = BeautifulSoup(html_body, features="lxml")
    link = parsed_html.find('a').get('href')
    return link

def process_messages(service, messages, houses):
    if not messages:
        print("No new messages")
    else:
        for message in messages:
            #grab the full message now
            msg = service.users().messages().get(userId='me', id=message['id'],format='raw').execute()
            #get the date that the message was sent
            msg_date = datetime.fromtimestamp(float(msg['internalDate'])/1000).strftime('%Y-%m-%d')
            #get the URL inside the body of the message
            html_link = get_message_link(msg)
            #create a House object based on that
            thishouse = House(html_link,msg_date)
            houses.append(thishouse)

def process_sold_summaries(service, sold_messages, sold_houses):
    if not sold_messages:
        print("No new messages")
    else:
        for message in sold_messages:
            #grab the full message now
            msg = service.users().messages().get(userId='me', id=message['id'],format='raw').execute()
            msg_date = datetime.fromtimestamp(float(msg['internalDate'])/1000).strftime('%Y-%m-%d')
            #get the URL inside the body of the message
            html_link = get_message_link(msg)
           
            options = EdgeOptions()
            options.use_chromium = True
            options.add_argument("headless")
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            driver = Edge(options = options)
            driver.get(html_link)
            timeout = 20
            try:
                driver.switch_to.frame(1)
                element_present = EC.presence_of_element_located((By.ID, 'ddViews'))
                WebDriverWait(driver, timeout).until(element_present)
            except TimeoutException:
                print("Timed out waiting for page to load")
                return
            except:
                print("Error accessing " + html_link)
                return
            
            #get the table of sold listings now
            sold_table = BeautifulSoup(driver.page_source, "lxml").find('table').find_all('tr')
            
            #find the link text in the listing HTML
            for row in sold_table:
                sold_row = row.text.split('\n')
                for cell in sold_row:
                    if 'ML' in cell:
                        #found the text. Now click the link
                        driver.switch_to.default_content()
                        driver.switch_to.frame(1)
                        try:
                            driver.find_element_by_link_text(cell).click()
                            #wait for the other frame to load. Pathetic lazy hack
                            time.sleep(5)
                            driver.switch_to.default_content()
                            driver.switch_to.frame(3)
                            element_present = EC.presence_of_element_located((By.ID, 'divHtmlReport'))
                            WebDriverWait(driver, timeout).until(element_present)
                        except TimeoutException:
                            print("Timed out waiting for sold frame to load")
                            return
                        except:
                            print("Error accessing " + cell)
                            return
                        #sold_item_soup = BeautifulSoup(driver.page_source, "lxml")
                        #print(driver.page_source)
                        #ad = sold_item_soup.find("div",{"style":"top:20px;left:203px;width:300px;height:17px;"}).text
                        #print(ad)
                        #create a Sold House object based on that
                        thishouse = SoldHouse(driver.page_source, msg_date, cell)
                        sold_houses.append(thishouse)    
            driver.quit()
    print("sold summaries are now processed")