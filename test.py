# getting infinite jobs
import contextlib
import time

import pandas as pd
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

chrome_options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
web_url = "https://in.linkedin.com/jobs/search?keywords=Python%20Developer&location=Ahmedabad%2C%20Gujarat%2C%20India&geoId=104990346&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0"
driver.get(web_url)


def scroll_to_bottom():
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(6)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


while True:
    scroll_to_bottom()

    try:
        if driver.find_element(By.XPATH, "//button[@aria-label='See more jobs']"):
            see_more_jobs = driver.find_element(By.XPATH, '//button[@aria-label="See more jobs"]')
            see_more_jobs.click()
            time.sleep(3)
    except Exception as e:
        break

jobs = driver.find_elements(By.XPATH, ".//div[@class='base-search-card__info']")

position_list = []
companies_list = []
locations_list = []
posted_ats_list = []


def inner(parent, strategy, locator, default='None'):
    get_company = None
    with contextlib.suppress(NoSuchElementException):
        get_company = parent.find_element(By.XPATH, ".//a[@class='hidden-nested-link']").text
    if not get_company:
        with contextlib.suppress(NoSuchElementException):
            get_company = parent.find_element(strategy, locator).text
    return get_company or default


try:
    for job in jobs:
        position = job.find_element(By.XPATH, ".//h3[@class='base-search-card__title']")
        position_list.append(position.text)
        companies = inner(job, By.XPATH, ".//h4[@class='base-search-card__subtitle']")
        # companies = inner(job, By.XPATH, ".//a[@class='hidden-nested-link']")
        companies_list.append(companies)
        locations = job.find_element(By.XPATH,
                                     ".//span[@class='job-search-card__location']")
        locations_list.append(locations.text)
        posted_ats = job.find_element(By.XPATH,
                                      ".//time[starts-with(@class, 'job-search-card__listdate')]")
        posted_ats_list.append(posted_ats.text)
    job_df = pd.DataFrame({
        'position': position_list,
        'companies': companies_list,
        'locations': locations_list,
        'posted_ats': posted_ats_list
    })

    job_df.to_excel('infinite_jobs.xlsx', index=False)
    driver.quit()
except Exception as e:
    print(f'Error : {e}')
