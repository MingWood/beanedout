import datetime


class Table(object):
    def __init__(self, db):
        self.db = db

    def create_table(self):
        self.db.execute_sql(self._create_statement())

    def insert_into_table(self, params):
        return self.db.execute_sql(self._insert_statement(), params)

class Users(Table):
    def _create_statement(self):
        return '''
        CREATE TABLE IF NOT EXISTS `users` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `name` varchar(255) COLLATE utf8_bin NOT NULL,
        `email` varchar(255) COLLATE utf8_bin NOT NULL,
        `date_added_epoch_s` int(11) NOT NULL,
        PRIMARY KEY (`id`),
        UNIQUE (name)
        );
        '''

    def _insert_statement(self):
        return '''
        INSERT INTO `users` (`name`, `email`, `date_added_epoch_s`) VALUES (%s, %s, %s)
        '''

    def _find_by_name_statement(self):
        return '''
        SELECT id from users where name like %s;
        '''

    def _find_by_email_statement(self):
        return '''
        SELECT id from users where email like %s;
        '''

    def insert(self, name, email):
        self.insert_into_table((name, email, datetime.datetime.now().timestamp()))

    def find_id_by_name(self, name):
        id = self.db.execute_sql(self._find_by_name_statement(), name, fetch=True)
        return id[0]['id']

    def find_id_by_email(self, email):
        id = self.db.execute_sql(self._find_by_email_statement(), email, fetch=True)
        return id[0]['id']


class Cuppings(Table):
    def _create_statement(self):
        return '''
        CREATE TABLE IF NOT EXISTS `cuppings` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `title` varchar(255) COLLATE utf8_bin NOT NULL,
        `date_epoch_s` int(11) NOT NULL,
        `notes` varchar(255) COLLATE utf8_bin,
        `alt_id` varchar(255) COLLATE utf8_bin NOT NULL,
        PRIMARY KEY (`id`),
        UNIQUE (alt_id)
        );
        '''

    def _insert_statement(self):
        return '''
        INSERT INTO `cuppings` (`title`, `date_epoch_s`, `notes`, `alt_id`) VALUES (%s, %s, %s, %s)
        '''

    def _find_by_alt_id_statement(self):
        return '''
        SELECT id from cuppings where alt_id = %s;
        '''

    def insert(self, title, notes='', alt_id=''):
        return self.insert_into_table((
            title,
            datetime.datetime.now().timestamp(),
            notes,
            alt_id
        ))

    def find_id_by_alt_id(self, alt_id):
        id = self.db.execute_sql(self._find_by_alt_id_statement(), alt_id, fetch=True)
        return id[0]['id']


class RoastingPlatforms(Table):
    platforms = {
        'roest-sagvag': {
            'id': 1,
            'link': 'https://front.roestcoffee.com/'
        },
        'roest-p16_1214': {
            'id': 2,
            'link': 'https://front.roestcoffee.com/'
        },
        'lorings7-mwhq': {
            'id': 3,
            'link': 'https://docs.google.com/spreadsheets/d/1QMYCa4FDj_LmK5ZYuIKKlfCfhbCnvOx-Q_bDydHsabI/edit?gid=345643284#gid=345643284'
        }
    }
    def _create_statement(self):
        return '''
        CREATE TABLE IF NOT EXISTS `roasting_platforms` (
        `id` int(11) NOT NULL,
        `name` varchar(255) COLLATE utf8_bin NOT NULL,
        `date_added_epoch_s` int(11) NOT NULL,
        `link_to_roast_details` varchar(255) COLLATE utf8_bin,
        PRIMARY KEY (`id`)
        );
        '''

    def _insert_statement(self):
        return '''
        INSERT INTO `roasting_platforms` (`id`, `name`, `date_added_epoch_s`, `link_to_roast_details`) VALUES (%s, %s, %s, %s)
        '''

    def insert(self, id, name, link_to_roast_details=''):
        self.insert_into_table((
            id,
            name,
            datetime.datetime.now().timestamp(),
            link_to_roast_details
        ))
    
    def seed(self):
        for platform, spec in RoastingPlatforms.platforms.items():
            self.insert(spec['id'], platform, spec['link'])

class Beans(Table):
    def _create_statement(self):
        return '''
        CREATE TABLE IF NOT EXISTS `beans` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `name` varchar(255) COLLATE utf8_bin NOT NULL,
        `date_added_epoch_s` int(11) NOT NULL,
        PRIMARY KEY (`id`)
        );
        '''
    def _insert_statement(self):
        return '''
        INSERT INTO `beans` (`name`, `date_added_epoch_s`) VALUES (%s, %s)
        '''

    def insert(self, name):
        return self.insert_into_table((name, datetime.datetime.now().timestamp()))


class Roasts(Table):
    def _create_statement(self):
        return '''
        CREATE TABLE IF NOT EXISTS `roasts` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `name` varchar(255) COLLATE utf8_bin,
        `notes` varchar(255) COLLATE utf8_bin,
        `roast_level` varchar(255) COLLATE utf8_bin DEFAULT "light",
        `grams_in` int(11),
        `grams_out` int(11),
        `date_roasted_epoch_s` int(11) NOT NULL,
        `roasting_platform_id` int(11) NOT NULL,
        `bean_id` int(11) NOT NULL,
        PRIMARY KEY (`id`),
        Foreign Key(`roasting_platform_id`) references roasting_platforms(`id`),
        Foreign Key(`bean_id`) references beans(`id`)
        );
        '''
    def _insert_statement(self):
        return '''
        INSERT INTO `roasts` (
        `bean_id`,
        `name`,
        `roast_level`,
        `grams_in`,
        `grams_out`,
        `date_roasted_epoch_s`,
        `roasting_platform_id`,
        `notes`
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        '''

    def _find_by_name_statement(self):
        return '''
        SELECT id from roasts where name like %s;
        '''

    def find_id_by_name(self, name):
        id = self.db.execute_sql(self._find_by_name_statement(), name, fetch=True)
        return id[0]['id']

    def insert(
        self,
        bean_id,
        name,
        roast_level='light',
        grams_in=0,
        grams_out=0,
        date_roasted_epoch_s=0,
        roasting_platform_id=1,
        notes=''):
        return self.insert_into_table((
            bean_id,
            name,
            roast_level,
            grams_in,
            grams_out,
            date_roasted_epoch_s,
            roasting_platform_id,
            notes
        ))


class CuppingsSamples(Table):
    def _create_statement(self):
        return '''
        CREATE TABLE IF NOT EXISTS `cuppings_samples` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `order_id` int(11),
        `cupping_id` int(11) NOT NULL,
        `user_id` int(11) NOT NULL,
        `roast_id` int(11) NOT NULL,
        `brew_style` varchar(255) COLLATE utf8_bin DEFAULT "cupping",
        `score_fragrance` float(4,2),
            `notes_frangrance` varchar(255) COLLATE utf8_bin,
        `score_aroma` float(4,2),
            `notes_aroma` varchar(255) COLLATE utf8_bin,
        `score_flavor` float(4,2),
            `notes_flavor` varchar(255) COLLATE utf8_bin,
        `score_aftertaste` float(4,2),
            `notes_aftertaste` varchar(255) COLLATE utf8_bin,
        `score_acidity` float(4,2),
            `notes_acidity` varchar(255) COLLATE utf8_bin,
        `score_body` float(4,2),
            `notes_body` varchar(255) COLLATE utf8_bin,
        `score_balance` float(4,2),
            `notes_balance` varchar(255) COLLATE utf8_bin,
        `score_overall` float(4,2),
            `notes_overall` varchar(255) COLLATE utf8_bin,
        `defect_faults_modifier` int(11) DEFAULT 0,
        PRIMARY KEY (`id`),
        Foreign Key(`cupping_id`) references cuppings(`id`),
        Foreign Key(`roast_id`) references roasts(`id`),
        Foreign Key(`user_id`) references users(`id`)
        );
        '''

    def _insert_statement(self):
        return '''
        INSERT INTO `cuppings_samples` (
        `order_id`,
        `cupping_id`,
        `user_id`,
        `roast_id`,
        `score_fragrance`,
            `notes_frangrance`,
        `score_aroma`,
            `notes_aroma`,
        `score_flavor`,
            `notes_flavor`,
        `score_aftertaste`,
            `notes_aftertaste`,
        `score_acidity`,
            `notes_acidity`,
        `score_body`,
            `notes_body`,
        `score_balance`,
            `notes_balance`,
        `score_overall`,
            `notes_overall`,
        `defect_faults_modifier`,
        `brew_style`
        )
        VALUES (%s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s,
        %s, %s)
        '''

    def insert(
        self,
        order_id,
        cupping_id,
        user_id,
        roast_id,
        score_fragrance,
        notes_frangrance,
        score_aroma,
        notes_aroma,
        score_flavor,
        notes_flavor,
        score_aftertaste,
        notes_aftertaste,
        score_acidity,
        notes_acidity,
        score_body,
        notes_body,
        score_balance,
        notes_balance,
        score_overall,
        notes_overall,
        defect_faults_modifier=0,
        brew_style='cupping'):
        return self.insert_into_table((
            order_id,
            cupping_id,
            user_id,
            roast_id,
            score_fragrance,
            notes_frangrance,
            score_aroma,
            notes_aroma,
            score_flavor,
            notes_flavor,
            score_aftertaste,
            notes_aftertaste,
            score_acidity,
            notes_acidity,
            score_body,
            notes_body,
            score_balance,
            notes_balance,
            score_overall,
            notes_overall,
            defect_faults_modifier,
            brew_style
        ))

class OnlineOrders(Table):
    def _create_statement(self):
        # {} -> "id": 6388378009884,
        # {} -> "created_at": "2025-04-01T01:57:54-04:00",
        return '''
        CREATE TABLE IF NOT EXISTS `online_orders` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `platform` varchar(64) COLLATE utf8_bin NOT NULL,
        `order_id` bigint(24) NOT NULL,
        `date_added_epoch_s` int(11) NOT NULL,
        `order_created_at` int(11) NOT NULL,
        PRIMARY KEY (`id`),
        UNIQUE (order_id)
        );
        '''

    def _insert_statement(self):
        return '''
        INSERT INTO `online_orders` (`platform`, `order_id`, `date_added_epoch_s`, `order_created_at`) VALUES (%s, %s, %s, %s)
        '''

    def _find_orders_greater_than_date(self):
        return '''
        SELECT * from online_orders where order_created_at > %s;
        '''
    
    def _multi_find_joined_line_items_greater_than_date(self):
        return '''
        SELECT o.order_id, o.id, o.platform, o.order_created_at,
         l.title, l.variant_title from online_orders o join line_items l on o.order_id=l.online_orders_order_id
        where o.order_created_at > %s;
        '''
    
    def insert(self, platform, order_id, order_created_at):
        self.insert_into_table((platform, order_id, datetime.datetime.now().timestamp(), order_created_at))

    def find_orders_greater_than_date(self, date):
        orders = self.db.execute_sql(self._find_orders_greater_than_date(), date, fetch=True)
        return orders
    
    def multi_find_joined_line_items_greater_than_date(self, date):
        orders = self.db.execute_sql(self._multi_find_joined_line_items_greater_than_date(), date, fetch=True)
        return orders


class LineItems(Table):
    def _create_statement(self):
        # {} -> "line_items"[] -> "title": "Granja Paraiso 92 Decaf - Colombia",
        # {} -> "line_items"[] -> "variant_title": "284g / 10oz",
        return '''
        CREATE TABLE IF NOT EXISTS `line_items` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `online_orders_order_id` bigint(24) NOT NULL ,
        `title` varchar(255) COLLATE utf8_bin NOT NULL,
        `variant_title` varchar(255) COLLATE utf8_bin NOT NULL,
        PRIMARY KEY (`id`)
        );
        '''

    def _insert_statement(self):
        return '''
        INSERT INTO `line_items` (`online_orders_order_id`, `title`, `variant_title`) VALUES (%s, %s, %s)
        '''

    def _find_by_order_id(self):
        return '''
        SELECT * from line_items where online_orders_order_id = %s;
        '''

    def insert(self, online_orders_order_id, title, variant_title):
        self.insert_into_table((online_orders_order_id, title, variant_title))

    def find_id_by_order_id(self, id):
        line_items = self.db.execute_sql(self._find_by_order_id(), id, fetch=True)
        return line_items
    
    