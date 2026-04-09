import requests
import json
import time
import pandas as pd
from config import APP_SECRET_KEY, USER_AGENT, BASE_URL


def get_headers():
    headers = {
        'X-Api-App-Id': APP_SECRET_KEY,
        'User-Agent': USER_AGENT
    }
    return headers


def get_towns(keyword=''):
    
    headers = get_headers()
    request = f'{BASE_URL}/towns/?keyword={keyword}'

    return get_res_by_request_and_headers(request, headers)


def get_regions(keyword=''):

    headers = get_headers()
    request = f'{BASE_URL}/regions/?keyword={keyword}'

    return get_res_by_request_and_headers(request, headers)

def get_catalogues():
    
    headers = get_headers()
    request = f'{BASE_URL}/catalogues/'
    
    return get_res_by_request_and_headers(request, headers)


def get_vacancies_page(page_id=0, count=100, keyword='', town=None, catalogue=None):
    
    headers = get_headers()
    request = f'{BASE_URL}/vacancies/?page={page_id}&count={count}&keyword={keyword}'

    if town is not None:
        request += f'&town={town}'

    if catalogue is not None:
        request += f'&catalogues={catalogue}'
        
    return get_res_by_request_and_headers(request, headers)

def get_vacancies_page_by_region(page_id=0, count=100, keyword='', region=None, catalogue=None):
    
    headers = get_headers()
    request = f'{BASE_URL}/vacancies/?page={page_id}&count={count}&keyword={keyword}'

    if region is not None:
        request += f'&region={region}'

    if catalogue is not None:
        request += f'&catalogues={catalogue}'
        
    return get_res_by_request_and_headers(request, headers)


def get_vacancy(vacancy_id):
    
    headers = get_headers()
    request = f'{BASE_URL}/vacancies/{vacancy_id}/'
    
    return get_res_by_request_and_headers(request, headers)

def get_company(company_id):

    headers = get_headers()
    request = f'{BASE_URL}/clients/{company_id}/'
    
    return get_res_by_request_and_headers(request, headers)

def get_metro(town_id):

    headers = get_headers()
    request = f'{BASE_URL}/metro/{town_id}/lines/'
    
    return get_res_by_request_and_headers(request, headers)

def vacancies_to_df(vacancies, region):
    rows = []
    companies_info = {}

    for v in vacancies:
        company_id = v.get('id_client')
        if company_id and company_id not in companies_info:
            companies_info[company_id] = get_company(company_id)

        company_data = companies_info.get(company_id)

        industry = None
        vacacy_count = None
        staff_count = None
        metro = []
        metro_lines = []
        metro_color_line = []
        category = []
        deteiled_categories = []

        if company_data:
            industries = company_data.get('industry')
            industry = industries[0].get('title') if industries else None
            vacacy_count = company_data.get('vacancy_count')
            staff_count = company_data.get('staff_count')
        
        if v.get('metro'):
            for m in v.get('metro'):
                metro_id = m.get('id')
                data_metro = get_metro(v.get('town').get('id'))
                line_id = 1
                for line in data_metro:
                    for station in line.get('stations'):
                        if metro_id == station.get('id'):
                            final_line = line_id
                            break
                    line_id += 1 
                metro_lines.append(data_metro[final_line-1].get('title'))
                metro_color_line.append(data_metro[final_line-1].get('color'))
                metro.append(m.get('title'))
        
        if v.get('catalogues'):
            for cat in v.get('catalogues')[0]:
                category.append(cat.get('title'))
                for det_cat in cat.get('positions'):
                    deteiled_categories.append(det_cat.get('title'))

        row = {
            'id': v.get('id'),
            'Название вакансии': v.get('profession'),
            'Минимальная зарплата': v.get('payment_from'),
            'Максимальная зарплата': v.get('payment_to'),
            'Валюта': v.get('currency'),
            'Категория': category,
            'Детальные категории': deteiled_categories,
            'Город': v.get('town', {}).get('title'),
            'Метро': metro,
            'Линия метро': metro_lines,
            'Цвет линии метро': metro_color_line,
            'Адрес': v.get('address'),
            'Id компании': v.get('id_client'),
            'Индуcтрия': industry,
            'Кол-во персонала в компании': staff_count,
            'Кол-во размещенных вакансий': vacacy_count,
            'Название компании': v.get('client', {}).get('title'),
            'Опыт': v.get('experience', {}).get('title'),
            'График работы': v.get('type_of_work',{}).get('title'),
            'Образование': v.get('education',{}).get('title'),
            'Широта': v.get('latitude'),
            'Долгота': v.get('longitude'),
            'ссылка': v.get('link')
        }
        rows.append(row)

    return pd.DataFrame(rows)

def get_res_by_request_and_headers(request, headers):
    return requests.get(request, headers=headers).json()


def main():
    output_file = 'superjob_vacancies.csv'

    cities = ['санкт-петербург','екатеринбург'] #москву не добавляем, так как она учитывается в МО
    town_ids = []

    regions = ['московская область']
    region_ids = []

    for city in cities:
        data = get_towns(city)
        objects = data.get('objects', [])
        if objects:
            town_ids.append(objects[0].get('id'))
    
    for region in regions:
        data = get_regions(region)
        region_ids.append(data.get('objects')[0].get('id'))

    catalogues_data = get_catalogues()
    cat_needed = ['it','банки', 'промышленность', 'строительство', 'ремонт', 'юриспреденция']
    cat_ids = []
    for cat in catalogues_data:
        for category in cat_needed:
            if category in cat.get('title_rus', '').lower():
                cat_ids.append(cat.get('key'))

    all_vacancies = []

    for town_id in town_ids:
        for cat_id in cat_ids:
            page = 0
            while True:
                print(cat_id, page, town_id)
                response = get_vacancies_page(page, 100, town=town_id, catalogue=cat_id)
                vacancies = response.get('objects', [])

                if not vacancies:
                    break

                all_vacancies += vacancies
                page += 1
    
    for region_id in region_ids:
        for cat_id in cat_ids:
            page = 0
            while True:
                print(cat_id, page, region_id)
                response = get_vacancies_page_by_region(page, 100, region=region_id, catalogue=cat_id)
                vacancies = response.get('objects', [])

                if not vacancies:
                    break

                all_vacancies += vacancies
                page += 1
    

    detailed_vacancies = []
    cnt = 1
    for v in all_vacancies:
        if cnt % 40 == 0:
            df = vacancies_to_df(detailed_vacancies)
            df.to_csv(output_file, index=False)
            
        id = v.get('id')
        print(cnt)
        if id:
            detailed = get_vacancy(id)
            detailed_vacancies.append(detailed)
            cnt += 1

    df = vacancies_to_df(detailed_vacancies)

    df.to_csv('superjob_vacancies.csv', index=False)

main()