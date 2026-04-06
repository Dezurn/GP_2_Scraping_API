import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
from selenium import webdriver as wd
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


url_main = 'https://weworkremotely.com'
page_main = requests.get(url_main) 
soup_main = BeautifulSoup(page_main.text, 'html')

category_names = []

#Получение категорий вакансий
for link in soup_main.find_all('a'):
    href = link.get('href')
    if href and 'categories' in href and '.rss' not in href and href not in category_names:
        category_names.append(link.get('href'))

category_names_clean = []

for name in category_names:
    category_names_clean.append(name.split('/')[-1])


job_names = []

#Получение названий вакансий
for name in category_names_clean:
    url_category = f'https://weworkremotely.com/categories/{name}'
    page_catogory = requests.get(url_category)
    soup_category = BeautifulSoup(page_catogory.text, 'html')
    for link in soup_category.find_all('a', {'class' : 'listing-link--unlocked'}):
        href = link.get('href')
        job_names.append(link.get('href'))
    time.sleep(2)

job_names_clean = []

for name in job_names:
    job_names_clean.append(name.split('/')[-1])

job_names_clean


jobs_data = []

options = Options()

options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

for job_name in job_names_clean:
    driver = wd.Chrome(options=options)

    job_url = f"https://weworkremotely.com/remote-jobs/{job_name}"
    
    driver.get(job_url)

    el_dict = {}

    element = driver.find_element(By.CLASS_NAME, "lis-container__header__hero__company-info__title")
    el_dict['Job name'] = element.text

    elements = driver.find_elements(By.CLASS_NAME, "lis-container__job__sidebar__job-about__list__item")

    el_list = []

    for el in elements:
        info = el.text.split('\n')
        if len(info) == 2:
            el_list.append(info)

    el_dict.update(dict(el_list))

    related_jobs = driver.find_elements(By.CLASS_NAME, "new-listing__header__title__text")

    el_list = []

    for el in related_jobs:
        el_list.append(el.text)

    el_dict["Related Jobs"] = el_list

    company_name = driver.find_element(By.CLASS_NAME, "lis-container__job__sidebar__companyDetails__info__title")
    info = company_name.text.split("\n")
    if len(info) > 1:
        el_dict['Company name'] = info[-1]
        el_dict['Company status'] = info[0]
    else:
        el_dict['Company name'] = info[0]
        el_dict['Company status'] = None

    job_posted = driver.find_element(By.CLASS_NAME, "lis-container__job__sidebar__companyDetails__info__jobs-posted")
    el_dict['Job posted by company'] = job_posted.text.split(':')[1]

    jobs_data.append(el_dict)
    driver.quit()


df = pd.DataFrame(jobs_data)
df.to_csv('we_work_remotely_jobs.csv')