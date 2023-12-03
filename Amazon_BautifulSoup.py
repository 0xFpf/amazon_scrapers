from bs4 import BeautifulSoup
import requests
import time
import datetime
import pandas as pd
import csv

# input: ASIN + botkey + chatID + Desired Price 
botkey='5456465228:AAG4Undn1rXjgrYBJQ73FFpn5-7EcTBFjh0'
chatid='-788507835'
alertPrice = float('50')
asin= 'B07HCSL8JR'
timer= 60*30 #  how often it checks for price, right now it's at 60 seconds times 30 so 30 minutes intervals.

URL = f'https://www.amazon.co.uk/dp/{asin}/'

# main function
def check_price(URL):
    # Connect to Website and pull in data, remember to update headers if you get this error: title = soup2.find(id='productTitle').get_text()        AttributeError: 'NoneType' object has no attribute 'get_text'
    # It means you have old headers or made too many requests and Amazon wants to verify that youre not a bit so it blocks the page with a captcha etc.
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}
    page = requests.get(URL, headers=headers)
    soup1 = BeautifulSoup(page.content, "html.parser")
    soup2 = BeautifulSoup(soup1.prettify(), "html.parser")
    title = soup2.find(id='productTitle').get_text()
    availability = soup2.find(id='availability').get_text()

    # checks availability
    if 'Temporarily' in availability:
        price = 'out of stock'
        title = title.strip()
        pass
    else:
        price = soup2.find(id, {'class':'a-offscreen'}).get_text()
        price = float(price.strip()[1:])
        title = title.strip()

        # checks price
        if price<alertPrice:
            price=str(price)
            tgram=price+' '+asin+' '+title
            print(tgram)
            msg = f'https://api.telegram.org/bot{botkey}/sendMessage?chat_id={chatid}&text={tgram}'
            requests.get(msg)
        else:
            pass
    
    print("price is "+ str(price))
    print(title)

    # Sets up csv or appends data if one exists
    header = ['Title', 'Price', 'Date']
    Date = str(datetime.date.today())
    csvfile=Date+'AmazonScraper.csv'
    if csvfile == False:
        with open(Date+'AmazonScraper.csv', 'w', newline='', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
    else:
        Now=str(datetime.datetime.now())
        data = [title, price, Now]
        with open(Date+'AmazonScraper.csv', 'a+', newline='', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow(data)
    print('DONE')

# Runs check_price after a set time and inputs data into your CSV
while(True):
    check_price(URL)
    time.sleep(timer)