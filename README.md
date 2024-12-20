# Modules to manage data for Coffee Roasting businesses

# Cupping Management Module 
`Create multiple interfaces for submitting and managing cupping data for green sourcing, qc, profile development starting with one that requires minimal input for power users`

ex. minimalistic log file

[12/18/24]
brew_style=cupping

1. 8.25 ripe berries peachy, 8.25 soft peach, 8 unstructured peach, 8.25 bright orange super floral [sagvag #158]
2. 7.75 sweet nougat caramel, 7.5 pear spiced sweet, 7.75 deep chocolate caramel apple pie, sweetest [Roastronics Andrew mystery medium]
___

## Functional Steps
### option 1 - email

Log file will be submitted to dedicated address with body of text in body of email.
A script will pick up the file and perform logical steps below:
1. Add cupping into database
2. Log each coffee used according to appropriate system (ex. Roest vs Loring). Add a new coffee if not seen before
3. Pick out scores and notes for each SCA cupping section and create aggregate score (if missing scores, will assume other fields are avg of existing scores)

____
## DB Schema:

users:
- name
- date_added
- id

cuppings:
- title
- date
- id
- notes
- alt_id

cuppings_sample:
- id
- order_id
- user_id
- cupping_id
- roast_id
- brew_style (default=cupping)
- score_fragrance
- notes_frangrance
- score_aroma
- notes_aroma
- score_flavor
- notes_flavor
- score_aftertaste
- notes_aftertaste
- score_acidity
- notes_acidity
- score_body
- notes_body
- score_balance
- notes_balance
- score_overall
- notes_overall

roasts:
- id
- date_roasted
- notes
- roasting_platform_id
- weight_in
- weight_out

roasting_platforms:
- id
- name
- link_to_roast_details

____
## Development:
1. `docker-compose up` -> starts the sample MysqlDB
2. create python 3 environment by your preference
3. `pip install -r requirements.txt`
4. `python main.py <command>` -> execute commands to load and run program
5. possible commands can be found by just running `python main.py`
