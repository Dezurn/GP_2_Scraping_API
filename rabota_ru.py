import requests
import time
import pandas as pd
from bs4 import BeautifulSoup


vacancy_links = []

#нужно добавить логгирование
#парсим ссылки на вакансии(нужно сделать так чтоб нас не банило)


headers = {'User-Agent': 'Mozilla/5.0'} 

cities = {'Москва': ['https://www.rabota.ru/?page=', 3], 'Санкт-Петербург':['https://spb.rabota.ru/?page=', 3],
          'Екатеренбург': ['https://eburg.rabota.ru/?page=', 3], 'Московсская область': ['https://msk-region.rabota.ru/?page=', 3]}

for key, value in cities.items():
    city = key
    num_pages = value[1] + 1
    url_main = value[0]

    for i in range(1,num_pages):
        url = f'{url_main}{i}'
        print(city, url)
        page_main = requests.get(url, headers=headers, timeout=15)

        soup_main = BeautifulSoup(page_main.text, 'html')

        for link in soup_main.find_all('a'):
            part = link.get('href')
            if part and 'vacancy' in part and '?' in part:
                vacancy_links.append(f"https://www.rabota.ru/{part.split('?')[0]}")
        
        time.sleep(2)

    vacancy_links = list(set(vacancy_links))
    if 'https://www.rabota.ru/vacancy' in vacancy_links:
        vacancy_links.remove('https://www.rabota.ru/vacancy')

    vacancy_data = []


    #нужно добавить логгирование
    #парсим информацию о вакансиях(нужно сделать так чтоб нас не банило)
    vacancy_data = []

    for link in vacancy_links:
        url_vacancy = link
        page_vacancy = requests.get(link, headers=headers, timeout=15) 
        soup_vacancy = BeautifulSoup(page_vacancy.text, 'html')

        vacancy_info = {}

        #Название
        name =  soup_vacancy.find('h1', {'class' : 'vacancy-card__title'}, itemprop = 'title')
        if name:
            vacancy_info['Название вакансии'] = name.text.strip()
        else:
            vacancy_info['Название вакансии'] = soup_vacancy.find('div', {'class' : 'branding-vacancy-card-header__title'}).text.strip()

        #Зарплата
        salary = soup_vacancy.find('h3', {'class' : 'vacancy-card__salary'})
        if salary:
            vacancy_info['Зарплата'] = salary.text.replace('\xa0', '')
        else:
            vacancy_info['Зарплата'] = soup_vacancy.find('div', {'class' : 'branding-vacancy-card-header__salary'}).text.replace('\xa0', '')

        #Требуемые навыки
        skills = []

        for skill in soup_vacancy.find_all('div', {'class' : 'vacancy-card__skills-item'}):
            skills.append(skill.text.strip())

        vacancy_info['Требуемые новыки'] = skills

        #Теги к вакансии
        tags = []

        for tag in soup_vacancy.find_all('div', {'class' : 'vacancy-tags__tag'}):
            tags.append(tag.text.strip())

        vacancy_info['Теги'] = tags

        vacancy_info['Компания'] = soup_vacancy.find('a', itemprop='legalName').text.strip()

        #Метро
        metro = []

        for station in soup_vacancy.find_all('span', {'class' : 'vacancy-locations__station'}):
            metro.append(station.text.strip())

        vacancy_info['Метро'] = metro

        #Адрес работы
        adress = soup_vacancy.find('div', {'class' : "vacancy-locations__address"}, itemprop="address")

        if adress:
            vacancy_info['Адрес'] = adress.text.strip().split(',')[len(metro):]
        else:
            vacancy_info['Адрес'] = None
        
        #Город работы
        vacancy_info['Город'] = city

        #Категории вакансии(может работать криво)
        categories = []

        for el in soup_vacancy.find_all('span', {'itemprop': 'name'}):
            categories.append(el.text)

        if len(categories) >= 5 or (len(categories) == 4 and categories[3] != vacancy_info['Название вакансии']):
            vacancy_info['Сфера'] = categories[2]
            vacancy_info['Общее название профессии'] = categories[3]
        elif len(categories) == 4 and categories[2] in vacancy_info['Название вакансии']:
            vacancy_info['Общее название профессии'] = categories[2]
        elif len(categories) == 4:
            vacancy_info['Сфера'] = categories[2]
        
        #Дополнительная информация(образование и опты работы)
        info = soup_vacancy.find('div', {'class' : 'vacancy-requirements'})
        if info:
            info = info.text.strip().split(',')
            vacancy_info['Опыт работы'] = info[-2].strip()
            vacancy_info['Образование'] = info[-1]     
        else:
            vacancy_info['Опыт работы'] = soup_vacancy.find('div', {'class' : 'info-table__text'}, itemprop="experienceRequirements").text.strip()
            vacancy_info['Образование'] = soup_vacancy.find('div', {'class' : 'info-table__text'}, itemprop="educationRequirements").text.strip()

        vacancy_info['Ссылка'] = link
        
        vacancy_data.append(vacancy_info)


    df = pd.DataFrame(vacancy_data)
    df.to_csv('rabota_ru.csv')