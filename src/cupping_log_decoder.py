import re
"""example text"""
import pprint
import datetime

example = '''
1. 8.25 ripe berries peachy, 8.25 soft peach, 8 unstructured peach, 8.25 bright orange super floral [sagvag #158]
2. 7.75 sweet nougat caramel, 7.5 pear spiced sweet, 7.75 deep chocolate caramel apple pie, 8 sweetest [Roastronics Andrew mystery medium]
'''

def decode_attributes_from_line(line):
    attributes = {
        'roast_name': '',
        'order_id': None,
        'scores': [
            {'score': None,
             'notes': None,
             'name': 'fragrance'},
            {'score': None,
             'notes': None,
             'name': 'aroma'},
            {'score': None,
             'notes': None,
             'name': 'flavor'},
             {'score': None,
             'notes': None,
             'name': 'aftertaste'},
            {'score': None,
             'notes': None,
             'name': 'acidity'},
            {'score': None,
             'notes': None,
             'name': 'body'},
            {'score': None,
             'notes': None,
             'name': 'balance'},
            {'score': None,
             'notes': None,
             'name': 'overall'},
        ]
    }
    if not line:
        return None
    if not re.search(r'[a-zA-Z0-9]', line):
        return None
    order_id_match = re.match(r'^[^.]*', line)

    attributes['order_id'] = int(order_id_match.group())
    order_id_match_end = order_id_match.span()[1] + 1
    line_less_order = line[order_id_match_end:]

    roast_name_match = re.search(r'\[(.*?)\](?!.*\[)', line_less_order)
    attributes['roast_name'] = roast_name_match.group().lstrip('[').rstrip(']')
    roast_name_match_start = roast_name_match.span()[0]
    line_less_roast = line_less_order[:roast_name_match_start]

    scores = line_less_roast.lstrip().split(',')

    score_position = 0
    scores_tab = []
    for score in scores:
        match = re.search(r'\d+(\.\d+)?', score)
        score_number = float(match.group())
        scores_tab.append(score_number)
        score_note = score[match.span()[1]:].lstrip()

        attributes['scores'][score_position]['score'] = score_number
        attributes['scores'][score_position]['notes'] = score_note
        score_position += 1
    # import ipdb;ipdb.set_trace()
    # if len(scores_tab) != len(attributes['scores']):
    #     avg = sum(scores_tab) / len(scores_tab)
    #     for attr in attributes['scores']:
    #         attr['score'] = attr['score'] or avg


    return(attributes)

def find_header_values(body):
    headers = {
        'brew_style': 'cupping'
    }
    new_body = body
    brew_style_key = r'brew_style=([^ ]+)'
    match = re.search(brew_style_key, body)
    if match:
        headers['brew_style'] = match.group(1)
        new_body = re.sub(brew_style_key, '', body).strip()
    return headers, new_body


def split_log_into_roasts_and_scores(body):
    body = body.replace('\r\n', ' ')
    body = body.replace('\n', ' ')
    headers, body = find_header_values(body)
    temp_lines = body.split(']')
    lines = ['{}]'.format(line)  for line in temp_lines]

    cupping_date = datetime.datetime.now().timestamp()

    entries = []
    for line in lines:
        attributes = decode_attributes_from_line(line)
        if attributes:
            entries.append(attributes)
    return headers, entries
