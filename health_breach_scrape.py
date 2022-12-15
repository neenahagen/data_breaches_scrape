import os
import pandas as pd
import paramiko
import time
import traceback
from datetime import date
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException


start_time = time.time()

today = date.today()
scrape_date = today.strftime("%m_%d_%Y")


def health_breach_download_csv(df_type):
    chrome_options = Options()
    chrome_options.headless = True

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    driver.get('https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf')

    if df_type == 'archive': ## click 'Archive' button
        archive = driver.find_element(By.ID, 'ocrForm:j_idt24')
        archive.click()
        time.sleep(3) # Wait until page loads

    elem = driver.find_element(By.ID, 'ocrForm:resultsPanel')
    tlink = elem.find_elements(By.TAG_NAME, 'a')[2] # excep: 0, pdf: 1, csv: 2, txt: 3
    
    time.sleep(2)
    tlink.click()
    time.sleep(10)
    link = elem.get_attribute("href")

    os.rename('breach_report.csv', df_type+'.csv')


def clean_and_merge_all():
    under_invest = pd.read_csv('under_investigation.csv')
    arc = pd.read_csv('archive.csv')

    under_invest['Web Description'] = under_invest['Web Description'].astype(object)
    under_invest['Individuals Affected'] = under_invest['Individuals Affected'].astype(float)

    under_invest['Currently Under Investigation?'] = 'Yes'
    arc['Currently Under Investigation?'] = 'No'

    merged_reports = pd.concat([under_invest, arc])
    merged_reports.to_csv('merged_reports.csv', index=False)


def upload_ftp(df_type):
    try:
        ftp_credentials = {
            'HOST': os.environ['HOST'],
            'FTP_USER': os.environ['FTP_USER'],
            'PASSWORD': os.environ['PASSWORD']
        }
        with paramiko.SSHClient() as ssh:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                ftp_credentials['HOST'],
                username=ftp_credentials['FTP_USER'],
                password=ftp_credentials['PASSWORD']
            )
            sftp = ssh.open_sftp()
            if df_type != 'merged_reports':

                sftp.put(
                    localpath=df_type+'.csv',
                    remotepath=(
                        '/home/data/health_care_data_breaches/'+df_type+'/'+df_type+'_'+scrape_date+'.csv'
                    )
                )
            else:
                sftp.put(
                    localpath= df_type+'.csv',
                    remotepath=(
                        '/home/data/health_care_data_breaches/'+df_type+'/'+df_type+'.csv'
                    )
                )
    except KeyError:
        raise(KeyError('FTP credentials not set'))



if __name__ == '__main__': 

    #Download raw tables
    try:
        health_breach_download_csv('under_investigation')
        health_breach_download_csv('archive')
    except (TimeoutError, WebDriverException):
        raise Exception('Website likely down')

    #Clean and merge tables
    clean_and_merge_all()

    #Upload all to SFTP server
    upload_ftp('under_investigation')
    upload_ftp('archive')
    upload_ftp('merged_reports')


print("Process finished --- %s seconds ---" % (time.time() - start_time))
