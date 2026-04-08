import requests
from api.superjob.config import APP_SECRET_KEY, USER_AGENT, BASE_URL

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


def get_vacancy(vacancy_id):
    
    headers = get_headers()
    request = f'{BASE_URL}/vacancies/{vacancy_id}/'
    
    return get_res_by_request_and_headers(request, headers)

def get_res_by_request_and_headers(request, headers):
    return requests.get(request, headers=headers).json()
