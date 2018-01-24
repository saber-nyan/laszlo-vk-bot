# <p align="center">НИКТО НЕ УЙДЕТ ОБИЖЕННЫМ</p>

Бот, автоматически постящий **ПРАВИЛО ДНЯ**.
В планах — наблюдающий за его **ВЫПОЛНЕНИЕМ**. 

Создается для [Visual Noble](https://vk.com/visualnoble),
вдохновлен [этим](https://vk.com/wall-108624900_2637).

Спасибо, [Дихлорид Карбонила](https://vk.com/id370446158)!

Используется [vk_api](https://github.com/python273/vk_api),
[schedule](https://github.com/dbader/schedule),
[cson](https://github.com/avakar/pycson).

### TODO [ЗДЕСЬ](https://github.com/saber-nyan/laszlo-vk-bot/issues/1)

## Установка & настройка

Для GNU/Linux:
```bash
## Заводим virtaulenv
$ mkdir bot && cd bot
$ virtualenv3 ./venv
$ source ./venv/bin/activate

## Клонируем репозиторий
$ git clone https://github.com/saber-nyan/laszlo-vk-bot.git && cd laszlo-vk-bot
$ pip install .

## Настраиваем бота, см. ниже

## Запускаем!
$ python -m laszlo-vk-bot

## Олсо, чуть позже напишу systemd-юнит
```

Бот настраивается с помощью переменных окружения.<br/>
Их полный список можно увидеть в [config.py](./laszlo-vk-bot/config.py).

### Настройка правил (`RULES_PATH`)
Для начала работы необходимо создать список правил.<br/>
Он хранится в формате [CSON](https://github.com/bevry/cson), пример есть
в [rules_example.cson](./rules_example.cson).

Отредактируйте файл и скопируйте в место, где бот сможет его прочесть.<br/>
Кодировка обязательно должна быть `UTF-8`.

Теперь укажите путь к файлу в ENV. На Windows:
```bat
> set "LASZLO_RULES_PATH=D:\DEVELOPMENT_IS_MY_LAIFU\Workspaces\laszlo-vk-bot\rules_example.cson"
```
или на GNU/Linux:
```bash
$ export LASZLO_RULES_PATH='~/saber-nyan/Workspaces/laszlo-vk-bot/rules_example.cson'
```

### Получение `GROUP_LINK`
Это просто ссылка на вашу группу, бот сам извлечет ID.<br/>
Желательно писать без дополнительных параметров.

Вот так на Windows:
```bat
> set "LASZLO_GROUP_LINK=https://vk.com/visualnoble"
```
или на GNU/Linux:
```bash
$ export LASZLO_GROUP_LINK='https://vk.com/visualnoble'
```

### Получение `ACCESS_TOKEN_LINK`
Здесь же все чуть сложнее.<br/>
Необходимо пройти по 
[этой](https://oauth.vk.com/authorize?client_id=6341488&redirect_uri=https://oauth.vk.com/blank.html&display=page&scope=73728&response_type=token&v=5.71&revoke=0)
ссылке и скопировать содержимое адресной строки. Верно, скопировать, хоть там предупреждали этого не делать!

Затем вставить его на Windows:
```bat
> set "LASZLO_ACCESS_TOKEN_LINK=https://oauth.vk.com/blank.html#access_token=*что-то*&expires_in=0&user_id=*кто-то*"
```
или на GNU/Linux:
```bash
$ export LASZLO_ACCESS_TOKEN_LINK='https://oauth.vk.com/blank.html#access_token=*что-то*&expires_in=0&user_id=*кто-то*'
```

Если же вы не хотите скармливать боту этот токен, то
[создайте](https://vk.com/editapp?act=create) Standalone-приложение и
[ссылку](https://vk.com/dev/implicit_flow_user) сами.<br/>
При этом обязательно должны присутствовать `scope=73728` (постинг на стену | неистекающий токен)
и `response_type=token`.

***

Другие переменные скармливаются боту аналогичным образом.
