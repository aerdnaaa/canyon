import requests, time, smtplib, ssl, os, datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from email.message import EmailMessage


def check_url(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    button_elements = soup.find_all('button', class_='productConfiguration__selectVariant')
    if button_elements:
        for button_element in button_elements:
            if button_element['data-product-size'] == 'M':
                return True
    return False

def send_email(bike_name, url, port, context, password):
    msg = EmailMessage()
    sender_email = "andregohbot@gmail.com"
    receiver_email = "andregohkr@hotmail.com"
    msg['Subject'] = 'Canyon Bike Availability'
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content(f"""Hi, the bike {bike_name} is currently available. You can check it out here: {url}""")

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, password)
        server.send_message(from_addr=sender_email,to_addrs=[receiver_email], msg=msg)
        
def get_bike_name(watchlist):
    watchdict = dict()
    for url in watchlist:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        title = soup.find_all('h1', class_='productDescription__productName')[0].text.strip()
        watchdict[title] = url
    return watchdict


def main():
    load_dotenv('.env')
    start_time = time.time()
    port = 465
    password = os.getenv('PASSWORD')    
    context = ssl.create_default_context()    
    watchlist = ['https://www.canyon.com/en-sg/road-bikes/endurance-bikes/endurace/al/endurace-7-disc/2946.html?dwvar_2946_pv_rahmenfarbe=BK%2FBK', 'https://www.canyon.com/en-sg/road-bikes/endurance-bikes/endurace/cf-sl/endurace-cf-sl-7-disc/2947.html?dwvar_2947_pv_rahmenfarbe=GY%2FBK']
    watchdict = get_bike_name(watchlist)
    while True:
        for title, url in watchdict.items():
            is_available = check_url(url)
            if is_available:
                send_email(title, url, port, context, password)
            else:
                print(title)
                now = datetime.datetime.now()
                with open('log.txt', 'a') as f:
                    f.write(f'\n{now}: {title} is still not available...')
                    f.close()
        time.sleep(600 - ((time.time() - start_time) % 60.0))

if '__main__' == __name__:
    main()