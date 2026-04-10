import logging

import requests
from api.headhunter.config import USER_AGENT, BASE_URL

logging.basicConfig(level=logging.INFO, filename="headhunter_api.log",filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")

def get_headers():
    headers = {
        'User-Agent': USER_AGENT
    }
    return headers


def get_areas():
    
    headers = get_headers()
    request = f'{BASE_URL}/areas'

    return get_res_by_request_and_headers(request, headers)


def get_dictionaries():
    
    headers = get_headers()
    request = f'{BASE_URL}/dictionaries'

    return get_res_by_request_and_headers(request, headers)


def get_vacancies_page(page_id=0, per_page=100, text='', area=None):
    headers = get_headers()
    request = f'{BASE_URL}/vacancies?page={page_id}&per_page={per_page}&text={text}'

    if area is not None:
        request += f'&area={area}'

    return get_res_by_request_and_headers(request, headers)


def get_vacancy(vacancy_id):
    headers = get_headers()
    request = f'{BASE_URL}/vacancies/{vacancy_id}'

    return get_res_by_request_and_headers(request, headers)


def get_res_by_request_and_headers(request, headers):
    logging.info(f"Начало отправки запроса: {request}")
    try:
        response = requests.get(request, headers=headers, timeout=20)
    except requests.RequestException:
        logging.exception(f"Ошибка, нет положительного ответа на  запрос: {request}")
        raise
    logging.info(f"Ответ успешно получен, запрос: {request}")
    return response.json()