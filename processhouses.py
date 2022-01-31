import sqlite3
import datetime
from house import House
from soldhouse import SoldHouse

def create_tables(db):

    houses_table = "Create table if not exists houses (" \
                    "ListingID text" \
                    ", Date text" \
                    ", Style text" \
                    ", Built text" \
                    ", Address text" \
                    ", Latitude real" \
                    ", Longitude real" \
                    ", FullBath integer" \
                    ", HalfBath integer" \
                    ", Bdr_Above integer" \
                    ", Bdr_Total integer" \
                    ", Bdr_Bsmt integer" \
                    ", Bsmt_Dev text" \
                    ", Ag_Sq_Ft real" \
                    ", Parking text" \
                    ", GoodsIncluded text" \
                    ", PreviousListPrice integer" \
                    ", CurrentListPrice integer" \
                    ", SalePrice integer" \
                    ", ListingURL text" \
                    ")"

    sold_houses_table = "Create table if not exists sold_houses (" \
                    "ListingID text" \
                    ", ListDate text" \
                    ", SoldDate text" \
                    ", ListPrice integer" \
                    ", SoldPrice integer" \
                    ", Address text" \
                    ")"

    # connect to the database
    conn = sqlite3.connect(db)

    # get the cursor so we can do stuff
    cur = conn.cursor()

    # create our tables
    cur.execute(houses_table)
    conn.commit()
    cur.execute(sold_houses_table)
    conn.commit()

    # close the connections
    cur.close()
    conn.close()

def process_houses(houses, db):
    # connect to the database
    conn = sqlite3.connect(db)
    # get the cursor so we can do stuff
    cur = conn.cursor()

    #add a record for each house into the database if they're new
    for house in houses:
        if house.ListingID is not None:
            #create a select statement to check that URL
            query = "select * from houses where ListingID = (?) and Date = (?) limit 1"
            cur.execute(query, [house.ListingID, house.date])
            this_house = cur.fetchone()

            if this_house == None:
                if house.address is not None:
                    # this is a new house price update
                    house_insert = "insert or ignore into houses values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);"
                    house_values = [house.ListingID,
                                    house.date,
                                    house.style,
                                    house.built,
                                    house.address,
                                    house.lat,
                                    house.lon,
                                    house.full_bath,
                                    house.half_bath,
                                    house.bdr_above,
                                    house.bdr_total,
                                    house.bdr_bsmt,
                                    house.bsmt_dev,
                                    house.ag_sq_ft,
                                    house.parking,
                                    house.goodsincluded,
                                    house.prev_listprice,
                                    house.listprice,
                                    house.saleprice,
                                    house.url
                                    ]
                    cur.execute(house_insert, house_values)
                    conn.commit()
                    print("Added " + house.address + " for $" + str(house.listprice) + " to houses table")
                else:
                    print(house.url + " has no info, can't add to table")
            else:
                print(house.address + " for $" + str(house.listprice) + " already exists in houses table")


def process_sold_houses(sold_houses, db):
    # connect to the database
    conn = sqlite3.connect(db)
    # get the cursor so we can do stuff
    cur = conn.cursor()

    #add a record for each house into the database if they're new
    for house in sold_houses:
        if house.ListingID is not None:
            #create a select statement to check that URL
            query = "select * from sold_houses where ListingID = (?) limit 1"
            cur.execute(query, [house.ListingID])
            this_house = cur.fetchone()

            if this_house == None:
                if house.ListingID is not None:
                    # this is a new sold house
                    house_insert = "insert or ignore into sold_houses values (?,?,?,?,?,?);"
                    house_values = [house.ListingID,
                                    house.listdate,
                                    house.solddate,
                                    house.listprice,
                                    house.saleprice,
                                    house.address
                                    ]
                    cur.execute(house_insert, house_values)
                    conn.commit()
                    print("Added " + house.ListingID + " to sold houses table")
                else:
                    print("Sold house object has no info, can't add to table. Try again in debug mode")
            else:
                print(house.ListingID + " already exists in sold houses table")
