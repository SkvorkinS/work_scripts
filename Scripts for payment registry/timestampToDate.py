import datetime

def convert_timestamps_to_date(timestamps):
    converted_dates = []
    for ts in timestamps:
        ts = ts / 1000 # Преобразование из миллисекунд в секунды
        dt_object = datetime.datetime.fromtimestamp(ts)
        converted_dates.append(dt_object.strftime("%d.%m.%Y"))
    return converted_dates

# пример использования
timestamps = [
  1690444583332
] # примеры unix timestamp
time = convert_timestamps_to_date(timestamps)

for i in time:
    print(i)
