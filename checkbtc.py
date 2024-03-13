from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import sys
import datetime

PATH = "send/"

def scraping(url):
    print("selenium: ")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    print("accessnow...")
    time.sleep(1)
    amount = driver.find_elements(By.CLASS_NAME,"c-tradeRate__trade__jpy__amount")
    amount_decimal = driver.find_elements(By.CLASS_NAME,"c-tradeRate__trade__jpy__amount_decimal")
    print(amount[0].text + amount_decimal[0].text)
    print(amount[1].text + amount_decimal[1].text)
    res1 = amount[0].text + amount_decimal[0].text
    res2 = amount[1].text + amount_decimal[1].text
    driver.close()
    print("OK")
    if res1 == '-':
        print("retry...")
        return scraping(url)
    return res1,res2

url = sys.argv[1]
path = sys.argv[2]
res1,res2=scraping(url)
time_now = datetime.datetime.now()
time_now = time_now.strftime('%Y年%m月%d日 %H:%M:%S')
res = open(PATH+path,"w")
res.write(str(res1)+"\n"+str(res2)+"\n"+time_now)
res.close()
print("write:",path,"OK")
