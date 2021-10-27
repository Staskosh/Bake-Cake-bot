# Bake-Cake-Bot


### Installing

To get started go to terminal(mac os) or CMD (Windows)
- create virtualenv, [See example](https://python-scripts.com/virtualenv)

```bash
$python virtualenv venv
```

- clone github repository

```bash
$git clone https://github.com/Staskosh/Bake-Cake-Bot.git
```

- install packages

```bash
$pip install -r requirements.txt
```

- get the token can obtain from @BotFather in Telegram, [See example](https://telegra.ph/Awesome-Telegram-Bot-11-11)
- create the file .env end put your token in `TG_TOKEN`
- run the bot with command below and pass to your bot chat in Telegram 

```bash
$python manage.py tg_bot
```

- for Admin access to database create super user 

```bash
$python manage.py createsuperuser"

```

- run the local server and pass to `http://127.0.0.1:8000/admin` to login to admin webpage
```bash
python manage.py runserver
```

## Authors

* **Rostislav** - [Rostislav](https://github.com/Rostwik)
* **Stas Koshenkov** - [Staskosh](https://github.com/Staskosh)
* **Anna** - [Anna](https://github.com/annfike)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details


