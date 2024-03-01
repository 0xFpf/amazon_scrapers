import configparser, os

def save_config(asin_entry, price_entry, timer_entry, telegram_id_entry, telegram_key_entry):
    config = configparser.ConfigParser()

    config.read('config.ini')
    config['USER_INPUTS'] = {
        'asin': asin_entry.get(),
        'price': price_entry.get(),
        'timer': timer_entry.get(),
        'tg_id': telegram_id_entry.get(),
        'tg_key': telegram_key_entry.get()
    }
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    return "Success", "User inputs saved successfully!"

def load_config(asin_entry, price_entry, timer_entry, telegram_id_entry, telegram_key_entry):
    if os.path.isfile('config.ini'):
        config = configparser.ConfigParser()
        config.read('config.ini')
        if 'USER_INPUTS' in config:
            user_inputs = config['USER_INPUTS']
            asin_entry.insert(0, user_inputs.get('asin', ''))
            price_entry.insert(0, user_inputs.get('price', ''))
            timer_entry.insert(0, user_inputs.get('timer', ''))
            telegram_id_entry.insert(0, user_inputs.get('tg_id', ''))
            telegram_key_entry.insert(0, user_inputs.get('tg_key', ''))

