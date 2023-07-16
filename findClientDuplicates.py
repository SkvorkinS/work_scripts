import pandas as pd

first_df = pd.read_excel('data/first_data.xls')
second_df = pd.read_excel('data/second_data.xls')

clients_df = pd.concat([first_df, second_df],ignore_index=True)

def format_phone_number(phone_number):
    digits = ''.join(filter(str.isdigit, phone_number))
    if len(digits) == 10:
        digits = '7' + digits
    formatted_number = '+{} ({}){}-{}-{}'.format(digits[:1], digits[1:4], digits[4:7], digits[7:9], digits[9:])
    return formatted_number

clients_df['Телефон'] = clients_df['Телефон'].apply(format_phone_number)

clients_df.to_csv('DATA/formatted_clients.csv')

counts = clients_df['Телефон'].value_counts()
duplicates = counts[counts > 1].index
duplicates_df = clients_df[clients_df['Телефон'].isin(duplicates)].drop_duplicates('Телефон')
print(duplicates_df.shape)
duplicates_df.to_csv('DATA/duplicates_cliets.csv')
