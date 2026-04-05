import requests
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

#нужно добавить логгирование
#парсим информацию о вакансиях(нужно сделать так чтоб нас не банило)
for link in vacancy_links:
    url_vacancy = link
    page_vacancy = requests.get(link) 
    soup_vacancy = BeautifulSoup(page_vacancy.text, 'html')

    vacancy_info = {}

    vacancy_info['Название вакансии'] = soup_vacancy.find('h1', {'class' : 'vacancy-card__title'}, itemprop = 'title').text.strip()

    vacancy_info['Зарплата'] = soup_vacancy.find('h3', {'class' : 'vacancy-card__salary'}).text.replace('\xa0', '')

    skills = []

    for skill in soup_vacancy.find_all('div', {'class' : 'vacancy-card__skills-item'}):
        skills.append(skill.text.strip())

    vacancy_info['Требуемые новыки'] = skills