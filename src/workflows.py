import datetime
import pprint
from dateutil.parser import parse
from src.cupping_log_decoder import (
    find_header_values,
    split_log_into_roasts_and_scores
)

def decode_cupping_text_and_insert(body, email, db, brew_style=None, alt_id=None, date=None):
    headers, entries = split_log_into_roasts_and_scores(body)
    user_id = db.users.find_id_by_email(email)

    if date:
        date = parse(date)
    else:
        date = datetime.datetime.now()
    title = '{}-{}'.format(date.strftime("%m/%d/%y %H:%M:%S"), 'cupping')
    if alt_id:
        try:
            existing_cupping_id = db.cuppings.find_id_by_alt_id(alt_id)
            if existing_cupping_id:
                print('existing cupping found for msg-id {}'.format(alt_id))
                return
        except IndexError:
            pass
    cupping_id = db.cuppings.insert(title, alt_id=alt_id)
    
    for log_entry in entries:
        try:
            roast_id = db.roasts.find_id_by_name(log_entry['roast_name'])
        except IndexError:
            roast_id = create_bean_and_roast(log_entry['roast_name'], db)
        insert_scored_sample(
            log_entry,
            cupping_id,
            user_id,
            roast_id,
            brew_style or headers['brew_style'],
            db
        )

def create_bean_and_roast(name, db):
    bean_id = db.beans.insert(name)
    roast_id = db.roasts.insert(bean_id, name)
    return roast_id

def insert_scored_sample(sample, cupping_id, user_id, roast_id, brew_style, db):
    scores = sample['scores']
    print('inserting scored sample for userid:{}, cupping_id:{}, roast_id:{}'.format(
        user_id, cupping_id, roast_id
    ))
    db.cuppings_samples.insert(
        sample['order_id'],
        cupping_id,
        user_id,
        roast_id,
        scores[0]['score'],
        scores[0]['notes'],
        scores[1]['score'],
        scores[1]['notes'],
        scores[2]['score'],
        scores[2]['notes'],
        scores[3]['score'],
        scores[3]['notes'],
        scores[4]['score'],
        scores[4]['notes'],
        scores[5]['score'],
        scores[5]['notes'],
        scores[6]['score'],
        scores[6]['notes'],
        scores[7]['score'],
        scores[7]['notes'],
        brew_style=brew_style
    )
