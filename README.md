# DogCollars
DogCollars - проект, созданный для отслеживания бездомных собак и оказания помощи им. DogCollars был написан с использованием языка программирования Python и фреймворка FastAPI.
## Как это работает?
Создаются запросы на фреймворке FastAPI, представляющие из себя обработку данных (геолокации, текст постов, ID'шники и т.д.). К приложению подключена БД PostgreSQL, геолокация ошейников отслеживается с помощью базовой станции LoRa.
## Сценарии использования:
  - Регистрация/вход пользователя
  - Создание профилей для собак + регистрация ошейника (отображение клички, пола)
  - Вывод активных ошейников и их геолокации с обновлением в каждую минуту
  - Пост задачи для одной или нескольких собак (до 3 штук), максимум 1 задача на собаку от одного пользователя
  - Пост одной глобальной задачи (доступно главным администраторам)
  - Вывод задач для выбранной собаки
  - Вывод глобальных задач
  - Отметить задачу как выполненную (доступно, если геолокация пользователя находится в определённом радиусе от геолокации ошейника)
  - Предложить новый вид задачи (отправляется на рассмотрение главному администратору)
  - Подтвердить новый тип задачи (доступно главному администратору)
## FastAPI
  - Запрос на вход/регистрацию пользователя. Параметры: имя, фамилия, адрес почты, пароль
  - Запрос на создание профиля собаки. Параметры: кличка, ID-ошейника, пол, токен сессии
  - Запрос на получение геолокации ошейников в определённом радиусе. Параметры: координаты пользователя, радиус, токен сессии
  - Запрос на пост задачи. Параметры: токен сессии, тег заданнной задачи(Например: 1: покормить собаку, 2: погладить собаку), ID-ошейников
  - Запрос на пост глобальной задачи. Параметры: токен сессии, текст задачи
  - Запрос на вывод задач для выбранной собаки. Параметры: ID-ошейника, токен сессии
  - Запрос на вывод глобальных задач. Параметры: ID-ошейника, токен сессии
  - Запрос на отметку выполнения задачи. Параметры: токен сессии, геолокация пользователя, геолокация выбранной собаки
  - Запрос на предложение новой задачи. Параметры: токен сессии, текст новой задачи
  - Запрос на утверждение новой задачи. Параметры: токен сессии

## Для поднятия сервисов баз для локальной разработки нужно запустить команду:
```
make up
```
## Для накатывания миграций, если файла alembic.ini ещё нет, нужно запустить в терминале команду:
```
alembic init migrations
```
После этого будет создана папка с миграциями и конфигурационный файл для алембика.

В alembic.ini нужно задать адрес базы данных, в которую будем катать миграции.

Дальше идём в папку с миграциями и открываем env.py, там вносим изменения в блок, где написано:
```
from myapp import mymodel
```
Дальше вводим: ``` alembic revision --autogenerate -m "comment" - делается при любых изменениях моделей ```
Будет создана миграция
Дальше вводим: ``` alembic upgrade heads ```
Для того, чтобы во время тестов нормально генерировались миграции нужно:

сначала попробовать запустить тесты обычным образом. с первого раза все должно упасть
если после падения в папке tests создались алембиковские файлы, то нужно прописать туда данные по миграхам
если они не создались, то зайти из консоли в папку test и вызвать вручную команды на миграции, чтобы файлы появились
