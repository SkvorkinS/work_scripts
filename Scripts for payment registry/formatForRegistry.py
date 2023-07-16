import pyperclip

data = """



"""

lines = data.strip().split('\n')
converted_data = []

for line in lines:
    items = line.strip().split('\t')
    name = items[0]
    date_1 = items[1]
    date_2 = items[2]
    amount = int(items[3])
    new_item = ['WAZZUP', 'Сервисы IT и платформы: подписка (расход)', amount, date_2, name]
    converted_data.append(new_item)

output = ''
for item in converted_data:
    output += '\t'.join(str(value) for value in item) + '\n'

# Копирование в буфер обмена
pyperclip.copy(output.strip())
# Вывод результата для проверки
print(pyperclip.paste())
