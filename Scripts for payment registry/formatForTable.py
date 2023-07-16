import pyperclip

def transform_input(data):
    transformed_data = []
    for line in data:
        elements = line.replace(",", "").split("\t") # убираем запятую и разделяем строку по табуляции
        if len(elements) != 4:
            continue # пропустить пустые строки
        name = elements[0].strip()
        date_start = elements[1].strip()
        date_end = elements[2].strip()
        cost = elements[3].strip() # стоимость подписки в входных данных
        transformed_line = "Wazzup\t" + cost + "\tПродление подписки " + name + "\t" + date_end
        transformed_data.append(transformed_line)
    return transformed_data

# Входные данные
data="""

"""

data = data.strip().split("\n") # преобразование входных данных в список строк
transformed_data = transform_input(data)

pyperclip.copy('\n'.join(transformed_data))

# Вывод результата для проверки
print(pyperclip.paste())
