import requests
import pandas as pd
from bs4 import BeautifulSoup


vacancy_links = []

#нужно добавить логгирование
#парсим ссылки на вакансии(нужно сделать так чтоб нас не банило)
for i in range(1,179):
    url = f'https://www.rabota.ru/?page={i}'
    page_main = requests.get(url)

    soup_main = BeautifulSoup(page_main.text, 'html')

    for link in soup_main.find_all('a'):
        part = link.get('href')
        if part and 'vacancy' in part and '?' in part:
            vacancy_links.append(f"https://www.rabota.ru/{part.split('?')[0]}")


vacancy_data = []


#нужно добавить логгирование
#парсим информацию о вакансиях(нужно сделать так чтоб нас не банило)
for link in vacancy_links:
    url_vacancy = link
    page_vacancy = requests.get(link) 
    soup_vacancy = BeautifulSoup(page_vacancy.text, 'html')

    vacancy_info = {}

    #Название
    vacancy_info['Название вакансии'] = soup_vacancy.find('h1', {'class' : 'vacancy-card__title'}, itemprop = 'title').text.strip()

    #Зарплата
    vacancy_info['Зарплата'] = soup_vacancy.find('h3', {'class' : 'vacancy-card__salary'}).text.replace('\xa0', '')

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
    city = soup_vacancy.find('a',{'class' : "router-link-active"}, href="/", itemprop="item").text
    vacancy_info['Город'] = city

    #Категории вакансии(может работать криво)
    categories = []

    for el in soup_vacancy.find_all('span', {'itemprop': 'name'}):
        categories.append(el.text)

    if len(categories) == 5 or (len(categories) == 4 and categories[3] != vacancy_info['Название вакансии']):
        vacancy_info['Сфера'] = categories[2]
        vacancy_info['Общее название профессии'] = categories[3]
    elif len(categories) == 4 and categories[2] in vacancy_info['Название вакансии']:
        vacancy_info['Общее название профессии'] = categories[2]
    elif len(categories) == 4:
        vacancy_info['Сфера'] = categories[2]
    
    vacancy_data.append(vacancy_info)


df = pd.DataFrame(vacancy_info)
df.to_csv('rabota_ru.csv')