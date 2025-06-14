# RiaParser - система агрегации данных для получения статей с [ria.ru](https://ria.ru/)
Проект представляет собой ETL-систему с REST API-сервером для получения полученной информации из базы данных. В частности, проект использует следующие технологии:
- Scrapy - как фреймворк для парсинга веб-страниц
- PostgreSQL - как базу данных
- Flask - как фреймворк для создания API-сервера
- SQLAlchemy - для взаимодейстия с базой данных посредством ORM и простых запросов
## Требования
Для работы проекта необходимы:
- Docker и docker-compose
- Любой способ подключаться к базам данных
## Установка
Установите docker и docker-compose, соберите в корневой директории проекта образы, затем запустите контейнеры:
```
docker-compose build
docker-compose up
```
## Использование
API-сервер доступен по адресу ```http://localhost:9090```. Доступны следующие endpoint'ы:
- ```/article/<id>``` - получить полную информацию по статье с id = *<id>*
- ```/articles``` - получить список статей с заданными критериями. Доступны следующие query-параметры:
  - ```tag=<tag>``` - получить все статьи с тегом *<tag>*. Можно указывать несколько тегов через запятую: ```tag=Россия,В мире```
  - ```date=<date>``` - получить все статьи, опубликованные в определенный день. День задается в формате **YYYY-MM-DD**. Если это поле не задано, используется текущий день
  - ```from=<x>&to=<y>``` - получить все статьи, опубликованные со дня *x* по день *y*. Формат дней такой же. Если эти поля не заданы, используется текущий день
  - ```limit=x&page=y``` - получить *y*-тые *x* статей. По умолчанию, y = 1, x = 10

Query-параметры можно комбинировать. Следующий запрос выведет вторые 10 статей с тегом "РТУ МИРЭА", опубликованные за июнь 2025 года:
```
http://localhost:9090/articles?tag=РТУ МИРЭА&from=2025-06-01&to=2025-06-30&page=2
```
При запросе к ```/article/<id>``` сервер вернет JSON-файл следующего формата:
```
{
  id: <id>,
  header: <Заголовок статьи>,
  content: <Текст статьи>,
  url: <Ссылка на статью на ria.ru>,
  tags: [<Теги>],
  publishing_date: <Дата публикации>
}
```
При запросе к ```/articles``` сервер вернет список JSON-файлов следующего формата:
```
[
...
{
  id: <id>,
  header: <Заголовок статьи>,
  url: <Ссылка на статью на ria.ru>,
  publishing_date: <Дата публикации>
}
...
]
```
В случае, если произошла ошибка из-за некорректно введенных данных, сервер вернет JSON-файл ```{response: "incorrect query params"}```. В случае, если тег даты пустой, он просто игнорируется.

По умолчанию, краулер запускается в начале каждого часа. Можно запустить паука немедленно средствами docker:
```
docker exec ria-crawl scrapy crawl ria
```
