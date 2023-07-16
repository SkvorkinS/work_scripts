from flask import Flask, request
from request import Bitrix



application = Flask(__name__)
bitrix = Bitrix()

def check_and_create_keys(dictionary):
    keylist = ['name', 'Phone', 'tranid', 'formid', 'utm_source', 'utm_medium', 'utm_campaign']
    for key in keylist:
        if key not in dictionary:
            dictionary[key] = ''
    return dictionary

@application.route('/tilda', methods=['POST'])

def set_hook():
    #return 'test'
    print('Data recieved')
    if request.method == 'POST':
        print('Data recieved')
        data = request.form.to_dict()
        print(data)
        full_data = check_and_create_keys(data)
        full_data['deal_name'] = f'Заявка #{full_data["tranid"]} с формы:{full_data["formid"]}'
        for key, value in full_data.items():
            print(f"{key}: {value}")
        bitrix.create_bitrix24_deal(full_data['name'], full_data['Phone'], full_data['deal_name'], full_data['utm_source'], full_data['utm_medium'], full_data['utm_campaign'])
        return 'Succes'

    else:
        return 'test'


if __name__ == '__main__':
    application.run(host='0.0.0.0', port=5000, debug=True)


'''
data['name'] = request.form.get('name')
data['phone'] = request.form.get('Phone')
data['tranid'] = request.form.get('tranid')
data['formid'] = request.form.get('formid')
data['utm_source'] = request.form.get('utm_source')
data['utm_medium'] = request.form.get('utm_medium')
data['utm_campaign'] = request.form.get('utm_campaign')
data['deal_name'] = f'Заявка #{data["trainid"]} с формы:{data["formid"]}'
'''
