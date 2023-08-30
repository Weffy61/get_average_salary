# Получение статистики для разработчиков
Данный скрипт выводит статистику по заработной плате разработчиков самых популярных [ЯП](https://habr.com/post/310262/) 
на основании обьявлений [hh.ru](https://hh.ru/) и [superjob.ru](https://superjob.ru/) по г. Москва
## Установка
```commandline
git clone https://github.com/Weffy61/get_average_salary
```
## Установка зависимостей
Переход в директорию с исполняемым файлом и установка
```commandline
cd get_average_salary
```
```commandline
pip install -r requirements.txt
```
## Создание и настройка .env
Для работы вам необходимо получить API ключ на [superjob.ru](https://superjob.ru/). 
Для этого:
- Зарегистрируйтесь на [сайте](https://www.superjob.ru/auth/login/?returnUrl=https://api.superjob.ru/register/)
- Нажмите [Зарегистрировать приложение](https://api.superjob.ru/register/)
- Получите  API ключ

Создайте в корне папки `get_average_salary` файл `.env`. Откройте его для редактирования любым текстовым 
редактором.  
```djangourlpath
export SUPER_JOB_KEY = вставить superjob API Key
```
## Запуск
```commandline
python main.py
```
Вы увидите шкалу прогресса, по окончании загрузки данных получите результирующую таблицу.  
Пример таблицы: 

| Язык программирования | Вакансий найдено |  Вакансий обработано  | Средняя зарплата | 
|:---------------------:|:----------------:|:---------------------:|:----------------:|
|      JavaScript       |       2749       |          294          |      176006      | 
|         Java          |       2183       |          181          |      222043      |                  
|        Python         |       2699       |          282          |      193111      |           

## Цели проекта
Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).
