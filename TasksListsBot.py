import telebot
import json
import sys

from telebot import types

path_data = "data/"
if(sys.platform == "win32"):
    path_data = "data\\"

bot = telebot.TeleBot(sys.argv[1])


help_spa = {
	'lists': "Mevcut liste kümesini göster."
	'addList NombreLista': "Yeni bir boş liste oluşturun.",
	'delList ListName': "Mevcut bir listeyi silin.",
	'advanced': "Gelişmiş komutları göster."
}


advanced_spa = {
	'show ListName': "Tek bir listedeki görevleri göster.",
	'add ListName, TaskName': "Listeye bir görev ekleyin.",
	'addAll ListName ': "Birden çok görev ekleyin (her biri bir satırda).",
	'del ListName, TaskNumber ': "Listeden bir görevi silin.",
	'delAll ListName, 3,1,4 ': "Bir listeden birden çok görevi silin.",
	'done ListName, TaskNumber': "Bir görevi tamamlandı olarak işaretle.",
	'empty ListName ': "Bir listeden tüm görevleri kaldır.",
}


def toSentence(s):
	'''Transforma en una oración correctamente formateada.'''
	return str(s).strip().capitalize()
	
def commandRegex(command):
	return f"^/{command}( |$|@)(?i)"

def getLists(cid):
	'''Devuelve el diccionario de listas del chat especificado.'''
	dic = None
	try:
		with open(path_data + f"lists_{cid}.json", "r") as f:
			dic = json.loads(f.read())
	except:
		dic = {}
	return dic
	
def writeLists(cid, dic):
	with open(path_data + f"lists_{cid}.json", "w") as f:
		f.write(json.dumps(dic))
		
def showList(cid, listName):
	dic = getLists(cid)
	
	if(listName in dic.keys()):
		ls = dic[listName]
		res = listName + ":"
		for i in range(len(ls)):
			task = ls[i]
			res += f"\n {i}. {task}"
		if(len(ls) == 0):
			res += "\n(Bu liste boş)"
		
		keyboard = types.InlineKeyboardMarkup()
		keyboard.add(types.InlineKeyboardButton("➕",callback_data=f"addall#{listName}"), types.InlineKeyboardButton("✔️",callback_data=f"doneall#{listName}"), types.InlineKeyboardButton("🗑️",callback_data=f"delall#{listName}"))
		bot.send_message(cid, res, reply_markup=keyboard)
	elif listName == "":
		bot.send_message(cid, "Bir liste belirtmelisiniz.")
	else:
		bot.send_message(cid, f"{listName} listesi mevcut değil.")

def showWithOptions(message):
	listName = message.text.split('#')[0][:-1]
	
	showList(message.chat.id, listName)
		
def deleteTask(cid, listName, taskNumber):
	dic = getLists(cid)

	num = None
	try:
		num = int(taskNumber)
	except:
		bot.send_message(cid, "Geçerli bir iş numarası sağlamadınız.")
		return
		
	if listName in dic.keys():
		ls = dic[listName]
		try:
			taskName = ls.pop(num)
			writeLists(cid, dic)
			bot.send_message(cid, f"Belirtilen Görev \"{taskName}\" Başarı İle Silindi!")
		except:
			bot.send_message(cid, f"Aralık dışı dizini: {num}.")
	else:
		bot.send_message(cid, f"{listName} listesi mevcut değil.")
		
def doneTask(cid, listName, taskNumber):
	dic = getLists(cid)
	
	if listName in dic.keys():
		try:
			taskNumber = int(taskNumber)
			try:
				ls = dic[listName]
				taskName = ls.pop(taskNumber)
				if "Hechas" in dic.keys():
					dic["Yapılmış"].append(taskName)
				else:
					dic["Yapılmış"] = [taskName]
				writeLists(cid, dic)
				bot.send_message(cid, f"Görev \ "{taskName} \" Tamamlandı Olarak İşaretlendi.")
			except IndexError:
				bot.send_message(cid, "Aralık dışı dizini.")
			except Exception as e:
				bot.send_message(cid, "HATA!")
				print(e)
		except:
			bot.send_message(cid, "Yapılan görev listesinde dizini belirtmelisiniz.")
	else:
		bot.send_message(cid, f"{listName} listesi mevcut değil.")

def addAll(cid, listName, tasks):	
	dic = getLists(cid)
	if listName in dic.keys():
		ls = dic[listName]
		c = 0
		for taskName in tasks:
			taskName = toSentence(taskName)
			if(len(taskName) >= 3):
				ls.append(taskName)
				c += 1
		writeLists(cid,dic)
		bot.send_message(cid, f"Seçilen Listeye\"{listName}\"{c} Tane Görev Eklendi.")
	else:
		bot.send_message(cid, f"{listName} listesi mevcut değil.")
		
def delAll(cid, listName, indices):
	indices = sorted([int(i.strip()) for i in indices], reverse=True)
	for i in indices:
		deleteTask(cid, listName, i)

def doneAll(cid, listName, indices):
	indices = sorted([int(i.strip()) for i in indices], reverse=True)
	for i in indices:
		doneTask(cid, listName, i)

@bot.message_handler(regexp=commandRegex("start"))
def command_start(message):
	'''Realiza el saludo inicial.'''
	user = message.from_user
	cid = message.chat.id
	ans = f"Merhaba{' ' + user.first_name if user.first_name else ''}{' ' + user.last_name if user.last_name else ''}. Tanıştığıma Memnun oldum!"
	ans += "\nTemel komutların listesine erişmek için /help yazın."
	bot.send_message(cid, ans)

@bot.message_handler(regexp=commandRegex("help"))
def command_help(message):
	'''Muestra los comandos básicos.'''
	cid = message.chat.id
	help = "Bunlar temel komutlardır:"
	for c in help_spa:
		help += f"\n*/{c}*: {help_spa[c]}"
	bot.send_message(cid, help, parse_mode='Markdown')

@bot.message_handler(regexp=commandRegex("advanced"))
def command_advanced(message):
	'''Muestra los comandos avanzados.'''
	cid = message.chat.id
	help = "Bunlar gelişmiş komutlardır:"
	for c in advanced_spa:
		help += f"\n*/{c}*: {advanced_spa[c]}"
	bot.send_message(cid, help, parse_mode='Markdown')


def showTEMP(message):
	showList(message.chat.id, message.text.split('#')[0][:-1])

@bot.message_handler(regexp=commandRegex("list(s)?"))
def command_lists(message):
	'''Muestra las listas disponibles en este chat y el número de elementos de las mismas.'''
	cid = message.chat.id
	dic = getLists(cid)
	markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
	if(dic == {}):
		bot.send_message(cid,"Henüz liste oluşturulmadı.")
	else:
		c = 0
		fila = ["","",""]
		for l in dic.keys():
			fila[c] = f"{l} #{len(dic[l])}"
			
			if(c == 2):
				c = 0
				markup.row(fila[0],fila[1],fila[2])
			else:
				c += 1
		if(c == 1):
			markup.row(fila[0])
		elif(c == 2):
			markup.row(fila[0],fila[1])
		msg = bot.send_message(cid, "Bir liste seçin", reply_markup=markup)
		bot.register_next_step_handler(msg, showWithOptions)
	
@bot.message_handler(regexp=commandRegex("addList"))
def command_addList(message):
	'''Crea una lista nueva con el nombre especificado.'''
	cid = message.chat.id
	listName = toSentence(message.text[9:])
	
	if(len(listName) >= 3):
		dic = getLists(cid)

		dic[listName] = []
		writeLists(cid,dic)
		
		bot.send_message(cid, f"Başarı İle \"{listName}\"Oluşturuldu.")
	else:
		bot.send_message(cid, "Liste adı en az 3 karakter uzunluğunda olmalıdır.")

@bot.message_handler(regexp=commandRegex("add"))
def command_add(message):
	'''Añade una única tarea a una lista dada.'''
	cid = message.chat.id
	
	partes = message.text.split(',')
	if(len(partes) < 2):
		bot.send_message(cid, "Listenin adını ve görevin adını virgülle ayırarak belirtmelisiniz. Örnek: /Add List1, Task1)
	else:
		listName = toSentence(partes[0][5:])
		taskName = toSentence(partes[1])
		dic = getLists(cid)
		
		if(len(taskName) < 3):
			bot.send_message(cid, "Görev adı en az 3 karakter uzunluğunda olmalıdır.")
		elif(not listName in dic.keys()):
			bot.send_message(cid, f"{listName} listesi mevcut değil.")
		else:
			ls = dic[listName]
			ls.append(taskName)
			writeLists(cid,dic)
			bot.send_message(cid, f"Başarı ile \"{taskName}\" seçilen listeye \"{listName}\"Eklendi")

@bot.message_handler(regexp=commandRegex("addAll"))
def command_addAll(message):
	'''Añade múltiples tareas (separadas por línea) a la lista indicada.'''
	cid = message.chat.id
	
	partes = message.text.split('\n')
	if(len(partes) < 2):
		bot.send_message(cid, "Listenin adını ve görevin adını virgülle ayırarak belirtmelisiniz. Örnek: /Add List1, Task1")
	else:
		listName = toSentence(partes[0][8:])
		tasks = partes[1:]
		addAll(cid, listName, tasks)
		
@bot.message_handler(regexp=commandRegex("show"))
def command_show(message):
	'''Muestra todas las tareas de la lista indicada.'''
	cid = message.chat.id
	
	listName = toSentence(message.text[6:])
	showList(cid, listName)

@bot.message_handler(regexp=commandRegex("delList"))
def command_delList(message):
	'''Elimina una lista y todas sus tareas asociades.'''
	cid = message.chat.id
	dic = getLists(cid)
	
	listName = toSentence(message.text[9:])
	if listName in dic.keys():
		dic.pop(listName)
		writeLists(cid, dic)
		bot.send_message(cid, f"{listName} listesi kaldırıldı.")
	elif listName == "":
		bot.send_message(cid, "Silinecek listeyi belirtmelisiniz.")
	else:
		bot.send_message(cid, f"{listName} listesi mevcut değil.")

@bot.message_handler(regexp=commandRegex("del"))
def command_del(message):
	'''Elimina una única tarea de la lista especificada.'''
	cid = message.chat.id
	dic = getLists(cid)
	
	partes = message.text.split(',')
	if(len(partes) < 2):
		bot.send_message(cid, "Listenin adını ve görev numarasını virgülle ayırarak belirtmelisiniz. Örnek: /del List1, 0")
	else:
		listName = toSentence(partes[0][5:])
		deleteTask(cid, listName, partes[1])

@bot.message_handler(regexp=commandRegex("delAll"))
def command_delAll(message):
	'''Elimina una única tarea de la lista especificada.'''
	cid = message.chat.id
	
	partes = message.text.split(',')
	if(len(partes) < 2):
		bot.send_message(cid, "Listenin adını ve görev numarasını virgülle ayırarak belirtmelisiniz. Örnek: /del List1, 0")
	else:
		listName = toSentence(partes[0][7:])
		delAll(cid,listName,partes[1:])
	
@bot.message_handler(regexp=commandRegex("(empty|clear)"))
def command_empty(message):
	'''Elimina todas las tareas de la lista especificada.'''
	cid = message.chat.id
	dic = getLists(cid)
	
	listName = toSentence(message.text[6:])
	if listName in dic.keys():
		size = len(dic[listName])
		dic[listName] = []
		writeLists(cid, dic)
		bot.send_message(cid, f"{size} Adet Görev \"{listName}\"Listesinden Kaldırıldı!")
	elif listName == "":
		bot.send_message(cid, "Listenin boş olduğunu belirtmelisiniz.")
	else:
		bot.send_message(cid, f"{listName} listesi mevcut değil.")

@bot.message_handler(regexp=commandRegex("done"))
def command_done(message):
	'''Marca como hecha una única tarea de una lista concreta.'''
	cid = message.chat.id
	
	partes = message.text.split(',')
	if(len(partes) < 2):
		bot.send_message(cid, "Listenin adını ve görev numarasını virgülle ayırarak belirtmelisiniz. Örnek: /done Listesi1, 0")
	else:
		listName = toSentence(partes[0][6:])
		taskNumber = None
		try:
			taskNumber = int(partes[1])
		except:
			bot.send_message(cid, "Geçerli bir iş numarası sağlamadınız.")
			return
		doneTask(cid, listName, taskNumber)

	
@bot.message_handler(regexp=commandRegex("id"))
def command_id(message):
	cid = message.chat.id
	bot.send_message(cid,f"Sohbet kimliğiniz : {cid}")
	
@bot.callback_query_handler(func=lambda call: True)
def handle_call(call):
	cid = call.message.chat.id
	data = call.data.split('#')
	func = data[0]
	
	markup = types.ForceReply()
	if func == "addall":
		listName = data[1]
		bot.answer_callback_query(call.id, "Success")
		msg = bot.send_message(cid, "Eklemek istediğiniz tüm görevleri ayrı satırlara yazın.", reply_markup=markup)
		bot.register_next_step_handler(msg, lambda m: addAll(cid,listName,m.text.split('\n')))
	elif func == "doneall":
		listName = data[1]
		bot.answer_callback_query(call.id, "Success")
		msg = bot.send_message(cid, "Yapılan görevlerin numaralarını virgülle ayırarak yazın.", reply_markup=markup)
		bot.register_next_step_handler(msg, lambda m: doneAll(cid,listName,m.text.split(',')))
	elif func == "delall":
		listName = data[1]
		bot.answer_callback_query(call.id, "Success")
		msg = bot.send_message(cid, "Silinecek görevlerin numaralarını virgülle ayırarak yazın.", reply_markup=markup)
		bot.register_next_step_handler(msg, lambda m: delAll(cid,listName,m.text.split(',')))
	else:
		print("Unknown callback query: " + call.data)
	
print("\nRunning TasksListsBot.py")
bot.polling()
