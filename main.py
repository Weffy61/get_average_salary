import time
import requests
from terminaltables import AsciiTable
from environs import Env
from tqdm import tqdm
import itertools


def draw_table(statistic: dict, table_tittle):
    vacancy_table = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    for language, stats in statistic.items():
        line = [language, stats['vacancies_found'], stats['vacancies_processed'], stats['average_salary']]
        vacancy_table.append(line)
    table_instance = AsciiTable(vacancy_table, title=table_tittle)
    table_instance.justify_columns[2] = 'right'
    return table_instance.table


def get_average_salary(min_salary, max_salary):
    if min_salary and min_salary > 0 and max_salary and max_salary > 0:
        salary = (min_salary + max_salary) / 2
    elif min_salary and min_salary > 0 and not max_salary:
        salary = min_salary * 1.2
    elif not min_salary and max_salary > 0:
        salary = max_salary * 0.8
    else:
        return
    return salary


def fetch_salaries_vacancies_hh(vacancy):
    salaries = []
    moscow_city_id = 1
    days_in_month = 31
    ads_count = 100
    vacancies_count = None

    for page in itertools.count():
        page_payload = {
            'text': f'Разработчик {vacancy}',
            'area': moscow_city_id,
            'period': days_in_month,
            'per_page': ads_count,
            'page': page
        }
        response_from_each_page = requests.get('https://api.hh.ru/vacancies/', params=page_payload)
        response_from_each_page.raise_for_status()
        response = response_from_each_page.json()
        time.sleep(0.5)
        for vacant_position in response['items']:
            if vacant_position['salary'] and vacant_position['salary']['currency'] == 'RUR':
                min_salary = vacant_position['salary']['from']
                max_salary = vacant_position['salary']['to']
                salaries.append(get_average_salary(min_salary, max_salary))
        if response['page'] == response['pages'] - 1:
            vacancies_count = response['found']
            break
    return salaries, vacancies_count


def fetch_salaries_vacancies_sj(vacancy, api_key):
    salaries = []
    moscow_city_id = 4
    ads_count = 100
    vacancies_count = None
    for page in itertools.count():
        page_payload = {
            'keyword': f'Разработчик {vacancy}',
            'town': moscow_city_id,
            'count': ads_count,
            'page': page
        }
        headers = {'X-Api-App-Id': api_key}

        response_from_each_page = requests.get('https://api.superjob.ru/2.0/vacancies/', headers=headers,
                                               params=page_payload)
        response_from_each_page.raise_for_status()
        response = response_from_each_page.json()
        for vacant_position in response['objects']:
            min_salary = vacant_position['payment_from']
            max_salary = vacant_position['payment_to']
            if not min_salary and not max_salary:
                continue
            salaries.append(get_average_salary(min_salary, max_salary))
        if not response['more']:
            vacancies_count = response['total']
            break
    return salaries, vacancies_count


def get_hh_statistic(languages):
    vacancies_statistic = {}
    for language in tqdm(languages, unit='language', desc='Load Statistic Progress (HH)'):
        offered_salaries, vacancies_count = fetch_salaries_vacancies_hh(language)
        vacancies_statistic[language] = {
            'vacancies_found': vacancies_count,
            'vacancies_processed': len(offered_salaries),
            'average_salary': int(sum(offered_salaries) / len(offered_salaries))
        }
    return vacancies_statistic


def get_sj_statistic(languages, api_key):
    vacancies_statistic = {}
    for language in tqdm(languages, unit='language', desc='Load Statistic Progress (SJ)'):
        offered_salaries, vacancies_count = fetch_salaries_vacancies_sj(language, api_key)
        vacancies_statistic[language] = {
            'vacancies_found': vacancies_count,
            'vacancies_processed': len(offered_salaries),
            'average_salary': int(sum(offered_salaries) / len(offered_salaries))
        }
    return vacancies_statistic


def main():
    env = Env()
    env.read_env()
    superjob_api_key = env.str('SUPER_JOB_KEY')
    programming_languages = ['JavaScript', 'Java', 'Python', 'Ruby', 'PHP', 'C++', 'C#', 'C', 'Go']
    hh_table = draw_table(get_hh_statistic(programming_languages), 'HeadHunter Moscow')
    sj_table = draw_table(get_sj_statistic(programming_languages, superjob_api_key), 'SuperJob Moscow')
    print(hh_table)
    print(sj_table)


if __name__ == '__main__':
    main()
