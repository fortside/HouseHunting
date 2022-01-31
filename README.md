# House Hunting
When shopping for a new home a couple years back I was signed up for listing alerts by my realtor.  These alerts included listing price changes and sales notifications - things not typically posted on MLS or other sites - invaluable information when trying to get the best deal. 

I wrote this utility to scrape my gmail inbox for listing alerts, pull the relevant data out of the page linked in the message, and stores the data I care about into a SQLite database. I then created a Power BI report to easily view what I wanted.

## Requirements
This is a fairly specific use case and won't likely be useful to many outside of Alberta. Or to anyone really. Just use the MLS website, it's less work than this, but this was a good excuse to learn some more Python and do a little data engineering.

### Prerequisites 
- A gmail account signed up to receive listing alerts from paragon messaging
- Tested using Edge browser on Windows 10 for Selenium web scraping
- Power BI Desktop only runs on Windows 10+, though any number of data viz tools would work fine

### Tools and libraries used
- Web scraping using BeautifulSoup
- Web scraping and phantom clicking using Selenium
- SQLite database for data storage
- ArcGIS geolocation library to convert addresses to lat/lon
- Power BI Desktop to view the data

### Sample Images
These are a couple simple reports that can be used. If pulling data for long enough you could easily see larger-scale information about local real estate trends, as opposed to being spoon fed by realtors.

Report page showing houses for sale, can easily filter the list based on various criteria (# bedrooms, finished basement, A/C, etc.) and view locations. Bigger circle = more expensive.
![Houses to potentially buy](https://github.com/fortside/HouseHunting/blob/main/forsale.png)

Report page with a different set of filters to view comparable houses for sale. Is my price to low/high? Easy to verify on a report like this. Bigger circle = more expensive
![Similar houses on the market](https://github.com/fortside/HouseHunting/blob/main/comparables.png)
