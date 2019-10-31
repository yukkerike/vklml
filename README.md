# vkMessageActionLogger
Перехват удаленных/измененных сообщений вконтакте


Начало
------------
> **[python 3.2](https://python.org/) или новее**

    $ git clone https://github.com/ikozlovsky/vkLongpollMessagesActionsLogger.git
    $ cd vkLongpollMessagesActionsLogger
    $ pip3 install -r requirements.txt

Запуск
------------
>    Передайте токен в качестве аргумента к скрипту:

    $ python3 vkLongpollLogger.py ACCESS_TOKEN


>    Либо подставьте своё значение переменной __ACCESS_TOKEN__ в __vkLongpollLogger.py__ и запустите скрипт:

    $ python3 vkLongpollLogger.py


Получить токен можно тут: http://oauth.vk.com/authorize?client_id=2685278&display=mobile&redirect_uri=https://oauth.vk.com/blank.html&scope=725086&response_type=token&v=5.101&revoke=1



>    Если вы хотите, чтобы к файлам отчёта генерировался index.html с ссылками на отчёты по дням за текущий месяц, добавьте правило для запуска __updateIndex.py__ раз в месяц в crontab, либо измените __False__ на __True__ в строке __createIndex = False__ внутри __vkLongpollLogger.py__ (делать так я не советую, это будет вызывать чтение index.html при каждой записи в отчёт, лучше создать задание средствами системы).