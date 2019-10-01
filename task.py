import json
from datetime import datetime
import boto3
import os
import tracker_service.utils as utils
from flask import jsonify
from decimal import Decimal
import requests

logger = utils.create_logger(__name__)
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TRACKER_TABLE_NAME'])
takealot_endpoint_url = os.environ['TAKEALOT_API_URL']
# table = dynamodb.Table('tracker_service_dev')
# takealot_endpoint_url = 'https://api.takealot.com/rest/v-1-9-0/product-details/{pldcode}?platform=desktop'


def scheduled_task(event, context):
    datetimenow = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    active_products = get_active_products()
    logger.info(f'Active Products: {active_products}')

    for i in active_products:
        price = get_product_price(i)
        update_product_price_history(pld=i, price=price)
        # print(price)


def get_active_products() -> list:
    plds = []
    result = table.scan(ProjectionExpression='payload.plds')

    for i in result['Items']:
        if 'payload' in i:
            if len(i['payload']['plds']) > 0:
                for j in i['payload']['plds']:
                    if j['active'] == 'true' and j['pldcode'] not in plds:
                        plds.append(j['pldcode'])
    return plds


def get_product_price(pld: str):
    url = get_takealot_api_endpoint(pld)
    r = requests.get(url)
    response = r.json()
    parse_float = Decimal
    return response['event_data']['documents']['product']['purchase_price']


def update_product_price_history(pld: str, price: float):
    dprice = Decimal(price)
    payload = {}
    payload['last_tracked_price'] = dprice
    payload['current_price'] = dprice

    product_response = table.get_item(Key={"partition_key": f"product_{pld}", 'sort_key': pld})

    if 'Item' in product_response:
        print(f'Product Exists {pld}')
        product = product_response['Item']
        last_tracked_price = product['payload']['last_tracked_price']
        current_price = product['payload']['current_price']

        if price != current_price:
            logger.info(f'Price Change: {pld}. Price was {current_price}. Price is now {price}')
            payload['last_tracked_price'] = current_price
            payload['current_price'] = Decimal(price)
            table.update_item(Key={'partition_key': f'product_{pld}', 'sort_key': pld, },
                                       UpdateExpression="SET #payload = :val",
                                       ExpressionAttributeNames={
                                           '#payload': 'payload',
                                       },
                                       ExpressionAttributeValues={
                                           ':val': payload,
                                       }, )
        else:
            print(f'No price change - {pld}, price is {dprice}')
    else:
        print('Adding Item')
        table.put_item(Item={"partition_key": f"product_{pld}", "sort_key": pld, "payload": payload})


def get_takealot_api_endpoint(pldcode: str) -> str:
    return takealot_endpoint_url.replace('{pldcode}', pldcode)


# if __name__ == '__main__':
#     scheduled_task('', '')

