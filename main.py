import pprint
import argparse

from src.schema import (
    Users,
    Cuppings,
    RoastingPlatforms,
    Beans,
    Roasts,
    CuppingsSamples,
    OnlineOrders,
    LineItems
)
from src.workflows import (
    decode_cupping_text_and_insert,
    create_bean_and_roast
)
from executors.cron import PyCronExecutor
from executors.web_server import WebServer
from connectors.database_connect import CupManagementMySQLDB
from connectors.email_connect import Gmail
from connectors.shopify_api_connect import Shopify


def connect_db():
    class CupManagementDB():
        db = None
        users = None
        cuppings = None
        roasting_platforms = None
        beans = None
        roasts = None
        cuppings_samples = None
        online_orders = None
        line_items = None

        def __init__(self):
            self.db = CupManagementMySQLDB()
            self.users = Users(self.db)
            self.cuppings = Cuppings(self.db)
            self.roasting_platforms = RoastingPlatforms(self.db)
            self.beans = Beans(self.db)
            self.roasts = Roasts(self.db)
            self.cuppings_samples = CuppingsSamples(self.db)
            self.online_orders = OnlineOrders(self.db)
            self.line_items = LineItems(self.db)
    return CupManagementDB()

def create_tables():
    db = connect_db()
    db.users.create_table()
    db.cuppings.create_table()
    db.roasting_platforms.create_table()
    db.beans.create_table()
    db.roasts.create_table()
    db.cuppings_samples.create_table()
    db.online_orders.create_table()
    db.line_items.create_table()
    db.db.close()

def seed_tables():
    db = connect_db()
    db.roasting_platforms.seed()
    db.users.insert('ming', 'mingliwood@gmail.com')
    db.db.close()

def test_insert():
    db = connect_db()
    body = '''
    1. 8.25 ripe berries peachy, 8.25 soft peach, 8 unstructured peach, 8.25 bright orange super floral [test bean]
    2. 7.75 sweet nougat caramel, 7.5 pear spiced sweet, 7.75 deep chocolate caramel apple pie, 8 sweetest [Roastronics Andrew mystery medium]
    '''
    decode_cupping_text_and_insert(body, 'ming', db)
    db.db.close()

def read_gmail_and_insert():
    db = connect_db()
    gmail = Gmail()
    cupping_logs = gmail.fetch_emails()
    pprint.pprint(cupping_logs)
    for cupping in cupping_logs:
        decode_cupping_text_and_insert(
            cupping['body'],
            cupping['from'],
            db,
            alt_id=cupping['message-id'],
            date=cupping['date-sent']
        )
    db.db.close()

def execute_cron_on_email():
    executor = PyCronExecutor(read_gmail_and_insert)
    executor.start_cron()

def start_api_server():
    db = None
    server = WebServer(db, [Shopify('moonwake-coffee-roasters'), Shopify('sruf1w-wq')])
    server.run(debug=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run specific commands.")
    parser.add_argument('function', choices=[
        'create_tables',
        'seed_tables',
        'test_insert',
        'read_gmail_and_insert',
        'execute_cron',
        'start_api_server'
    ], help="Function to execute")
    args = parser.parse_args()

    if args.function == 'create_tables':
        create_tables()
        print('completed creating tables')
    elif args.function == 'seed_tables':
        seed_tables()
        print('completed seeding tables')
    elif args.function == 'test_insert':
        test_insert()
    elif args.function == 'read_gmail_and_insert':
        read_gmail_and_insert()
    elif args.function == 'execute_cron':
        print('Starting email cron polling')
        execute_cron_on_email()
    elif args.function == 'start_api_server':
        print('Starting API server')
        start_api_server()
    elif args.function == 'hello_world':
        print('hello_world')

