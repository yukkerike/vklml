# vkMessageActionLogger
Перехват удаленных/измененных сообщений вконтакте

Начало
------------
> **[python 3.4](https://python.org/) или новее**

    $ git clone https://github.com/ikozlovsky/vkLongpollMessagesActionsLogger.git
    $ cd vkLongpollMessagesActionsLogger
    $ pip3 install -r requirements.txt

>    Либо скачайте всё в архиве и распакуйте (Clone or download > Download ZIP).

>   Зависимости лучше устанавливать от имени администратора. В случае с windows стоит писать не __pip3__, а __py -m pip__, и не __python3__, а __py__. 

Запуск
------------
>    Укажите токен в __config.json__ и запустите скрипт:

    $ python3 vkLongpollLogger.py

>    Либо передайте токен в качестве аргумента к скрипту:

    $ python3 vkLongpollLogger.py ACCESS_TOKEN

Получить токен можно тут: http://oauth.vk.com/authorize?client_id=2685278&display=mobile&redirect_uri=https://oauth.vk.com/blank.html&scope=725086&response_type=token&v=5.101&revoke=1

Советы по настройке
------------
>    Если вы хотите, чтобы к файлам отчёта генерировался index.html с ссылками на отчёты по дням за текущий месяц (__излишне в случае использования встроенного веб-сервера__), добавьте правило для запуска __updateIndex.py__ раз в месяц в crontab, либо измените значение __false__ на __true__ ключа __createIndex__ в __config.json__.

>   Если вы не хотите использовать встроенный веб-сервер, flask можно не устанавливать.

>   Если хотите использовать встроенный веб-сервер, измените значение ключа __enableFlaskWebServer__ на __true__. Использование простой http аутентификации настраивается ключом __useAuth__, список пользователей представлен словарём в ключе __users__, измените стандартный пароль перед использованием.

>   Если доступ к логу есть у посторонних лиц (например, через веб-сервер), целесообразно изменить ключ __placeTokenInGetVideo__ на __false__, чтобы токен было невозможно подсмотреть в файле __vkGetVideoLink.html__.

>   Помимо прямого назначения, бота можно использовать для выполнения своих действий в ответ на события:
>   1. Измените значение __false__ на __true__ ключа __customActions__ в __config.json__.
>   1. Добавьте свои обработчики действий в файле __customActions.py__.

>   Либо использовать исключительно для выполнения своих действий, отключив запись удалений/изменений сообщений переведением ключа __disableMessagesLogging__ в __false__.


>   В папке __autostart__ приложены примеры сервисов для автозапуска программы, в них требуется подкорректировать пути до __vkLongpollLogger.py__.

*   __SysV init__ – vkCacheBot -> __/etc/init.d__
*   __systemd__– vkCacheBot.service -> __/lib/systemd/system__ (~/.local/share/systemd/user/ для запуска от имени пользователя)
*  __Windows__ – vkCacheBot.vbs -> __C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup__

Обновление
------------
>   Сверьте, не изменился ли список зависимостей в __requirements.txt__. Если нужно, установите их. Замените файлы новыми версиями. Допустимо сохранить свой __config.json__, он будет автоматически обновлён, если в новой версии список поддерживаемых настроек отличается.