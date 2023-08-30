import time
import requests
from terminaltables import AsciiTable
import math
from environs import Env
from tqdm import tqdm


def count_vacancies_hh(languages):
    vacancies = {}

    for language in languages:
        payload = {
            'text': f'Разработчик {language}',
            'area': 1,
            'period': 31
        }
        vacancies[language] = {'vacancies_found': requests.get('https://api.hh.ru/vacancies/',
                                                               params=payload).json()['found']}
    return vacancies


def count_vacancies_sj(languages, api_key):
    vacancies = {}
    headers = {
        'X-Api-App-Id': api_key
    }
    for language in languages:
        payload = {
        'keyword': f'Разработчик {language}',
        'town': 4,
        'count': 100
    }
        vacancies[language] = {'vacancies_found': requests.get('https://api.superjob.ru/2.0/vacancies/',
                                                               headers=headers,
                                                               params=payload).json()['total']}
    return vacancies


def draw_table(statistic: dict, table_tittle):
    vacancy_table = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    for language, stats in statistic.items():
        raw = [language, stats['vacancies_found'], stats['vacancies_processed'], stats['average_salary']]
        vacancy_table.append(raw)
    table_instance = AsciiTable(vacancy_table, title=table_tittle)
    table_instance.justify_columns[2] = 'right'
    return table_instance.table


def predict_rub_salary(vacancy):
    salary_array = []
    payload = {
        'text': f'Разработчик {vacancy}',
        'area': 1,
        'period': 31,
        'per_page': 100
    }
    response = requests.get('https://api.hh.ru/vacancies/', params=payload)
    for page in range(response.json()['pages']):
        page_payload = {
            'text': f'Разработчик {vacancy}',
            'area': 1,
            'period': 31,
            'per_page': 100,
            'page': page
        }
        response_pagination = requests.get('https://api.hh.ru/vacancies/', params=page_payload)
        time.sleep(0.5)
        for salary in response_pagination.json()['items']:
            if salary['salary']:
                if salary['salary']['currency'] != 'RUR':
                    salary_array.append(None)
                    break
                min_salary = salary['salary']['from']
                max_salary = salary['salary']['to']
                if min_salary and max_salary:
                    salary_array.append((min_salary + max_salary) / 2)
                elif min_salary and not max_salary:
                    salary_array.append(min_salary * 1.2)
                elif not min_salary and max_salary:
                    salary_array.append(max_salary * 0.8)
            else:
                salary_array.append(None)
    return salary_array


def predict_rub_salary_for_superjob(vacancy, api_key):
    salary_array = []
    payload = {
        'keyword': f'Разработчик {vacancy}',
        'town': 4,
        'count': 100
    }
    headers = {
        'X-Api-App-Id': api_key
    }
    response = requests.get('https://api.superjob.ru/2.0/vacancies/', headers=headers, params=payload)
    page_counter = math.ceil(response.json()['total'] / 100)

    for page in range(page_counter):
        page_payload = {
            'keyword': f'Разработчик {vacancy}',
            'town': 4,
            'count': 100,
            'page': page
        }

        response_pagination = requests.get('https://api.superjob.ru/2.0/vacancies/', headers=headers,
                                           params=page_payload)
        time.sleep(1)
        for salary in response_pagination.json()['objects']:
            if salary['payment_from'] > 0 and salary['payment_to'] > 0:
                salary_array.append((salary['payment_from'] + salary['payment_to']) / 2)
            elif salary['payment_from'] > 0 and salary['payment_to'] == 0:
                salary_array.append(salary['payment_from'] * 1.2)
            elif salary['payment_from'] == 0 and salary['payment_to'] > 0:
                salary_array.append(salary['payment_to'] * 0.8)
            else:
                salary_array.append(None)
    return salary_array


def get_hh_statistic(languages):
    vacancies_info_hh = count_vacancies_hh(languages)
    for language in tqdm(languages, unit='language', desc='Load Statistic Progress (HH)'):
        average_salary = []
        for amount in predict_rub_salary(language):
            if amount:
                average_salary.append(amount)
        vacancies_info_hh[language]['vacancies_processed'] = len(average_salary)
        vacancies_info_hh[language]['average_salary'] = int(sum(average_salary) / len(average_salary))
    print()
    return vacancies_info_hh


def get_sj_statistic(languages, api_key):
    vacancies_info_sj = count_vacancies_sj(languages, api_key)
    for language in tqdm(languages, unit='language', desc='Load Statistic Progress (SJ)'):
        average_salary = []
        for amount in predict_rub_salary_for_superjob(language, api_key):
            if amount:
                average_salary.append(amount)
        vacancies_info_sj[language]['vacancies_processed'] = len(average_salary)
        vacancies_info_sj[language]['average_salary'] = int(sum(average_salary) / len(average_salary))
    return vacancies_info_sj


def main():
    env = Env()
    env.read_env()
    superjob_api_key = env.str('SUPER_JOB_KEY')
    programming_languages = ['JavaScript', 'Java', 'Python', 'Ruby', 'PHP', 'C++', 'C#', 'C', 'Go']
    sj_table = draw_table(get_sj_statistic(programming_languages, superjob_api_key), 'SuperJob Moscow')
    hh_table = draw_table(get_hh_statistic(programming_languages), 'HeadHunter Moscow')
    print(hh_table)
    print()
    print(sj_table)


if __name__ == '__main__':
    main()
