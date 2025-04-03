from flask import Flask, request, jsonify
from prometheus_client import make_wsgi_app, Gauge
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from datetime import datetime
import threading
import time

def iso_to_epoch_s(date_str):
    dt = datetime.fromisoformat(date_str)  # Convert string to datetime object
    return int(dt.timestamp())  # Convert to epoch milliseconds

PORT = 5234

class WebServer(object):
    app = None
    metric_refresh_from_api_interval_seconds = 1 * 60

    def __init__(self, db, apis):
        self.app = Flask(__name__)
        self.db = db
        self.shop_apis = apis
        self.app.wsgi_app = DispatcherMiddleware(self.app.wsgi_app, {
            '/metrics': make_wsgi_app()
        })  
        self.app.route('/shopify-webhook/order-created', methods=['POST'])(self.shopify_webhook)
        self.app.route('/orders', methods=['GET'])(self.fetch_orders_db)
        self.setup_prometheus()
        self.start_background_updater()

    def start_background_updater(self):
        """
        Starts a daemon thread to update metrics in the background.
        """
        thread = threading.Thread(target=self.update_metrics, daemon=True)
        thread.start()

    def update_metrics(self):
        """
        Periodically fetches coffee sales data and updates Prometheus metrics.
        Runs in a background thread.
        """
        while True:
            comb_aggs = {}
            inventory_aggs = {}
            for api in self.shop_apis:
                comb_aggs[api.url] = api.fetch_and_aggregate_orders()
                inventory_aggs[api.nickname[api.url]] = api.fetch_and_aggregate_inventory()

            superset_items = set()
            for k, v in comb_aggs.items():
                superset_items = superset_items | set(v.keys())

            new_agg = {}
            for item in superset_items:
                merged_metric = {
                    "quantity": 0,
                    "total_weight_g": 0
                }
                for k, v in comb_aggs.items():
                    metric = v.get(item, {})
                    merged_metric['quantity'] = merged_metric['quantity'] + metric.get('quantity', 0)
                    merged_metric['total_weight_g'] = merged_metric['total_weight_g'] + metric.get('total_weight_g', 0)
                new_agg[item] = merged_metric

            for k, v in new_agg.items():
                self.bag_quantity_tracker.labels(coffee_name=k).set(v['quantity'])
                self.roasted_weight_tracker.labels(coffee_name=k).set(v['total_weight_g'])

            for site, metrics in inventory_aggs.items():
                for variant, count in metrics.items():
                    self.inventory_count.labels(coffee_variant_name=variant,site=site).set(count)

            time.sleep(WebServer.metric_refresh_from_api_interval_seconds)

    def setup_prometheus(self):
        self.bag_quantity_tracker = Gauge(
            'bags_ordered',
            'number of current unfullfilled bag orders',
            ["coffee_name"]
        )
        self.roasted_weight_tracker = Gauge(
            'weight_ordered',
            'total grams of roasted coffee ordered from all orders',
            ["coffee_name"]
        )
        self.inventory_count = Gauge(
            'inventory_count',
            'number of items left in stock for item',
            ["coffee_variant_name", "site"]
        )

    def shopify_webhook(self):
        try:
            payload = request.get_json()
            print("Received Shopify Webhook:", payload.get('id', 'no id found'))
            self.db.online_orders.insert(
                'shopify',
                payload['id'],
                iso_to_epoch_s(payload['created_at'])
            )
            for item in payload['line_items']:
                self.db.line_items.insert(
                    payload['id'],
                    item['title'],
                    item['variant_title']
                )
            print("Completed insert")
            return jsonify({"message": "Webhook processed successfully"}), 200
        except Exception as e:
            print("Error processing webhook:", str(e))
            return jsonify({"error": "Failed to process webhook"}), 400

    def fetch_orders_db(self):
        try:
            orders = self.db.online_orders.multi_find_joined_line_items_greater_than_date(1)
            return jsonify(orders), 200
        except Exception as e:
            print("Error processing webhook:", str(e))
            return jsonify({"error": "Failed to fetch orders"}), 400

    def run(self, debug=True):
        self.app.run(host='0.0.0.0', port=PORT, debug=debug)




if __name__ == '__main__':
    server = WebServer()
    server.run()