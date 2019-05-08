import upsmychoice
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from SimulatedDevice import iothub_client_telemetry_sample_run
import csv 
import requests 
import queue    # For Python 2.x use 'import Queue as queue'
import threading, time, random
import random
from captcha_solver import CaptchaSolver
from captcha2upload import CaptchaUpload
def FEXPackage(user, psswd):
    print (user)
    print (psswd)
    driver = webdriver.Firefox()
    driver.get("https://www.fedex.com/apps/fedextracking/?cntry_code=us&amp;locale=us_en#")
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//input[@class='fxg-field__input-text']"))) 
    users = driver.find_element_by_xpath("//input[@class='fxg-field__input-text']")
    password = driver.find_element_by_xpath("//input[@id='pswd-input']")
    users.send_keys(user)
    password.send_keys(psswd)
    password.send_keys(Keys.ENTER)
    try :
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='content']/div[2]/div/div[4]/div[5]/div[5]/div/div[5]/div/div/div[4]/div[1]"))) 
        deliveryStatus = driver.find_elements_by_xpath("//*[@id='content']/div[2]/div/div[4]/div[5]/div[5]/div/div[5]/div/div/div[4]/div[1]")
        for i in range(len(deliveryStatus)):
            status = driver.find_element_by_xpath("//*[@id='content']/div[2]/div/div[4]/div[5]/div[5]/div/div[5]/div/div["+str(i+1)+"]/div[4]/div[1]").text
            if status == "Delivered":
                continue
            tracking_number = driver.find_element_by_xpath("//*[@id='content']/div/div/div/div/div[5]/div/div/div/div["+str(i+1)+"]/div[2]/div").text
            scheduleDate = driver.find_element_by_xpath("//*[@id='content']/div[2]/div/div[4]/div[5]/div[5]/div/div[5]/div/div["+str(i+1)+"]/div[5]").text
            with open('myfile-1.csv',"a",encoding="utf-8",newline="") as f:
                writer=csv.writer(f,delimiter=',')
                writer.writerow(['FEDEX',scheduleDate,status,tracking_number]) 
            print(['FEDEX',tracking_number,status,scheduleDate])
            driver.close()
    except:
        None
    driver.close()
def USPSPackage(user1, passwd1):
    print(user1)
    print(passwd1)
    url = 'https://reg.usps.com/login?app=MyUSPS'
    #url="https://reg.usps.com/entreg/LoginAction"
    #display = Display(visible=0, size=(800, 600))
    #display.start()
    
    driver = webdriver.Firefox()
    #driver.implicitly_wait(10)
    time.sleep(2)

    driver.get('https://reg.usps.com/entreg/LoginAction_input?app=ATG&appURL=https%3A//store.usps.com/store/myaccount/profile.jsp')

    user = driver.find_element_by_xpath('//input[@id="username"]')

    driver.execute_script("arguments[0].value = '" + user1 + "'", user)
    time.sleep(3)
    password = driver.find_element_by_xpath('//input[@id="password"]')
    
    password.send_keys(passwd1)

    password.send_keys(Keys.ENTER)    
    time.sleep(2)
    if "Please try again" in driver.page_source:
        df3=pd.DataFrame()
        print("invalid credentials")
        driver.quit()
        return df3,"skip"
        

     
    driver.get(r'https://informeddelivery.usps.com/box/pages/secure/DashboardAction_input.action')

    
    page_source = driver.page_source

    response = scrapy.Selector(text=page_source)

    tracking_number = response.xpath("//div[@id='coltextR2']//div[@class='pack_h4']/text()").extract()

    delivery_date = []

    status = response.xpath(
        "//div[@class='pack_row']/div[@class='pack_lastscan_desk']/div[@id='coltextR3']/div[1]/text()").extract()

    delivery_month = response.xpath(
        "//div[@class='packageContainer']/div[@class='pack_row']/div[@class='pack_status-bigNumber']/div[1]/text()").extract()

    delivery_day = response.xpath(
        "//div[@class='packageContainer']/div[@class='pack_row']/div[@class='pack_status-bigNumber']/div[2]/text()").extract()

    carrier_val = []

    for i in range(len(delivery_month)):
        delivery_date.append(delivery_month[i] + "-" + delivery_day[i])

        carrier_val.append("USPS")

    print(tracking_number)

    print(status)

    print(delivery_date)

    df3 = pd.DataFrame({'carrier': carrier_val,

                        'estimated_delivery_date': delivery_date,

                        'status': status,
                        'tracking_number': tracking_number
                        })

    #df3 = df3["Delivered" not in df3["status"]]

    print(df3)

    driver.close()

    # display.stop()

    return df3,"valid"

def UPSPackage(user, psswd):
    print (user)
    print (psswd)
    try:
        session = upsmychoice.get_session(user, psswd)
        #print(session.status_code)
    except:
        df3=pd.DataFrame()
        print("invalid credentials")
        return df3,"skip"
    packages = upsmychoice.get_packages(session)
    filename = "UPS_" + user + "_" + psswd + ".csv"
    df1 = pd.DataFrame(packages)
    #df1 = df1[df1["status"] != "Delivered"]
    df1.drop(["estimated_delivery_timeframe"], axis=1, inplace=True)

    df1.drop(["delivery_date"], axis=1, inplace=True)

    

    df1.drop(["from"], axis=1, inplace=True)

    df1.drop(["from_location"], axis=1, inplace=True)
    ups = []
    for i in range(len(df1)):
        ups.append("UPS")

    dd = pd.DataFrame({'carrier': ups})

    df1 = pd.concat([dd,df1], axis=1)

    print(df1)

    return df1,"valid"
def AMAZONPackage(user, psswd):
    thread=[]
    trackingUrl=[]
    driver = webdriver.Firefox()
    driver.get("https://www.amazon.com/ap/signin?_encoding=UTF8&ignoreAuthState=1&openid.assoc_handle=usflex&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_signin&switch_account=")
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//input[@id='ap_email']")))
    emailField = driver.find_element_by_xpath("//input[@id='ap_email']")
    passwordField = driver.find_element_by_xpath("//input[@id='ap_password']")
    emailField.send_keys(user)
    passwordField.send_keys(psswd)
    passwordField.send_keys(Keys.ENTER)
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//input[@id='continue']")))
        verificationbutton = driver.find_element_by_xpath("//input[@id='continue']")
        verificationbutton.click()
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//*[@id='cvf-page-content']/div/div/div[1]/form/div[2]/input")))
        t1 = threading.Thread(target=iothub_client_telemetry_sample_run)
        t1.start()
        thread.append(t1)
        thread[0].join(0)
        time.sleep(60)
        verificationCode = []
        try:
            with open(r"verification.csv",mode="r",encoding="utf-8") as f:    
                reader=csv.reader(f,delimiter=",")
                for row_index, row_data in enumerate(reader):
                    verificationCode = row_data
        except:
            time.sleep(0.5)
        verificationbuttonInput =driver.find_element_by_xpath("//*[@id='cvf-page-content']/div/div/div[1]/form/div[2]/input")
        verificationbuttonInput.send_keys(verificationCode[0])
        submitVerification = driver.find_element_by_xpath("//*[@id='a-autoid-0']/span/input")
        submitVerification.click()
        try:
            os.remove("verification.csv")
        except:
            None        
        time.sleep(10)
    except:
        time.sleep(0.5)
        username = driver.find_element_by_xpath("//input[@id='ap_email']")
        imageCaptcha = driver.find_element_by_xpath("//div[@id='auth-captcha-image-container']/img[@id='auth-captcha-image']").get_attribute("src")
        password = driver.find_element_by_xpath("//input[@id='ap_password']")
        username.clear()
        password.clear()
        username.send_keys(user)
        password.send_keys(psswd)
        r = requests.get(imageCaptcha)  
        with open('imageCaptcha'+'.jpg','wb') as f: 
            f.write(r.content)
        # solver = CaptchaSolver('twocaptcha', api_key='e84b10e0869becd360d0a4eb58460449')
        captcha = CaptchaUpload('e84b10e0869becd360d0a4eb58460449')
        # raw_data = open('imageCaptcha.jpg', 'rb').read()
        # print(solver.solve_captcha(raw_data)) 
        captchaString = captcha.solve("imageCaptcha.jpg")   
        captchaKey = driver.find_element_by_xpath("//div[@class='a-section']/input[@id='auth-captcha-guess']")
        for x in captchaString:
            captchaKey.send_keys(x) 
            time.sleep(random.randint(1,4)/5)
        
        # time.sleep(3) 
        signupClick = driver.find_element_by_xpath("//input[@id='signInSubmit']")          
        signupClick.click()
        time.sleep(3)
        pass
        
    try:
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='nav-orders']")))
    except:
        return
    orderInfo = driver.find_element_by_xpath("//*[@id='nav-orders']")
    orderInfo.click()
    try :
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//div[@class='a-box-inner']/div/div/div[@class='a-row']/div/span/span/span/a")))
    except:
        None
    try :
        for i in range(100):
            try:
                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//div[@class='a-box-inner']/div/div/div[@class='a-row']/div/span/span/span/a")))
            except:
                break
            trackUrlElements = driver.find_elements_by_xpath("//div[@class='a-box-inner']/div/div/div[@class='a-row']/div/span/span/span/a")
            for trackUrlElement in trackUrlElements:
                trackingUrl.append(trackUrlElement.get_attribute("href"))
            try:
                nextButton = buttons[len(buttons)-1]
                nextButton.click()
                buttons = driver.find_elements_by_xpath("//*[@id='ordersContainer']/div/div/ul/li/a")      
                time.sleep(1)    
            except:
                break      
            
    except:
        None
    df4=[]
    for trancking in trackingUrl:
        driver.get(trancking)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='primaryStatus']")))
        time.sleep(1.8)
        try:
            trackingid = driver.find_element_by_xpath("//*[@id='carrierRelatedInfo-container']/div/span/a").text.split(":")[1][:-1]
        except:
            continue
        
        order= driver.find_element_by_xpath("//*[@id='primaryStatus']").text
        status = order.split(" ")[0]
        orderDate = order.replace(status,"")
        if status == "Delivered":
            print(['AMAZON',status,orderDate,trackingid]) 
            continue
        
        with open('myfile-1.csv',"a",encoding="utf-8",newline="") as f:
            writer=csv.writer(f,delimiter=',')
            writer.writerow(['AMAZON',status,orderDate,trackingid]) 
            print(['AMAZON',status,orderDate,trackingid])
        driver.close()
        driver.quit()   
     
def run():
    # try:
    #     os.remove("myfile-1.csv")
    # except:
    #     None      
    global df1, df2, df3,df4
    file = r"Login-1.csv"
    webs=[]
    usernames=[]
    passwords=[]
    validity=[]
    df = pd.read_csv(file)
    for i in range(len(df.index)):
        web = df.iloc[i][0]
        usernmae = df.iloc[i][2]
        password = df.iloc[i][1]
        webs.append(web)
        usernames.append(usernmae)
        passwords.append(password)
        vcerd=None
        if web == "AMAZON":
            AMAZONPackage(usernmae, password)
        if web == "UPS":
            df1,vcerd = UPSPackage(usernmae, password)
            with open('myfile-1.csv', 'a') as f:
               df1.to_csv(f,index=False, header=False)
        if web == "FEDEX":
            FEXPackage(usernmae, password)
        if web == "USPS":
            df3,vcerd = USPSPackage(usernmae, password)
            with open('myfile-1.csv', 'a') as f:
               df3.to_csv(f,index=False, header=False)    
        validity.append(vcerd)
    df = pd.DataFrame({'carrier':webs,'password':passwords,'username':usernames,'validity':validity})
    with open('Login-1.csv','w') as f:
        df.to_csv(f,index=False, header=True)
        print("---------------------------------------")
        print (df) 
    df = pd.read_csv('myfile-1.csv')
    df=df.drop_duplicates(['tracking_number'])

    df.to_csv('myfile-1.csv', index=False)

    print(list(df.tracking_number))


if __name__ == '__main__':
    run()






