# Приложение для печати ценников
## Используется в магазине Sony Centre (г. Воронеж)

> **Backend:** *Боровец Тимофей*  
> **Frontend:** *Skillbox,* *Боровец Тимофей*  
> **Version:** *2.0*  
> ***©2021-2023***

### Основная задача
Данное веб-приложение призвано упростить работу сотрудников магазина при печати 
ценников.  

### Предпосылки к созданию данного приложения
Использование сотрудниками печати ценников с помощью файла Excel приводило к 
необходимости каждый раз вносить информацию о цене, наименовании, стране 
производители и т.д. Данные действия приводили к медленной реализации простого
функционала.

### Предыдущие версии
* Первая версия данного приложения представляла собой Excel файл с макросами 
и сложными функциями для поиска информации на листе. С помощью сканера штрихкодов
сотрудники сканировали ean товаров, после чего получали на отдельных листах
разные типы ценников.  
Недостатки:  
    1. Неэффективное использование листа (на одном листе печатался только один 
  вид ценников).
    2. Трудоемкий процесс любых изменений (добавление товаров, категорий, стран
  и прочей информации)
    3. Высокая вероятность нарушения целостности файла.
* Вторая версия (Версия 1.0) была также основана на Django, но использовала в 
большей степени не возможности БД, а инструменты по работе с txt-файлами. 
Данная версия имела громоздкий код и избыточный функционал, который не доказал
свою эффективность. Код расположен на [GitHub](https://github.com/sonic-tim/price_tags).

### Изменения в текущей версии:
* Все манипуляции производятся с помощью БД.
* Полностью переработаны модули представлений, форм, моделей и перенаправлений.
* SECRET_KEY вынесен за пределы публикации на удаленных репозиториях.
* Информация и стилях объектов вынесена в css и не загромождает html-код.
* Изменены ссылки для работы с приложением.
* Переработаны шаблоны страниц, изменены названия.
* Максимально использованы инструменты Django.

## КЛЮЧЕВЫЕ МОМЕНТЫ
1. Данное веб-приложение не требует публикации при работе для сотрудников.  
Для запуска используется bat-файл, функционал которого сводится к тому, чтобы 
развернуть локальный сервер и открыть Microsoft Edge.
2. В приложении не используются UpdateView и некоторые другие view, по причине
специфичности задач.  
Например, 4 вида ценников, обновление цен из файла Excel при поступлении товаров,
а также необходимость точечного обновления цен при получении уведомления в ICQ.  
Все эти задачи было необходимо реализовать так, чтобы сотрудники прилагали 
минимум усилий для всех манипуляций.

