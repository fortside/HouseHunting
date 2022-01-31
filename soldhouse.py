import random
import requests
from bs4 import BeautifulSoup
import lxml
from geopy.geocoders import ArcGIS

#copy/paste of the House class with required scraping changes
class SoldHouse:
    def __init__(self, page_source, msg_date, listing):
        #get the adress from the listing and clean up the data for it
        soup = BeautifulSoup(page_source, "lxml")
        
        #scrape the rest of the house information off the page. There are two distinct formats :(
        if soup.find("div",{"style":"top:29px;left:580px;width:144px;height:14px;"}) is None:
            print("Incomplete details for " + listing + " from the summary email on " + msg_date)
            self.ListingID = soup.find("div",{"style":"top:55px;left:570px;width:75px;height:16px;"}).text
            self.listprice = int(soup.find("div",{"style":"top:2px;left:634px;width:100px;height:17px;"}).text.replace('$','').replace(',',''))
            self.saleprice = int(soup.find("div",{"style":"top:20px;left:634px;width:100px;height:17px;"}).text.replace('$','').replace(',',''))
            self.listdate = "Unknown"
            self.solddate = msg_date
            self.address = soup.find("div",{"style":"top:20px;left:203px;width:300px;height:17px;"}).text
        else:
            self.ListingID = soup.find("div",{"style":"top:29px;left:580px;width:144px;height:14px;"}).text
            self.listprice = int(soup.find("div",{"style":"top:5px;left:631px;width:91px;height:17px;"}).text.replace('$','').replace(',',''))
            self.saleprice = int(soup.find("div",{"style":"top:920px;left:324px;width:140px;height:16px;"}).text.replace('$','').replace(',',''))
            self.listdate = soup.find("div",{"style":"top:920px;left:575px;width:119px;height:16px;"}).text.split(" ")[0]
            self.solddate = soup.find("div",{"style":"top:935px;left:86px;width:139px;height:15px;"}).text
            self.address = soup.find("div",{"style":"top:5px;left:120px;width:349px;height:17px;"}).text
            if self.address is not None:
                geolocator = ArcGIS(user_agent="fs-househunter")
                location = geolocator.geocode(self.address + ", Fort Saskatchewan, AB")
                #make sure the location found is valid
                if location is not None and location.address.startswith(self.address.split(' ')[0]) and "T8L" in location.address:
                    self.address = location.address
            else:
                self.address = ""
                    
            print(self.ListingID + " created as sold house object")
