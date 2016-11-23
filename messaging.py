import telebot
import pprint

bot = telebot.TeleBot('270442436:AAGR2t_5DNyWwU01k9SzBgCRf9OXl_gVdoc')

send_bot = telebot.TeleBot('270442436:AAGR2t_5DNyWwU01k9SzBgCRf9OXl_gVdoc')

sissas_chat = '-175861996'
test_lara = "-169286463"

@bot.message_handler(commands=['write'])
def send_welcome(message):
	try: bot.send_message(test_lara, message.text.split(" ")[1:])
	except Exception as ex: pass

@bot.message_handler(func=lambda message:  True)
def all_echo(message):
	try: bot.forward_message(sissas_chat, test_lara, message.message_id)
	except Exception as ex:	pass
	
@bot.message_handler(func=lambda message:  True)
def all_echo(message):
	try: bot.forward_message(sissas_chat, test_lara, message.message_id)
	except Exception as ex:	pass
    
#@bot.message_handler(func=lambda message: str(message.chat.id) == test_lara)
#def all_echo(message):
#    bot.send_message(sissas_chat, test_lara, message.message_id) 
    


bot.polling()
