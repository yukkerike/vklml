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
>    Подставьте своё значение переменной ACCESS_TOKEN в vkLongpollLogger.py и запустите скрипт:
    
    $ python3 vkLongpollLogger.py
    
>    Либо передайте токен в качестве аргумента к скрипту:
    
    $ python3 vkLongpollLogger.py ACCESS_TOKEN


Получить токен можно тут: http://oauth.vk.com/authorize?client_id=2685278&display=mobile&redirect_uri=https://oauth.vk.com/blank.html&scope=725086&response_type=token&v=5.101&revoke=1
