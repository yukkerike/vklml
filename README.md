# vkMessageActionLogger
Перехват удаленных/измененных сообщений вконтакте

Начало
------------
> **[python 3.4](https://python.org/) или новее**

    $ git clone https://github.com/ikozlovsky/vkLongpollMessagesActionsLogger.git
    $ cd vkLongpollMessagesActionsLogger
    $ pip3 install -r requirements.txt

Запуск
------------
>    Передайте токен в качестве аргумента к скрипту:

    $ python3 vkLongpollLogger.py ACCESS_TOKEN

>    Либо укажите токен в __config.json__ и запустите скрипт:

    $ python3 vkLongpollLogger.py

Получить токен можно тут: http://oauth.vk.com/authorize?client_id=2685278&display=mobile&redirect_uri=https://oauth.vk.com/blank.html&scope=725086&response_type=token&v=5.101&revoke=1

>    Если вы хотите, чтобы к файлам отчёта генерировался index.html с ссылками на отчёты по дням за текущий месяц, добавьте правило для запуска __updateIndex.py__ раз в месяц в crontab, либо измените значение __false__ на __true__ ключа __createIndex__ в __config.json__.

>   Если доступ к логу есть у посторонних лиц (например, через веб-сервер), из __mesAct/vkGetVideoLink.html__ целесообразно удалить токен. 

>   Помимо прямого назначения, бота можно использовать для выполнения своих действий в ответ на события:
>   1. Измените значение __false__ на __true__ ключа __customActions__ в __config.json__.
>   1. Добавьте свои обработчики действий в файле __customActions.py__.

