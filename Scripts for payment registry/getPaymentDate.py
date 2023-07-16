from datetime import datetime, timedelta


subscriptions = {}

data = """

"""
lines = data.strip().split("\n")
for line in lines:
    subscription, date = map(str.strip, line.split("\t"))
    subscriptions[subscription] = date

print(subscriptions)
# Функция для нахождения ближайшего вторника или четверга перед заданной датой
def find_payment_date(end_date):
    end_date = datetime.strptime(end_date, "%d.%m.%Y")
    while end_date.weekday() not in [1, 3]:  # 1 - вторник, 3 - четверг
        end_date -= timedelta(days=1)
    return end_date.strftime("%d.%m.%Y")

# Назначение дат оплаты для каждой подписки
for subscription, end_date in subscriptions.items():
    payment_date = find_payment_date(end_date)
    print(f"{payment_date}")
