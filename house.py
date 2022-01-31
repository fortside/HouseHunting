import random
import requests
from bs4 import BeautifulSoup
import lxml
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from msedge.selenium_tools import Edge, EdgeOptions
from geopy.geocoders import ArcGIS

class House:
    def __init__(self, url, date):
        self.url = url
        self.date = date
        self.get_house_properties()

    def get_house_properties(self):

        #load up geolocator class
        geolocator = ArcGIS(user_agent="fs-househunter")

        # Launch Microsoft Edge (Chromium)
        # downloaded msedgedriver.exe and copied the exe to SYSWOW64 folder (since it's in PATH)
        options = EdgeOptions()
        options.use_chromium = True
        options.add_argument("headless")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = Edge(options = options)
        driver.get(self.url)
        timeout = 20
        try:
            driver.switch_to.frame(3)
            element_present = EC.presence_of_element_located((By.ID, 'divHtmlReport'))
            #element_present = EC.visibility_of_element_located((By.CSS_SELECTOR, "top:989px;left:658px;width:90px;height:16px;"))
            WebDriverWait(driver, timeout).until(element_present)
        except TimeoutException:
            print("Timed out waiting for page to load")
            return
        except:
            print("Error accessing " + self.url)
            return

        soup = BeautifulSoup(driver.page_source, "lxml")

        #get the adress from the listing and clean up the data for it
        self.address = soup.find("div",{"style":"top:20px;left:203px;width:300px;height:17px;"}).text
        if self.address is not None:
            location = geolocator.geocode(self.address + ", Fort Saskatchewan, AB")
            #make sure the location found is valid
            if location is not None and location.address.startswith(self.address.split(' ')[0]) and "T8L" in location.address:
                self.lat = location.latitude
                self.lon = location.longitude
                #also update the location to a more consistent name
                self.address = location.address
            elif location is not None:
                print("Partial address match - lookup:" + self.address + ". Result:" + location.address)
                self.lat = location.latitude
                self.lon = location.longitude
            else:
                print("No address match found for: " + self.address)
                self.lat = 0
                self.lon = 0
        else:
            print("No address for listing: " + self.url)
            self.lat = 0
            self.lon = 0
        #scrape the rest of the house information off the pace
        self.ListingID = soup.find("div",{"style":"top:55px;left:570px;width:75px;height:16px;"}).text
        self.style = soup.find("div",{"style":"top:71px;left:285px;width:190px;height:16px;"}).text
        self.built = int(soup.find("div",{"style":"top:87px;left:285px;width:190px;height:16px;"}).text)
        self.full_bath = int(soup.find("div",{"style":"top:103px;left:285px;width:190px;height:16px;"}).text)
        self.half_bath = int(soup.find("div",{"style":"top:119px;left:285px;width:190px;height:16px;"}).text)
        self.bdr_above = int(soup.find("div",{"style":"top:71px;left:570px;width:175px;height:16px;"}).text)
        self.bdr_total = int(soup.find("div",{"style":"top:87px;left:570px;width:175px;height:16px;"}).text)
        self.bdr_bsmt = self.bdr_total - self.bdr_above
        self.bsmt_dev = soup.find("div",{"style":"top:119px;left:570px;width:175px;height:16px;"}).text
        self.ag_sq_ft = float(soup.find("div",{"style":"top:135px;left:285px;width:190px;height:16px;"}).text.replace(',',''))
        self.listprice = int(soup.find("div",{"style":"top:2px;left:634px;width:100px;height:17px;"}).text.replace('$','').replace(',',''))
        try:
            self.saleprice = int(soup.find("div",{"style":"top:20px;left:634px;width:100px;height:17px;"}).text.replace('$','').replace(',',''))
        except:
            self.saleprice = 0
        self.parking = soup.find("div",{"style":"top:422px;left:102px;width:415px;height:16px;"}).text
        self.goodsincluded = soup.find("div",{"style":"top:690px;left:102px;width:277px;height:77px;"}).text

        ##START new part
        #now go to the mobile view to get the price change data, since it's not available in the desktop view
        try:
            mobile_url = "https://rae.paragonrels.com/CollabLink/?id=" + self.url.split('=')[1].split('&')[0]
            driver.get(mobile_url)
            #element_present = EC.presence_of_element_located((By.ID, 'normalList'))
            element_present = EC.presence_of_element_located((By.CSS_SELECTOR, '.color-green'))
            WebDriverWait(driver, timeout).until(element_present)
        except TimeoutException:
            print("")

        mobile_soup = BeautifulSoup(driver.page_source, "lxml")
        pdropval = mobile_soup.find("div",{"class":"price-change-value"})
        if pdropval is None:
            print("No price drop for " + self.address)
            price_drop = 0
        else:
            price_drop = int(pdropval.text.replace('$','').replace(',',''))
            print(str(price_drop) + " price drop for " + self.address)
        self.prev_listprice = self.listprice + price_drop

        ##END new part
        print(self.address + " created as house object")

        #clean up the browser
        driver.quit()
