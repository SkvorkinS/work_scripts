import requests
from credentials import BITRIX_REST_WEBHOOK, CATEGORY_ID, STAGE_ID
class Bitrix():
    def create_bitrix24_client(self, client_name, phone):
        print('started client registration')
        api_endpoint = f'{BITRIX_REST_WEBHOOK}/crm.contact.add.json'
        client_data = {
            'fields': {
                'NAME': client_name,
                'PHONE': [{'VALUE': phone, 'VALUE_TYPE': 'WORK'}],
            },
            'params': {
                'REGISTER_SONET_EVENT': 'Y'
            }
        }

        response = requests.post(api_endpoint, json=client_data)
        if response.status_code == 200:
            client_id = response.json()['result']

            print(f"Client created successfully. Client ID: {client_id}")
            return client_id
        else:
            print(f"Failed to create client. Error: {response.text}")



    def create_bitrix24_deal(self, client_name,client_phone , deal_name, utm_source, utm_medium, utm_campaning):
        client_id = self.create_bitrix24_client(client_name, client_phone)
        api_endpoint = f'{BITRIX_REST_WEBHOOK}h/crm.deal.add.json'

        # Prepare the data for the deal
        deal_data = {
            'fields': {
                'ASSIGNED_BY_ID': '1',
                'TITLE': deal_name,
                'CATEGORY_ID': CATEGORY_ID,
                'STAGE_ID': STAGE_ID,
                'COMPANY_ID': 0,
                'CONTACT_ID': client_id,
                'OPENED': 'Y',
                'CLOSED': 'N',
                'UTM_SOURCE': utm_source,
                'UTM_MEDIUM': utm_medium,
                'UTM_CAMPAIGN': utm_campaning,
            },
            'params': {
                'REGISTER_SONET_EVENT': 'Y'
            }
        }

        # Create the deal using Bitrix24 API
        response = requests.post(api_endpoint, json=deal_data)

        # Check the response status
        if response.status_code == 200:
            deal_id = response.json()['result']
            print(f"Deal created successfully. Deal ID: {deal_id}")
        else:
            print(f"Failed to create deal. Error: {response.text}")

if __name__ == '__main__':
    name = 'TEST NAME'
    phone = '+7 (123) 456-78-91'
    trainid = '1234567:1234567891'
    formid = 'form123456789'
    utm_source = 'utm_source_test'
    utm_medium = 'utm_medium_test'
    utm_campaning = 'utm_campaning_campaning'
    deal_name = f'Заявка #{trainid} с формы:{formid}'

    Bitrix.create_bitrix24_deal(name, phone, deal_name, utm_source, utm_medium, utm_campaning)
