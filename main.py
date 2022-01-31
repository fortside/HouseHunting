#connect to gmail mailbox
#find all messages from person X in the last Y days
#for each message
# note the timestamp when it was sent and the URL it's linked to
# open that URL using a scraper and pull all the relevant data from the page
# save all the data off the page into a House object (class)
#take the array of Houses and save it somewhere (csv, excel, sqlite)
# foreach item make sure there's no entry for that date and address yet
# if it's already in there just ignore it, otherwise add it

from reademail import get_gmail_service, get_message_link, get_messages_list, process_messages, process_sold_summaries
from house import House
import os.path
from processhouses import create_tables, process_houses, process_sold_houses


dir_path = os.path.dirname(os.path.abspath(__file__))
db_file = os.path.join(dir_path, "houses.db")

msg_list_query = "from:Email@paragonmessaging.com subject:Real Estate Listing Notification for "
msg_list_recent_query = "from:Email@paragonmessaging.com notification newer_than:10d"
monthly_summary_query = "from:Email@paragonmessaging.com -notification newer_than:1d"

#connect to gmail
def main():
    
    #initialize array of new houses to document
    houses = []
    
    #create the gmail service so we can use the API
    service = get_gmail_service()
    
    #get a list of messages matching this criteria. One-time run to import everything, then just do the 'recent'
    #messages = get_messages_list(service, msg_list_query)
    messages = get_messages_list(service, msg_list_recent_query)
    
    #process all the matching emails
    process_messages(service, messages, houses)

    if len(houses) > 0:
        #get the db ready
        create_tables(db_file)
        #add our entries to the db
        process_houses(houses, db_file)
    else:
        print("nothing to add to house table")

    #our fresh array of sold houses
    sold_houses = []

    #get the list of monthly sold summaries
    #sold_messages = get_messages_list(service, monthly_summary_query)

    #now process the sold messages
    #process_sold_summaries(service, sold_messages, sold_houses)

    if len(sold_houses) > 0:
        #get the db ready
        create_tables(db_file)
        #add sold entries to the db
        process_sold_houses(sold_houses, db_file)

    print("The end")

if __name__ == '__main__':
    main()

