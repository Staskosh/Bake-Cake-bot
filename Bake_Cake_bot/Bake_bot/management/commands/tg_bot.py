# @BakeCakeBot
TG_TOKEN = '2087101616:AAEhpiKxkxaImTkIvEvy8hV1MiAlpxcIr_4'
from environs import Env

from django.core.management.base import BaseCommand
from django.db.models import F
from Bake_bot.models import Customer, Product, Productproperties, Product_parameters, Order

import logging
from datetime import datetime, timedelta

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, KeyboardButton
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

(
    MAIN,  # основное меню
    PD,  # добавляем ПД в БД, def add_pd
    CONTACT,  # добавляем контакты в БД, def add_contact
    LOCATION,  # добавляем адрес в БД, def add_address
    ORDER,  # БОТ - собрать торт, def make_cake
    OPTION1,  # записывает опцию 'Количество уровней', предлагает опцию 'Форма', def choose_option1
    OPTION2,  # записывает опцию 'Форма', предлагает опцию 'Топпинг', def choose_option2
    OPTION3,  # записывает опцию 'Топпинг', предлагает опцию 'Ягоды', def choose_option3
    OPTION4,  # записывает опцию 'Ягоды', предлагает опцию 'Декор', def choose_option4
    OPTION5,  # записывает опцию 'Декор', предлагает опцию 'Надпись', def choose_option5
    OPTION6,  # записывает опцию 'Надпись', предлагает опцию 'Коммент', def choose_option6
    OPTION7,  # записывает опцию 'Комментарии', предлагает опцию 'Адрес', def choose_option7
    OPTION8,  # записывает опцию 'Адрес', предлагает опцию 'Дата и время доставки', def choose_option8
    CONFIRM_ORDER,  # записывает опцию 'Дата и время доставки', записывает все детали заказа,
    # предлагает подтвердить заказ, def confirm_order
    SEND_ORDER,  # считает стоимость заказа, записывает заказ в БД, def send_order
) = range(15)

options = {
    '1 уровень': 400,
    '2 уровня': 750,
    '3 уровня': 1100,
    'Квадрат': 600,
    'Круг': 400,
    'Прямоугольник': 1000,
    'Без декора': 0,
    'Фисташки': 300,
    'Безе': 400,
    'Фундук': 350,
    'Пекан': 300,
    'Маршмеллоу': 200,
    'Марципан': 280,
    'Надпись': 500,
}

# кнопки
main_keyboard = [
    [KeyboardButton('Собрать торт'), KeyboardButton('Ваши заказы')]
]


# БОТ - начало
def start(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    try:
        Customer.objects.get(external_id=update.message.chat_id)
        update.message.reply_text(
            f' Здравствуйте, {user.first_name}! '
            ' Вас приветствует сервис "Изготовление тортов на заказ"! '
            ' Выберите ингредиенты, форму, основу, надпись, а мы привезем готовый торт к вашему празднику.',
            reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
    except:
        update.message.reply_text(
            f' Здравствуйте, {user.first_name}! '
            ' Вас приветствует сервис "Изготовление тортов на заказ"! '
            ' Вы у нас впервые? Давайте зарегистрируемся. ',
        )
    # добавляем юзера в ДБ, проверяем есть ли пд, контакт и адрес
    is_contact, is_address, is_pd = add_user_to_db(update.message.chat_id, user)
    if not is_pd:
        # with open("../pd.pdf", 'rb') as file:
        #     context.bot.send_document(chat_id=update.message.chat_id, document=file)
        reply_keyboard = [['Принять', 'Отказаться']]
        update.message.reply_text(
            text='Для заказа нужно ваше согласие на обработку персональных данных',
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, resize_keyboard=True
            ),
        )
        return PD
    if not is_contact:
        update.message.reply_text(
            text=(f'Напишите, пожалуйста, телефон для связи.')
        )
        return CONTACT
    if not is_address:
        update.message.reply_text(
            text=(f'Напишите, пожалуйста, адрес для доставки.')
        )
        return LOCATION

    update.message.reply_text('Что желаете?',
                              reply_markup=ReplyKeyboardMarkup(
                                  main_keyboard, one_time_keyboard=True,
                                  resize_keyboard=True, input_field_placeholder='Что желаете?'
                              ),
                              )
    return ORDER


# добавляем юзера в ДБ
def add_user_to_db(chat_id, user):
    customer, _ = Customer.objects.get_or_create(external_id=chat_id)

    logger.info(f'Get profile {customer}')
    customer.first_name = user.first_name
    customer.last_name = user.last_name or '-'
    customer.save()

    logger.info(f'Update_user {customer.external_id} '
                f'first_name {customer.first_name} '
                f'last_name {customer.last_name} '
                f'contact {customer.phone_number} '
                f'address {customer.home_address} ')
    return customer.phone_number, customer.home_address, customer.GDPR_status


# добавляем ПД в БД
def add_pd(update, context):
    customer = Customer.objects.get(external_id=update.message.chat_id)
    answer = update.message.text
    if answer == 'Принять':
        customer.GDPR_status = True
        update.message.reply_text(
            f'Добавлено согласие на обработку данных.',
        )
        logger.info(f'Пользователю {customer.external_id}'
                    f'Добавлено согласие на обработку данных: {customer.GDPR_status}')
        customer.save()
        if not customer.phone_number:
            update.message.reply_text(
                text='У меня нет вашего телефона, напишите, пожалуйста.',
            )
            return CONTACT
    elif answer == 'Отказаться':
        update.message.reply_text(
            f'Извините, без согласия на обработку данных заказы невозможны.',
        )
        return PD


# добавляем контакты в БД
def add_contact(update, context):
    customer = Customer.objects.get(external_id=update.message.chat_id)
    customer.phone_number = update.message.text
    customer.save()
    update.message.reply_text(
        f'Добавлен контакт для связи: {customer.phone_number}',
    )
    logger.info(f'Пользователю {customer.external_id}'
                f'добавлен контакт {customer.phone_number}')
    if not customer.home_address:
        update.message.reply_text(
            text='Напишите, пожалуйста, адрес для доставки.',
        )
        return LOCATION
    return MAIN


# добавляем адрес в БД
def add_address(update: Update, context):
    customer = Customer.objects.get(external_id=update.message.chat_id)
    customer.home_address = update.message.text
    customer.save()
    update.message.reply_text(
        f'Добавлен адрес доставки: {customer.home_address}',
        reply_markup=ReplyKeyboardMarkup(
            main_keyboard, resize_keyboard=True, one_time_keyboard=True
        )
    )
    logger.info(f'Пользователю {customer.external_id}'
                f'добавлен контакт {customer.home_address}')
    return ORDER


temp_order = {}


# БОТ - собрать торт
def make_cake(update: Update, context):
    user = update.message.from_user
    logger.info("choice of %s, %s: %s", user.first_name,
                user.id, update.message.text)
    user_input = update.effective_message.text
    if user_input == 'ГЛАВНОЕ МЕНЮ':
        update.message.reply_text(
            'Собрать новый торт или посмотреть заказы?',
            reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return MAIN
    parameters = []
    for parameter in Product_parameters.objects.filter(product_property__property_name__contains='Количество уровней'):
        parameters.append(parameter.parameter_name)
    option1_keyboard = [parameters, ['ГЛАВНОЕ МЕНЮ']]
    update.message.reply_text(
        'Начнем! Выберите количество уровней',
        reply_markup=ReplyKeyboardMarkup(option1_keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return OPTION1


# записывает опцию 'Количество уровней', предлагает опцию 'Форма'
def choose_option1(update: Update, context: CallbackContext):
    user_input = update.effective_message.text
    context.user_data['Количество уровней'] = user_input

    if user_input == 'ГЛАВНОЕ МЕНЮ':
        update.message.reply_text(
            'Собрать новый торт или посмотреть заказы?',
            reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return MAIN
    parameters = []
    for parameter in Product_parameters.objects.filter(product_property__property_name__contains='Форма'):
        parameters.append(parameter.parameter_name)
    option2_keyboard = [parameters, ['ГЛАВНОЕ МЕНЮ']]
    update.message.reply_text('Выберите форму',
                              reply_markup=ReplyKeyboardMarkup(option2_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))
    return OPTION2


# записывает опцию 'Форма', предлагает опцию 'Топпинг'
def choose_option2(update: Update, context: CallbackContext):
    user_input = update.effective_message.text
    context.user_data['Форма'] = user_input

    if user_input == 'ГЛАВНОЕ МЕНЮ':
        update.message.reply_text(
            'Собрать новый торт или посмотреть заказы?',
            reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return MAIN
    parameters = []
    for parameter in Product_parameters.objects.filter(product_property__property_name__contains='Топпинг'):
        parameters.append(parameter.parameter_name)
    option3_keyboard = [parameters,['ГЛАВНОЕ МЕНЮ']
    ]
    update.message.reply_text('Выберите топпинг',
                              reply_markup=ReplyKeyboardMarkup(option3_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))
    return OPTION3


# записывает опцию 'Топпинг', предлагает опцию 'Ягоды', def choose_option3
def choose_option3(update: Update, context: CallbackContext):
    user_input = update.effective_message.text
    context.user_data['Топпинг'] = user_input

    if user_input == 'ГЛАВНОЕ МЕНЮ':
        update.message.reply_text(
            'Собрать новый торт или посмотреть заказы?',
            reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return MAIN
    parameters = []
    for parameter in Product_parameters.objects.filter(product_property__property_name__contains='Ягоды'):
        parameters.append(parameter.parameter_name)
    option4_keyboard = [parameters,
        ['ГЛАВНОЕ МЕНЮ']
    ]
    update.message.reply_text('Выберите ягоды',
                              reply_markup=ReplyKeyboardMarkup(option4_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))
    return OPTION4


# записывает опцию 'Ягоды', предлагает опцию 'Декор'
def choose_option4(update: Update, context: CallbackContext):
    user_input = update.effective_message.text
    context.user_data['Ягоды'] = user_input

    if user_input == 'ГЛАВНОЕ МЕНЮ':
        update.message.reply_text(
            'Собрать новый торт или посмотреть заказы?',
            reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return MAIN
    parameters = []
    for parameter in Product_parameters.objects.filter(product_property__property_name__contains='Декор'):
        parameters.append(parameter.parameter_name)
    option5_keyboard = [parameters,
        ['ГЛАВНОЕ МЕНЮ']
    ]
    update.message.reply_text('Выберите декор',
                              reply_markup=ReplyKeyboardMarkup(option5_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))
    return OPTION5


# записывает опцию 'Декор', предлагает опцию 'Надпись'
def choose_option5(update: Update, context: CallbackContext):
    user_input = update.effective_message.text
    context.user_data['Декор'] = user_input

    if user_input == 'ГЛАВНОЕ МЕНЮ':
        update.message.reply_text(
            'Собрать новый торт или посмотреть заказы?',
            reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return MAIN
    option6_keyboard = [['Без надписи'], ['ГЛАВНОЕ МЕНЮ']]
    update.message.reply_text('Мы можем разместить на торте любую надпись, например: "С днем рождения!" '
                              'Введите текст надписи или нажмите "Без надписи"',
                              reply_markup=ReplyKeyboardMarkup(option6_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))
    return OPTION6


# записывает опцию 'Надпись', предлагает опцию 'Коммент'
def choose_option6(update: Update, context: CallbackContext):
    user_input = update.effective_message.text
    context.user_data['Надпись'] = user_input

    if user_input == 'ГЛАВНОЕ МЕНЮ':
        update.message.reply_text(
            'Собрать новый торт или посмотреть заказы?',
            reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return MAIN

    if user_input == 'Без надписи':
        options['Надпись'] = 0
    else:
        options['Надпись'] = 500

    option7_keyboard = [['Без комментариев'], ['ГЛАВНОЕ МЕНЮ']]
    update.message.reply_text('Если вы хотите оставить какие-то комментарии к заказу '
                              '- введите текст или нажмите "Без комментариев"',
                              reply_markup=ReplyKeyboardMarkup(option7_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))
    return OPTION7


# записывает опцию 'Комментарии', предлагает опцию 'Адрес'
def choose_option7(update: Update, context: CallbackContext):
    user_input = update.effective_message.text
    context.user_data['Комментарии'] = user_input

    if user_input == 'ГЛАВНОЕ МЕНЮ':
        update.message.reply_text(
            'Собрать новый торт или посмотреть заказы?',
            reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return MAIN

    option8_keyboard = [['Не менять адрес'], ['ГЛАВНОЕ МЕНЮ']]
    update.message.reply_text('Если вы хотите изменить адрес доставки - напишите его '
                              'или нажмите "Не менять адрес"',
                              reply_markup=ReplyKeyboardMarkup(option8_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))
    return OPTION8


# записывает опцию 'Адрес', предлагает опцию 'Дата и время доставки'
def choose_option8(update: Update, context: CallbackContext):
    user_input = update.effective_message.text
    context.user_data['Адрес'] = user_input

    if user_input == 'Не менять адрес':
        customer = Customer.objects.get(external_id=update.effective_user.id)
        context.user_data['Адрес'] = customer.home_address

    if user_input == 'ГЛАВНОЕ МЕНЮ':
        update.message.reply_text(
            'Собрать новый торт или посмотреть заказы?',
            reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return MAIN

    option9_keyboard = [['Как можно быстрее'], ['ГЛАВНОЕ МЕНЮ']]
    update.message.reply_text('Напишите желаемую дату и время доставки в формате "DD.MM.YYYY HH-MM" '
                              '(например 27.10.2021 10-00) или нажмите "Как можно быстрее". '
                              'При доставке в ближайшие 24 часа стоимость будет увеличена на 20%',
                              reply_markup=ReplyKeyboardMarkup(option9_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))
    return CONFIRM_ORDER


# записывает опцию 'Дата и время доставки', записывает все детали заказа, предлагает подтвердить заказ
def confirm_order(update: Update, context: CallbackContext):
    user_input = update.effective_message.text
    try:
        if user_input == 'Как можно быстрее':
            today = datetime.today()
            user_input = today.strftime("%d.%m.%Y %H-%M")
        date_time_delivery = datetime.strptime(user_input, "%d.%m.%Y %H-%M")
        context.user_data['Дата и время доставки'] = str(date_time_delivery)

        if date_time_delivery < datetime.now() + timedelta(hours=24):
            context.user_data['Срочность'] = 1
        else:
            context.user_data['Срочность'] = 0
    except ValueError:
        option9_keyboard = [['Как можно быстрее'], ['ГЛАВНОЕ МЕНЮ']]
        update.message.reply_text(
            'Время не соответствует формату "DD.MM.YYYY HH-MM" Введите заново '
            '(например: 27.10.2021 10-00) или нажмите "Как можно быстрее".',
            reply_markup=ReplyKeyboardMarkup(option9_keyboard, resize_keyboard=True, one_time_keyboard=True))
        return CONFIRM_ORDER

    if user_input == 'ГЛАВНОЕ МЕНЮ':
        update.message.reply_text(
            'Собрать новый торт или посмотреть заказы?',
            reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return MAIN

    temp_order.update(
        {
            'Количество уровней': context.user_data.get('Количество уровней'),
            'Форма': context.user_data.get('Форма'),
            'Топпинг': context.user_data.get('Топпинг'),
            'Ягоды': context.user_data.get('Ягоды'),
            'Декор': context.user_data.get('Декор'),
            'Надпись': context.user_data.get('Надпись'),
            'Комментарии': context.user_data.get('Комментарии'),
            'Адрес': context.user_data.get('Адрес'),
            'Дата и время доставки': context.user_data.get('Дата и время доставки'),
            'Срочность': context.user_data.get('Срочность'),
        }
    )
    order_keyboard = [['Да', 'Нет'], ['ГЛАВНОЕ МЕНЮ']]
    update.message.reply_text('Заказать торт?',
                              reply_markup=ReplyKeyboardMarkup(order_keyboard, resize_keyboard=True,
                                                               one_time_keyboard=True))
    return SEND_ORDER


# считает стоимость заказа, записывает заказ в БД
def send_order(update: Update, context: CallbackContext):
    user_input = update.effective_message.text

    if user_input == 'ГЛАВНОЕ МЕНЮ':
        update.message.reply_text(
            'Собрать новый торт или посмотреть заказы?',
            reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return MAIN

    elif user_input == 'Нет':
        update.message.reply_text(
            'Собрать новый торт или посмотреть заказы?',
            reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return MAIN

    if user_input == 'Да':
        total_price = 0
        for option in temp_order.values():
            try:
                total_price += options.get(option)
            except:
                pass
        total_price += options['Надпись']
        if context.user_data['Срочность'] == 1:
            total_price *= 1.2

        order_keyboard = [['Собрать торт'], ['ГЛАВНОЕ МЕНЮ']]
        update.message.reply_text(
            f'Заказ принят! Стоимость вашего заказа {total_price} руб.',
            reply_markup=ReplyKeyboardMarkup(order_keyboard, resize_keyboard=True, one_time_keyboard=True))
        logger.info(f"Итоговая цена {total_price} "
                    f'Выбранные опции {temp_order}')
        # create_new_order(update.message.chat_id, str(temp_order), total_price)
    return ORDER


# создаем заказ в БД
def create_new_order(chat_id, details, price):
    сustomer = Customer.objects.get(external_id=chat_id)
    order = Order.objects.create(
        сustomer=сustomer,
        description=details,
        price=price,
    )
    order.save
    temp_order.clear()


# БОТ - команда стоп
def stop(update, context):
    user = update.effective_user
    update.message.reply_text(f'До свидания, {user.first_name}!')
    return ConversationHandler.END


# БОТ - нераспознанная команда
def unknown(update, context):
    reply_keyboard = [['ГЛАВНОЕ МЕНЮ']]
    update.message.reply_text(
        'Извините, не понял, что вы хотели этим сказать, начнем сначала',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        )
    )
    return MAIN


def error(bot, update, error):
    logger.error('Update "%s" caused error "%s"', update, error)
    return MAIN


class Command(BaseCommand):
    help = 'Телеграм-бот'

    def handle(self, *args, **options):
        # Create the Updater and pass it your bot's token.
        updater = Updater(TG_TOKEN)

        # Get the dispatcher to register handlers
        dispatcher = updater.dispatcher

        # Add conversation handler with the states CHOICE, TITLE, PHOTO, CONTACT, LOCATION
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                MAIN: [
                    MessageHandler(Filters.regex('^Собрать торт$'),
                                   make_cake),
                    MessageHandler(Filters.regex('^Посмотреть заказы$'),
                                   make_cake),
                    MessageHandler(Filters.text & ~Filters.command,
                                   unknown)
                ],
                PD: [MessageHandler(Filters.text & ~Filters.command, add_pd)],
                CONTACT: [MessageHandler(Filters.text & ~Filters.command, add_contact)],
                LOCATION: [MessageHandler(Filters.text & ~Filters.command, add_address)],
                ORDER: [MessageHandler(Filters.text & ~Filters.command, make_cake)],
                OPTION1: [MessageHandler(Filters.text & ~Filters.command, choose_option1)],
                OPTION2: [MessageHandler(Filters.text & ~Filters.command, choose_option2)],
                OPTION3: [MessageHandler(Filters.text & ~Filters.command, choose_option3)],
                OPTION4: [MessageHandler(Filters.text & ~Filters.command, choose_option4)],
                OPTION5: [MessageHandler(Filters.text & ~Filters.command, choose_option5)],
                OPTION6: [MessageHandler(Filters.text & ~Filters.command, choose_option6)],
                OPTION7: [MessageHandler(Filters.text & ~Filters.command, choose_option7)],
                OPTION8: [MessageHandler(Filters.text & ~Filters.command, choose_option8)],
                CONFIRM_ORDER: [MessageHandler(Filters.text & ~Filters.command, confirm_order)],
                SEND_ORDER: [MessageHandler(Filters.text & ~Filters.command, send_order)],

            },
            fallbacks=[CommandHandler('stop', stop)],
        )

        dispatcher.add_handler(conv_handler)
        dispatcher.add_error_handler(error)

        # Start the Bot
        updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()
