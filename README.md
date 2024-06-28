[<img src="https://img.shields.io/badge/Telegram-%40Me-orange">](https://t.me/gh0st1337)


![img1](.github/images/demo.png)

> 🇪🇳 README in english available [here](README-EN.md)

## Функционал  
| Функционал                                                     | Поддерживается  |
|----------------------------------------------------------------|:---------------:|
| Многопоточность                                                |        ✅        |
| Привязка прокси к сессии                                       |        ✅        |
| Рандомное время сна между кликами                              |        ✅        |
| Рандомное количество кликов за запрос                          |        ✅        |
| Поддержка tdata / pyrogram .session                            |        ✅        |


## [Настройки](https://github.com/DARKM00N1337/ShitCoinTapBot/blob/main/.env-example)
| Настройка                        | Описание                                                                |
|----------------------------------|-------------------------------------------------------------------------|
| **API_ID / API_HASH**            | Данные платформы, с которой запускать сессию Telegram (сток - Android)  |
| **SLEEP_BETWEEN_TAP**            | Время сна между чередой кликов (напр. 10, 25)                           |
| **CLICKS_FOR_SLEEP**             | Количество кликов до сна (напр. 100, 150)                               |
| **LONG_SLEEP_BETWEEN_TAP**       | Время сна для ожидания накопления энергии (напр. 6000, 7000)            |
| **SLEEP_BY_MIN_ENERGY_IN_RANGE** | Количество энергии при котором бот уйдет в долгий сон (напр. 300, 350)  |
| **SHOW_BALANCE_EVERY_TAPS**      | Каждые сколько тапов показывать баланс и энергию (напр. 20)             |
| **USE_PROXY_FROM_FILE**          | Использовать-ли прокси из файла `bot/config/proxies.txt` (True / False) |


## Установка
Вы можете скачать [**Репозиторий**](https://github.com/DARKM00N1337/ShitCoinTapBot) клонированием на вашу систему и установкой необходимых зависимостей:
```shell
~ >>> git clone https://github.com/DARKM00N1337/ShitCoinTapBot.git 
~ >>> cd ShitCoinTapBot


# Linux
~/ShitCoinTapBot >>> python3 -m venv venv
~/ShitCoinTapBot >>> source venv/bin/activate
~/ShitCoinTapBot >>> pip3 install -r requirements.txt
~/ShitCoinTapBot >>> cp .env-example .env
~/ShitCoinTapBot >>> nano .env  # Здесь вы обязательно должны указать ваши API_ID и API_HASH , остальное берется по умолчанию
~/ShitCoinTapBot >>> python3 main.py

# Windows
~/ShitCoinTapBot >>> python -m venv venv
~/ShitCoinTapBot >>> venv\Scripts\activate
~/ShitCoinTapBot >>> pip install -r requirements.txt
~/ShitCoinTapBot >>> copy .env-example .env
~/ShitCoinTapBot >>> # Указываете ваши API_ID и API_HASH, остальное берется по умолчанию
~/ShitCoinTapBot >>> python main.py
```

Также для быстрого запуска вы можете использовать аргументы, например:
```shell
~/ShitCoinTapBot >>> python3 main.py --action (1/2)
# Или
~/ShitCoinTapBot >>> python3 main.py -a (1/2)

# 1 - Создает сессию
# 2 - Запускает кликер
```


