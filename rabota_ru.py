import random
from selenium import webdriver as wd
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd

def save_vacancies_data(data, output_file):
    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)


def parse_rabota_ru_vacancy_page(vacancy_url):
    page = requests.get(vacancy_url, timeout=20)
    soup_vacancy = BeautifulSoup(page.text, 'html.parser')

    vacancy_info = {}

    name = soup_vacancy.find('h1', {'class': 'vacancy-card__title'}, itemprop='title')
    if name:
        vacancy_info['Название вакансии'] = name.text.strip()
    else:
        title = soup_vacancy.find('div', {'class': 'branding-vacancy-card-header__title'})
        vacancy_info['Название вакансии'] = title.text.strip() if title else None

    salary = soup_vacancy.find('h3', {'class': 'vacancy-card__salary'})
    if salary:
        vacancy_info['Зарплата'] = salary.text.replace('\xa0', '').strip()
    else:
        salary = soup_vacancy.find('div', {'class': 'branding-vacancy-card-header__salary'})
        vacancy_info['Зарплата'] = salary.text.replace('\xa0', '').strip() if salary else None

    vacancy_info['Требуемые навыки'] = [skill.text.strip() for skill in soup_vacancy.find_all('div', {'class': 'vacancy-card__skills-item'})]
    vacancy_info['Теги'] = [tag.text.strip() for tag in soup_vacancy.find_all('div', {'class': 'vacancy-tags__tag'})]

    company = soup_vacancy.find('a', itemprop='legalName')
    vacancy_info['Компания'] = company.text.strip() if company else None

    vacancy_info['Метро'] = [station.text.strip() for station in soup_vacancy.find_all('span', {'class': 'vacancy-locations__station'})]

    address = soup_vacancy.find('div', {'class': 'vacancy-locations__address'}, itemprop='address')
    vacancy_info['Адрес'] = address.text.strip() if address else None

    city = soup_vacancy.find('span', {'class': 'vacancy-requirements__city'})
    if city:
        vacancy_info['Город'] = city.text.strip()
    else:
        city = soup_vacancy.find('a', {'class': 'router-link-active', 'href': '/', 'itemprop': 'item'})
        vacancy_info['Город'] = city.text.strip() if city else None

    categories = [el.text.strip() for el in soup_vacancy.find_all('span', {'itemprop': 'name'})]
    if len(categories) >= 5 or (len(categories) == 4 and categories[3] != vacancy_info.get('Название вакансии')):
        vacancy_info['Сфера'] = categories[2]
        vacancy_info['Общее название профессии'] = categories[3]
    elif len(categories) == 4 and vacancy_info.get('Название вакансии') and categories[2] in vacancy_info['Название вакансии']:
        vacancy_info['Общее название профессии'] = categories[2]
    elif len(categories) == 4:
        vacancy_info['Сфера'] = categories[2]

    info = soup_vacancy.find('div', {'class': 'vacancy-requirements'})
    if info:
        info_parts = [part.strip() for part in info.text.strip().split(',') if part.strip()]
        if len(info_parts) >= 2:
            vacancy_info['Опыт работы'] = info_parts[-2]
            vacancy_info['Образование'] = info_parts[-1]
        elif info_parts:
            vacancy_info['Опыт работы'] = info_parts[0]
            vacancy_info['Образование'] = None
        else:
            vacancy_info['Опыт работы'] = None
            vacancy_info['Образование'] = None
    else:
        exp = soup_vacancy.find('div', {'class': 'info-table__text'}, itemprop='experienceRequirements')
        edu = soup_vacancy.find('div', {'class': 'info-table__text'}, itemprop='educationRequirements')
        vacancy_info['Опыт работы'] = exp.text.strip() if exp else None
        vacancy_info['Образование'] = edu.text.strip() if edu else None

    vacancy_info['Ссылка'] = vacancy_url
    return vacancy_info


def parse_rabota_ru(cities_dict, output_file):
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.page_load_strategy = 'eager'
    
    driver = wd.Chrome(options=options)
    driver.set_page_load_timeout(40)
    
    data = []
    
    for city, value in cities_dict.items():
        main_url, pages = value
        for page in range(1, pages + 1):
            url = f"{main_url}{page}"
            print(f"Обработка страницы {page}: {url}, город: {city}")
            
            driver.get(url)
            time.sleep(random.uniform(2, 3))
            
            cards = driver.find_elements(By.CSS_SELECTOR, ".vacancy-preview-card")
            
            for card in cards:
                vacancy_link = None
                try:
                    title_el = card.find_element(By.CSS_SELECTOR, "a.vacancy-preview-card__title_border")
                    vacancy_link = title_el.get_attribute("href")
                except:
                    vacancy_link = None

                if not vacancy_link:
                    continue

                vacancy_info = parse_rabota_ru_vacancy_page(vacancy_link)
                vacancy_info["Город"] = city
                data.append(vacancy_info)

            save_vacancies_data(data, output_file)
            print(f"Сохранено {len(data)} вакансий в {output_file} после страницы {page}.")
            
            time.sleep(random.uniform(2, 3))
    
    driver.quit()
    
    print(f"Собрано вакансий: {len(data)}")
    return data


cities = {'Москва': ['https://www.rabota.ru/?page=', 178],
          'Санкт-Петербург':['https://spb.rabota.ru/?page=', 93],
          'Екатеренбург': ['https://eburg.rabota.ru/?page=',57], 
          'Московская область': ['https://msk-region.rabota.ru/?page=', 97]}
parse_rabota_ru(cities, output_file='rabota_ru.csv')