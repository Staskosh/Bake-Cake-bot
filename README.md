# Bake-Cake-Bot

Telegram bot for cake shop.   
The service allows customers to order a cake choosing size, shape, decor, sign, etc. 


## Enviroments

- create new bot in Telegram and get the token   
  (you can obtain bot from @BotFather in Telegram, [See example](https://telegra.ph/Awesome-Telegram-Bot-11-11))
- create the file .env and fill in this data:
  - TG_TOKEN
  - DEBUG
  - SECRET_KEY
  - ALLOWED_HOSTS
- create file pd.pdf with personal data agreements for customers

## Installing

To get started go to terminal(mac os) or CMD (Windows)
- create virtualenv, [See example](https://python-scripts.com/virtualenv)

- clone github repository or download the code

```bash
$git clone https://github.com/Staskosh/Bake-Cake-Bot.git
```

- install packages

```bash
$pip install -r requirements.txt
```
- if you want to deploy bot to a server please proceed the manual of the selected service for settings. This project is adjusted for Heroku.
  
- set up Database as it described below

- for Admin access to create super user 

```bash
$python manage.py createsuperuser"
```

- run the local server and pass to `http://127.0.0.1:8000/admin` to login to admin webpage
```bash
python manage.py runserver
```

- fullfill the fields according to the chapter "Models"

- run the bot with command below and pass to your bot chat in Telegram

```bash
$python manage.py tg_bot
```

## Working with Database 
- Go to the app folder

```bash
$cd Bake_Cake_bot
```

- run the following commands to migrate models into DB:
```bash
python3 manage.py makemigrations
```

```bash
$python manage.py migrate 
```

## Models

Please enter the following information into the database on the admin web page before using the bot.

- products for selling (for example: Cake)
- product_properties (for example: Cake levels, Shape etc.)
- product_parameters (for example: Cake levels contains following options: 1 level, 2 level,3 level)


P.S: Please note that the code in the tg_bot.py file has the names that you wrote on the admin page.

## Authors

* **Rostislav** - [Rostislav](https://github.com/Rostwik)
* **Stanislav** - [Staskosh](https://github.com/Staskosh)
* **Anna** - [Anna](https://github.com/annfike)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details


