import os
import json
import requests


class Shopify(object):
    def __init__(self, shop_name):
        self.access_token = None
        self.url = "https://{}.myshopify.com/admin/api/2024-01/graphql.json".format(shop_name)

        current_file_path = os.path.abspath(__file__)
        current_folder = os.path.dirname(current_file_path)
        creds_path = "{}/shopify_keys.json".format(current_folder)
        with open(creds_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            self.access_token = data.get(shop_name, None) 

    def fetch_unfullfilled_orders(self):
        headers = {
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json"
        }
        payload = {
            "query": "query { orders(first: 250, reverse: true, query: \"fulfillment_status:unfulfilled\", sortKey: CREATED_AT) { edges { node { id name createdAt totalPriceSet { shopMoney { amount currencyCode } } lineItems(first: 250) { edges { node { title quantity variant { id title sku } } } } fulfillmentOrders(first: 5) { edges { node { status } } } } } pageInfo { hasPreviousPage hasNextPage startCursor endCursor } } }"
        }
        response = requests.post(self.url, json=payload, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"GraphQL Query Failed: {response.status_code}, {response.text}")

    def fetch_and_aggregate_orders(self):
        print('executing shopify fetch')
        raw_orders = self.fetch_unfullfilled_orders()

        aggregate_items = {}
        for order in raw_orders['data']['orders']['edges']:
            if order['node']['fulfillmentOrders']['edges'][0]['node']['status'] != 'OPEN':
                # filters out ready for pickup orders
                continue
            for item in order['node']['lineItems']['edges']:
                title = item['node']['title']
                qty = item['node']['quantity']
                if not item['node']['variant']:
                    weight = ''
                else:
                    weight = item['node']['variant']['title'] # 'title': '227g / 8oz' or 'title': '1kg'
                try:
                    if 'kg' in weight:
                        weight_parsed = int(weight.split('kg')[0]) * 1000
                    else:
                        weight_parsed = int(weight.split('g')[0])
                except:
                    weight_parsed = 0
                if not aggregate_items.get(title):
                    aggregate_items[title] = {'quantity': 0, 'total_weight_g': 0}
                aggregate_items[title]['quantity'] = aggregate_items[title]['quantity'] + qty
                aggregate_items[title]['total_weight_g'] = aggregate_items[title]['total_weight_g'] + weight_parsed

        return aggregate_items
      

if __name__=='__main__':
    shop = Shopify('moonwake-coffee-roasters')
    shop.fetch_and_aggregate_orders()