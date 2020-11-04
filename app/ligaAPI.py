import json

import requests

from db import add_payment_history

BASE_URL_POST = 'https://api-demo-kiev.ligataxi.com/rpc'
BASE_URL_GET = 'https://api-demo-kiev.ligataxi.com/api/v1/client/company/'


def user_exists(name, password):
    response = requests.post(BASE_URL_POST, auth=(name, password))
    if not response.status_code == 401:
        return True


def send_payment(tg_id, name, password, driver_id, payment_sum):
    data ={"jsonrpc": "2.0", "method": "driver.fin_operation.create", "params": {"driver_id": driver_id, "payment": payment_sum}}
    response = requests.post(BASE_URL_POST, auth=(name, password), data=json.dumps(data)).json()
    if response.get('error'):
        return response['error']['message']

    else:
        add_payment_history(tg_id, payment_sum)

    return True, response['params']['balance']


def test():
    response = requests.get('https://api-demo-kiev.ligataxi.com/api/v1/cars/',
                            headers={
                                'api-key': 'dc268050ea54a105d09449ea3d6da156'
                            })
    print(response)
