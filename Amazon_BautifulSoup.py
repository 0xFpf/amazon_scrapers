from bs4 import BeautifulSoup
import requests
import time
import datetime
import csv
import threading
import tkinter as tk
import utils
import os

# Create threading Event
pause_event = threading.Event()

def check_price():
    while True:
        if not pause_event.is_set():
            asin = asin_entry.get()
            botkey=telegram_key_entry.get()
            chatid=telegram_id_entry.get()
            try:
                alertPrice = float(price_entry.get())
            except TypeError:
                response_listbox.insert(tk.END, "Invalid input. Please enter a number.")
                response_listbox.yview(tk.END)
                startButton.config(state='normal')
                break
            try:
                timer= 60*int(timer_entry.get()) #  right now it's at 60 seconds times input.
            except TypeError:
                response_listbox.insert(tk.END, "Invalid input. Please enter a number.")
                response_listbox.yview(tk.END)
                startButton.config(state='normal')
                break

            URL = f'https://www.amazon{country}/dp/{asin}/'

            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}
            try:
                page = requests.get(URL, headers=headers)
            except Exception as e:
                    response_listbox.insert(tk.END, f"Error connecting to Amazon, check connection & VPN, error msg: {e}")
                    response_listbox.yview(tk.END)
                    startButton.config(state='normal')
                    break
            
            soup1 = BeautifulSoup(page.content, "html.parser")
            soup2 = BeautifulSoup(soup1.prettify(), "html.parser")
            try:
                captcha= soup2.find(class_="a-last").get_text()
                if 'robot' in captcha:
                    response_listbox.insert(tk.END, f"Error, captcha encountered")
                    response_listbox.yview(tk.END)
                    startButton.config(state='normal')
                    break
            except Exception:
                pass

            try:
                title = soup2.find(id='productTitle').get_text()
            except Exception as e:
                    response_listbox.insert(tk.END, f"Error, product likely non-existent, error msg: {e}")
                    response_listbox.insert(tk.END, f"URL: {URL}")
                    response_listbox.yview(tk.END)
                    startButton.config(state='normal')
                    break
            availability = soup2.find(id='availability').get_text()

            # checks availability
            if 'Temporarily' in availability:
                price = 'out of stock'
                title = title.strip()
                    
            else:
                price = soup2.find(id, {'class':'a-offscreen'}).get_text()
                price = float(price.strip()[1:])
                title = title.strip()

                # checks price
                if price<=alertPrice:
                    price=str(price)
                    tgram=f'price is now {price} for {title}'
                    # print(tgram)
                    msg = f'https://api.telegram.org/bot{botkey}/sendMessage?chat_id={chatid}&text={tgram}'
                    try:
                        requests.get(msg)
                    except Exception as e:
                        response_listbox.insert(tk.END, "Error, issue with Telegram or inputted Telegram KEY & ID")
                        response_listbox.insert(tk.END, f"Error msg: {e}")
                        response_listbox.yview(tk.END)
                        startButton.config(state='normal')
                        break
            price_result=("price is "+ str(price))
            response_listbox.insert(tk.END, price_result+"  for "+str(title))
            response_listbox.yview(tk.END)

            # Sets up csv
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
            # print('Looping')
        time.sleep(timer)


def startThread():
    startButton.config(state='disabled')
    threading.Thread(target=check_price, args=(), daemon=True).start()

def togglePause():
    if pause_event.is_set():
        pause_event.clear()  # Resume the check_price() function
        pauseButton.config(text='Pause')
    else:
        pause_event.set()  # Pause the check_price() function
        pauseButton.config(text='Resume')

def endThread():
    utils.save_config(asin_entry, price_entry, timer_entry, telegram_id_entry, telegram_key_entry)
    exit()


def toggle_country():
    global country
    if country == ".co.uk":
        country = ".com"
        toggle_button.config(text="US")
    else:
        country = ".co.uk"
        toggle_button.config(text="UK")

def clear_placeholder(event, entry, placeholder):
    if entry.get() == placeholder:
        entry.delete(0, tk.END)
        entry.config(fg='black')

def reset_placeholder(event, entry, placeholder):
    if entry.get() == '':
        entry.insert(0, placeholder)
        entry.config(fg='grey')

# Initial country value
country = ".co.uk"



# Create the Tkinter window
root = tk.Tk()
root.title("Amazon price checker")
root.geometry("600x300+100+100")

# Set dark grey background color
root.configure(bg="#303030")


# Title label
title_label = tk.Label(root, text="Amazon price checker", bg="#303030", fg="white", font=("Arial", 16))
title_label.pack(pady=10)

# Toggle button to switch between UK and US
toggle_button = tk.Button(root, text="UK", bg="#181A1C", fg="white", font=("Arial", 10), command=toggle_country)
toggle_button.place(relx=1.0, rely=0, anchor="ne", x=-10, y=10)

# ID's field
input_frame = tk.Frame(root, bg="#303030")
input_frame.pack()

# ASIN Label and Entry
asin_placeholder = "Enter ASIN..."
asin_label = tk.Label(input_frame, text="ASIN:", bg="#303030", fg="white", font=("Arial", 8))
asin_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
asin_entry = tk.Entry(input_frame, bg="white", fg="black", font=("Arial", 8))
asin_entry.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

asin_entry.bind('<FocusIn>', lambda event: clear_placeholder(event, asin_entry, asin_placeholder))
asin_entry.bind('<FocusOut>', lambda event: reset_placeholder(event, asin_entry, asin_placeholder))


# Price Label and Entry
price_placeholder = "0.00"
price_label = tk.Label(input_frame, text="Price:", bg="#303030", fg="white", font=("Arial", 8))
price_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
price_entry = tk.Entry(input_frame, bg="white", fg="black", font=("Arial", 8))
price_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

price_entry.bind('<FocusIn>', lambda event: clear_placeholder(event, price_entry, price_placeholder))
price_entry.bind('<FocusOut>', lambda event: reset_placeholder(event, price_entry, price_placeholder))


# Timer Label and Entry
timer_placeholder = "Enter time in minutes..."
timer_label = tk.Label(input_frame, text="Timer:", bg="#303030", fg="white", font=("Arial", 8))
timer_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")
timer_entry = tk.Entry(input_frame, bg="white", fg="black", font=("Arial", 8))
timer_entry.grid(row=1, column=2, padx=5, pady=5, sticky="ew")

timer_entry.bind('<FocusIn>', lambda event: clear_placeholder(event, timer_entry, timer_placeholder))
timer_entry.bind('<FocusOut>', lambda event: reset_placeholder(event, timer_entry, timer_placeholder))


# Telegram ID Label and Entry
telegram_id_placeholder = "Enter Telegram Chat ID..."
telegram_id_label = tk.Label(input_frame, text="Telegram ID:", bg="#303030", fg="white", font=("Arial", 8))
telegram_id_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
telegram_id_entry = tk.Entry(input_frame, bg="white", fg="black", font=("Arial", 8))
telegram_id_entry.grid(row=3, column=0, columnspan=1, padx=5, pady=5, sticky="ew")

telegram_id_entry.bind('<FocusIn>', lambda event: clear_placeholder(event, telegram_id_entry, telegram_id_placeholder))
telegram_id_entry.bind('<FocusOut>', lambda event: reset_placeholder(event, telegram_id_entry, telegram_id_placeholder))

# Telegram Key Label and Entry
telegram_key_placeholder = "Enter Telegram API Key..."
telegram_key_label = tk.Label(input_frame, text="Telegram Key:", bg="#303030", fg="white", font=("Arial", 8))
telegram_key_label.grid(row=2, column=1, padx=5, pady=5, sticky="w")
telegram_key_entry = tk.Entry(input_frame, bg="white", fg="black", font=("Arial", 8))
telegram_key_entry.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

telegram_key_entry.bind('<FocusIn>', lambda event: clear_placeholder(event, telegram_key_entry, telegram_key_placeholder))
telegram_key_entry.bind('<FocusOut>', lambda event: reset_placeholder(event, telegram_key_entry, telegram_key_placeholder))


# Buttons frame
button_frame = tk.Frame(root, bg="#303030")
button_frame.pack()

startButton = tk.Button(button_frame, text='Start', fg="white", bg="#181A1C", command=startThread)
startButton.pack(side=tk.LEFT, padx=5, pady=10)

pauseButton = tk.Button(button_frame, text='Pause', fg="white", bg="#181A1C", command=togglePause)
pauseButton.pack(side=tk.LEFT, padx=5, pady=10)

endScript = tk.Button(button_frame, text='Quit', fg="white", bg="#181A1C", command=endThread)
endScript.pack(side=tk.LEFT, padx=5, pady=10)

# Response window with history
response_frame = tk.Frame(root, bg="black")
response_frame.pack(fill="both", expand=True)

response_listbox = tk.Listbox(response_frame, bg="black", fg="white", font=("Arial", 8), selectbackground="#303030", selectforeground="white")
response_listbox.pack(fill="both", expand=True)

if os.path.isfile('config.ini'):
    utils.load_config(asin_entry, price_entry, timer_entry, telegram_id_entry, telegram_key_entry)
else:
    asin_entry.insert(0, asin_placeholder)
    price_entry.insert(0, price_placeholder)
    timer_entry.insert(0, timer_placeholder)
    telegram_id_entry.insert(0, telegram_id_placeholder)
    telegram_key_entry.insert(0, telegram_key_placeholder)
# Make the response window always cover the entire bottom half of the GUI
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(3, weight=1)

# Start the Tkinter event loop
root.mainloop()