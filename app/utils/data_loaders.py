import pandas as pd
import streamlit as st
import requests
import json
import time
import os


API_KEY = st.secrets["API_KEY"]

token_transfers_sql = """
with celsius_addr as (
  select distinct address from crosschain.address_labels
  where address_name = 'celsius wallet'
)

SELECT 
    count(TX_HASH) as transfer_count,
    AVG(TOKEN_PRICE) as avg_token_price,
    SUM(AMOUNT) as transfer_volume,
    SUM(AMOUNT_USD) as transfer_volume_usd,
    CONTRACT_ADDRESS,
    SYMBOL,
  	tt.FROM_ADDRESS,
  	tt.TO_ADDRESS,
    FROM_LABEL_TYPE,
    FROM_LABEL_SUBTYPE,
    FROM_ADDRESS_NAME,
    FROM_PROJECT_NAME,
    TO_LABEL_TYPE,
    TO_LABEL_SUBTYPE,
    TO_ADDRESS_NAME,
    TO_PROJECT_NAME
FROM ethereum.core.ez_token_transfers as tt
LEFT JOIN (
  	SELECT
      ADDRESS AS FROM_ADDRESS,
      LABEL_TYPE AS FROM_LABEL_TYPE,
      LABEL_SUBTYPE AS FROM_LABEL_SUBTYPE,
      ADDRESS_NAME AS FROM_ADDRESS_NAME,
      PROJECT_NAME AS FROM_PROJECT_NAME
 	FROM crosschain.address_labels 
  ) as fal ON tt.from_address=fal.FROM_ADDRESS
LEFT JOIN (
  	SELECT
      ADDRESS AS TO_ADDRESS,
      LABEL_TYPE AS TO_LABEL_TYPE,
      LABEL_SUBTYPE AS TO_LABEL_SUBTYPE,
      ADDRESS_NAME AS TO_ADDRESS_NAME,
      PROJECT_NAME AS TO_PROJECT_NAME
 	FROM crosschain.address_labels 
  ) as tal ON tt.to_address=tal.TO_ADDRESS
WHERE 1=1
	AND ((tt.from_address IN (select address from celsius_addr)) OR (tt.to_address IN (select address from celsius_addr)))
  	AND AMOUNT_USD IS NOT null
GROUP BY 
  CONTRACT_ADDRESS,SYMBOL,ORIGIN_FROM_ADDRESS,ORIGIN_TO_ADDRESS,tt.FROM_ADDRESS,tt.TO_ADDRESS,FROM_LABEL_TYPE,FROM_LABEL_SUBTYPE,FROM_ADDRESS_NAME,FROM_PROJECT_NAME,TO_LABEL_TYPE,TO_LABEL_SUBTYPE,TO_ADDRESS_NAME,TO_PROJECT_NAME
ORDER BY transfer_volume_usd DESC LIMIT 10000
"""
# st.code(token_transfers_sql)

approvals_sql = """with celsius_addr as (
  select distinct address from crosschain.address_labels
  where address_name = 'celsius wallet'
)

SELECT 
    COUNT(TX_HASH) as num_txs,
    DATE_TRUNC('day', block_timestamp) as "day",
    "ORIGIN_FROM_ADDRESS",
    "ORIGIN_TO_ADDRESS",
    CONTRACT_ADDRESS,
    CONTRACT_NAME,
    FROM_LABEL_TYPE,
    FROM_LABEL_SUBTYPE,
    FROM_ADDRESS_NAME,
    FROM_PROJECT_NAME,
    TO_LABEL_TYPE,
    TO_LABEL_SUBTYPE,
    TO_ADDRESS_NAME,
    TO_PROJECT_NAME
FROM  ethereum.core.fact_event_logs
LEFT JOIN (
  	SELECT
      ADDRESS AS FROM_ADDRESS,
      LABEL_TYPE AS FROM_LABEL_TYPE,
      LABEL_SUBTYPE AS FROM_LABEL_SUBTYPE,
      ADDRESS_NAME AS FROM_ADDRESS_NAME,
      PROJECT_NAME AS FROM_PROJECT_NAME
 	FROM crosschain.address_labels 
  ) as fal ON ORIGIN_FROM_ADDRESS=fal.FROM_ADDRESS
LEFT JOIN (
  	SELECT
      ADDRESS AS TO_ADDRESS,
      LABEL_TYPE AS TO_LABEL_TYPE,
      LABEL_SUBTYPE AS TO_LABEL_SUBTYPE,
      ADDRESS_NAME AS TO_ADDRESS_NAME,
      PROJECT_NAME AS TO_PROJECT_NAME
 	FROM crosschain.address_labels 
  ) as tal ON ORIGIN_FROM_ADDRESS=tal.TO_ADDRESS
WHERE 1=1
  	AND TX_STATUS='SUCCESS'
  	AND EVENT_REMOVED=false
	AND (origin_from_address in (select address from celsius_addr) or origin_to_address in (select address from celsius_addr)) 
  	AND block_timestamp>'2022-05-01'
  	AND event_name='Approval'
GROUP BY DATE_TRUNC('day', block_timestamp),ORIGIN_FROM_ADDRESS,ORIGIN_TO_ADDRESS,CONTRACT_ADDRESS,CONTRACT_NAME,FROM_LABEL_TYPE,FROM_LABEL_SUBTYPE,FROM_ADDRESS_NAME,FROM_PROJECT_NAME,TO_LABEL_TYPE,TO_LABEL_SUBTYPE,TO_ADDRESS_NAME,TO_PROJECT_NAME"""
# st.code(approvals_sql)

transfers_sql = """with celsius_addr as (
  select distinct address from crosschain.address_labels
  where address_name = 'celsius wallet'
)

, TMP AS (
SELECT 
    COUNT(TX_HASH) AS transfer_count,
    SUM(AMOUNT) as transfer_volume,
    SUM(AMOUNT_USD) as transfer_volume_usd,
    ORIGIN_FROM_ADDRESS,
    ORIGIN_TO_ADDRESS,
    ETH_FROM_ADDRESS,
    ETH_TO_ADDRESS,
    FROM_LABEL_TYPE,
    FROM_LABEL_SUBTYPE,
    FROM_ADDRESS_NAME,
    FROM_PROJECT_NAME,
    TO_LABEL_TYPE,
    TO_LABEL_SUBTYPE,
    TO_ADDRESS_NAME,
    TO_PROJECT_NAME
FROM ethereum.core.ez_eth_transfers as tt
LEFT JOIN (
  	SELECT
      ADDRESS AS FROM_ADDRESS,
      LABEL_TYPE AS FROM_LABEL_TYPE,
      LABEL_SUBTYPE AS FROM_LABEL_SUBTYPE,
      ADDRESS_NAME AS FROM_ADDRESS_NAME,
      PROJECT_NAME AS FROM_PROJECT_NAME
 	FROM crosschain.address_labels 
  ) as fal ON tt.ETH_FROM_ADDRESS=fal.FROM_ADDRESS
LEFT JOIN (
  	SELECT
      ADDRESS AS TO_ADDRESS,
      LABEL_TYPE AS TO_LABEL_TYPE,
      LABEL_SUBTYPE AS TO_LABEL_SUBTYPE,
      ADDRESS_NAME AS TO_ADDRESS_NAME,
      PROJECT_NAME AS TO_PROJECT_NAME
 	FROM crosschain.address_labels 
  ) as tal ON tt.ETH_TO_ADDRESS=tal.TO_ADDRESS
WHERE 1=1
	AND ((tt.ETH_FROM_ADDRESS IN (select address from celsius_addr)) OR (tt.ETH_TO_ADDRESS IN (select address from celsius_addr)))
  	AND AMOUNT_USD is not null
GROUP BY 
  ORIGIN_FROM_ADDRESS,ORIGIN_TO_ADDRESS,ETH_FROM_ADDRESS,ETH_TO_ADDRESS,FROM_LABEL_TYPE,FROM_LABEL_SUBTYPE,FROM_ADDRESS_NAME,FROM_PROJECT_NAME,TO_LABEL_TYPE,TO_LABEL_SUBTYPE,TO_ADDRESS_NAME,TO_PROJECT_NAME
)
SELECT * FROM TMP ORDER BY transfer_volume_usd DESC LIMIT 10000
"""
# st.code(transfers_sql)


balances_sql = """
with celsius_addr as (
  select distinct address from crosschain.address_labels
  where address_name = 'celsius wallet'
)

SELECT 
    AVG(PRICE) as avg_price,
    SUM(BALANCE) as total_balance,
    SUM(AMOUNT_USD) as total_balance_usd,
    DATE_TRUNC('day', BALANCE_DATE) as "day",
    SYMBOL,
    USER_ADDRESS,
    CONTRACT_ADDRESS,
    fal.LABEL_TYPE,
    fal.LABEL_SUBTYPE,
    fal.ADDRESS_NAME,
    fal.PROJECT_NAME
FROM  flipside_prod_db.ethereum.erc20_balances
LEFT JOIN (
  	SELECT
      ADDRESS AS ADDRESS,
      LABEL_TYPE AS LABEL_TYPE,
      LABEL_SUBTYPE AS LABEL_SUBTYPE,
      ADDRESS_NAME AS ADDRESS_NAME,
      PROJECT_NAME AS PROJECT_NAME
 	FROM crosschain.address_labels 
  ) as fal ON USER_ADDRESS=fal.ADDRESS
WHERE 1=1
	AND (address in (select address from celsius_addr))
  	AND BALANCE_DATE>current_timestamp()-interval'70 days'
  	AND AMOUNT_USD is not null
GROUP BY DATE_TRUNC('day', BALANCE_DATE),SYMBOL,USER_ADDRESS,CONTRACT_ADDRESS,fal.LABEL_TYPE,fal.LABEL_SUBTYPE,fal.ADDRESS_NAME,fal.PROJECT_NAME
HAVING total_balance_usd>25 and total_balance_usd<2500000000000
ORDER BY total_balance_usd DESC LIMIT 10000
"""
# st.code(balances_sql)

txs_sql = """with celsius_addr as (
  select distinct address from crosschain.address_labels
  where address_name = 'celsius wallet'
)

SELECT 
  	ft.FROM_ADDRESS,
  	ft.TO_ADDRESS,
    FROM_LABEL_TYPE,
    FROM_LABEL_SUBTYPE,
    FROM_ADDRESS_NAME,
    FROM_PROJECT_NAME,
    TO_LABEL_TYPE,
    TO_LABEL_SUBTYPE,
    TO_ADDRESS_NAME,
    TO_PROJECT_NAME,
  	count(*) as num_txs
FROM ethereum.core.fact_transactions as ft
LEFT JOIN (
  	SELECT
      ADDRESS AS FROM_ADDRESS,
      LABEL_TYPE AS FROM_LABEL_TYPE,
      LABEL_SUBTYPE AS FROM_LABEL_SUBTYPE,
      ADDRESS_NAME AS FROM_ADDRESS_NAME,
      PROJECT_NAME AS FROM_PROJECT_NAME
 	FROM crosschain.address_labels 
  ) as fal ON ft.from_address=fal.FROM_ADDRESS
LEFT JOIN (
  	SELECT
      ADDRESS AS TO_ADDRESS,
      LABEL_TYPE AS TO_LABEL_TYPE,
      LABEL_SUBTYPE AS TO_LABEL_SUBTYPE,
      ADDRESS_NAME AS TO_ADDRESS_NAME,
      PROJECT_NAME AS TO_PROJECT_NAME
 	FROM crosschain.address_labels 
  ) as tal ON ft.to_address=tal.TO_ADDRESS
WHERE 1=1
  	AND STATUS='SUCCESS'
	AND ((ft.from_address IN (select address from celsius_addr)) OR (ft.to_address IN (select address from celsius_addr)))
GROUP BY 
  ft.FROM_ADDRESS,ft.TO_ADDRESS,FROM_LABEL_TYPE,FROM_LABEL_SUBTYPE,FROM_ADDRESS_NAME,FROM_PROJECT_NAME,TO_LABEL_TYPE,TO_LABEL_SUBTYPE,TO_ADDRESS_NAME,TO_PROJECT_NAME
HAVING num_txs>5"""

# st.code(txs_sql)

daily_txs_sql = """with celsius_addr as (
  select distinct address from crosschain.address_labels
  where address_name = 'celsius wallet'
)

SELECT 
  	DATE_TRUNC('day', block_timestamp) as "day",
  	ft.from_address as address,
  	'from' as side,
  	count(*) as num_txs
FROM ethereum.core.fact_transactions as ft
WHERE 1=1
  	AND STATUS='SUCCESS'
	AND (ft.from_address IN (select address from celsius_addr))
  	AND block_timestamp>'2021-06-01'
GROUP BY 1, 2
UNION ALL
SELECT 
  	DATE_TRUNC('day', block_timestamp) as "day",
  	ft.to_address as address,
  	'to' as side,
  	count(*) as num_txs
FROM ethereum.core.fact_transactions as ft
WHERE 1=1
  	AND STATUS='SUCCESS'
	AND (ft.to_address IN (select address from celsius_addr))
  	AND block_timestamp>'2021-06-01'
GROUP BY 1, 2"""
# st.code(daily_txs_sql)

token_transfers2_sql = """with celsius_addr as (
  select distinct address from crosschain.address_labels
  where address_name = 'celsius wallet'
)

SELECT 
    count(TX_HASH) as transfer_count,
    AVG(TOKEN_PRICE) as avg_token_price,
    SUM(AMOUNT) as transfer_volume,
    SUM(AMOUNT_USD) as transfer_volume_usd,
  	DATE_TRUNC('day', BLOCK_TIMESTAMP) as "day",
    CONTRACT_ADDRESS,
    SYMBOL,
  	'to' as side
FROM ethereum.core.ez_token_transfers as tt
WHERE 1=1
	AND (tt.to_address IN (select address from celsius_addr))
  	AND block_timestamp>current_timestamp()-interval'180 days'
  	AND AMOUNT_USD IS NOT null
GROUP BY 
  DATE_TRUNC('day', BLOCK_TIMESTAMP),
  CONTRACT_ADDRESS,SYMBOL
UNION ALL
SELECT 
    count(TX_HASH) as transfer_count,
    AVG(TOKEN_PRICE) as avg_token_price,
    SUM(AMOUNT) as transfer_volume,
    SUM(AMOUNT_USD) as transfer_volume_usd,
  	DATE_TRUNC('day', BLOCK_TIMESTAMP) as "day",
    CONTRACT_ADDRESS,
    SYMBOL,
  	'from' as side
FROM ethereum.core.ez_token_transfers as tt
WHERE 1=1
	AND (tt.from_address IN (select address from celsius_addr))
  	AND block_timestamp>current_timestamp()-interval'180 days'
  	AND AMOUNT_USD IS NOT null
GROUP BY 
  DATE_TRUNC('day', BLOCK_TIMESTAMP),
  CONTRACT_ADDRESS,SYMBOL
ORDER BY transfer_volume_usd DESC LIMIT 10000"""
# st.code(token_transfers2_sql)

transferes2_sql = """with celsius_addr as (
  select distinct address from crosschain.address_labels
  where address_name = 'celsius wallet'
)

, TMP AS (
SELECT 
    COUNT(TX_HASH) AS transfer_count,
    SUM(AMOUNT) as transfer_volume,
    SUM(AMOUNT_USD) as transfer_volume_usd,
    DATE_TRUNC('day', BLOCK_TIMESTAMP) AS "day",
  	'to' as side
FROM ethereum.core.ez_eth_transfers as tt
WHERE 1=1
	AND (tt.ETH_TO_ADDRESS IN (select address from celsius_addr))
  	AND AMOUNT_USD is not null
  	AND block_timestamp>current_timestamp()-interval'180 days'
GROUP BY 
  DATE_TRUNC('day', BLOCK_TIMESTAMP)
UNION ALL
SELECT 
    COUNT(TX_HASH) AS transfer_count,
    SUM(AMOUNT) as transfer_volume,
    SUM(AMOUNT_USD) as transfer_volume_usd,
    DATE_TRUNC('day', BLOCK_TIMESTAMP) AS "day",
  	'from' as side
FROM ethereum.core.ez_eth_transfers as tt
WHERE 1=1
	AND (tt.ETH_FROM_ADDRESS IN (select address from celsius_addr))
  	AND AMOUNT_USD is not null
  	AND block_timestamp>current_timestamp()-interval'180 days'
GROUP BY 
  DATE_TRUNC('day', BLOCK_TIMESTAMP)
)
SELECT * FROM TMP ORDER BY transfer_volume_usd DESC LIMIT 1\0000"""
# st.code(transferes2_sql)

celsius_accounts_sql = """with celsius_addr as (
  select distinct address from crosschain.address_labels
  where address_name = 'celsius wallet'
)

SELECT * FROM celsius_addr"""


def load_flip_df(SQL_QUERY, API_KEY):
	TTL_MINUTES = 15
	def create_query():
		r = requests.post(
			'https://node-api.flipsidecrypto.com/queries', 
			data=json.dumps({
				"sql": SQL_QUERY,
				"ttlMinutes": TTL_MINUTES
			}),
			headers={"Accept": "application/json", "Content-Type": "application/json", "x-api-key": API_KEY},
		)
		if r.status_code != 200:
			raise Exception("Error creating query, got response: " + r.text + "with status code: " + str(r.status_code))
		
		return json.loads(r.text)    


	def get_query_results(token):
		r = requests.get(
			'https://node-api.flipsidecrypto.com/queries/' + token, 
			headers={"Accept": "application/json", "Content-Type": "application/json", "x-api-key": API_KEY}
		)
		if r.status_code != 200:
			raise Exception("Error getting query results, got response: " + r.text + "with status code: " + str(r.status_code))
		
		data = json.loads(r.text)
		if data['status'] == 'running':
			time.sleep(10)
			return get_query_results(token)

		return data
	query = create_query()
	token = query.get('token')
	data = get_query_results(token)
	df = pd.DataFrame(data['results'], columns=data['columnLabels'])
	return df
# load_flip_df(SQL_QUERY=approvals_sql, API_KEY=API_KEY)
# load_flip_df(SQL_QUERY=transfers_sql, API_KEY=API_KEY)
# load_flip_df(SQL_QUERY=balances_sql, API_KEY=API_KEY)
# load_flip_df(SQL_QUERY=txs_sql, API_KEY=API_KEY)
# load_flip_df(SQL_QUERY=daily_txs_sql, API_KEY=API_KEY)
# load_flip_df(SQL_QUERY=transferes2_sql, API_KEY=API_KEY)

# load_flip_df(SQL_QUERY=celsius_accounts_sql, API_KEY=API_KEY)

# token_transfers_sql
# approvals_sql
# transfers_sql
# balances_sql
# txs_sql
# daily_txs_sql
# token_transfers2_sql
# transferes2_sql


# @st.cache
def load_token_transfers():
	#token_transfers = pd.read_json('https://node-api.flipsidecrypto.com/api/v2/queries/ed9ec9a3-5465-48a5-b9a2-fd43f17b9b46/data/latest')
	token_transfers = load_flip_df(SQL_QUERY=token_transfers_sql, API_KEY=API_KEY)
	return token_transfers

# @st.cache
def load_transfers():
	#transfers = pd.read_json("https://node-api.flipsidecrypto.com/api/v2/queries/06fbdc78-926e-473a-9a24-ab6076003601/data/latest")
	transfers = load_flip_df(SQL_QUERY=transfers_sql, API_KEY=API_KEY)

	return transfers

# @st.cache
def load_approvals():
	#approvals = pd.read_json("https://node-api.flipsidecrypto.com/api/v2/queries/afc06e0c-768b-4228-bee1-7ae5a56e173e/data/latest")
	approvals = load_flip_df(SQL_QUERY=approvals_sql, API_KEY=API_KEY)
	return approvals

# @st.cache
def load_txs():
	#txs = pd.read_json("https://node-api.flipsidecrypto.com/api/v2/queries/8b31c403-abdc-4fcf-8aba-46c7b7812a1f/data/latest")
	txs = load_flip_df(SQL_QUERY=txs_sql, API_KEY=API_KEY)

	return txs

# @st.cache
def load_daily_txs():
	#daily_txs = pd.read_json("https://node-api.flipsidecrypto.com/api/v2/queries/9312140e-c66d-4f74-995f-a66c4197a493/data/latest")
	daily_txs = load_flip_df(SQL_QUERY=daily_txs_sql, API_KEY=API_KEY)
	daily_txs['day'] = pd.to_datetime(daily_txs['day'])
	daily_txs = daily_txs.sort_values(by='day')
	return daily_txs

# @st.cache
def load_balances():
	#balances = pd.read_json("https://node-api.flipsidecrypto.com/api/v2/queries/f8f8f8f8-f8f8-f8f8-f8f8-f8f8f8f8f8f8/data/latest")
	balances =  load_flip_df(SQL_QUERY=balances_sql, API_KEY=API_KEY)
	balances['day'] = pd.to_datetime(balances['day'])
	balances = balances.sort_values(by='day')
	return balances

# @st.cache
def load_celsius_accounts():
	#celsius_accounts = pd.read_json("https://node-api.flipsidecrypto.com/api/v2/queries/8daf6411-fd29-4737-961c-71b08b7ffe30/data/latest")
	celsius_accounts = load_flip_df(SQL_QUERY=celsius_accounts_sql, API_KEY=API_KEY)

	return celsius_accounts

# @st.cache
def load_token_transfers_daily():
	#token_transfers_daily = pd.read_json("https://node-api.flipsidecrypto.com/api/v2/queries/a0f06d3b-01c8-4745-baa2-5f122d5e1c11/data/latest")
	token_transfers_daily = load_flip_df(SQL_QUERY=token_transfers2_sql, API_KEY=API_KEY)
	token_transfers_daily['day'] = pd.to_datetime(token_transfers_daily['day'])
	token_transfers_daily = token_transfers_daily.sort_values(by='day')
	token_transfers_daily = token_transfers_daily.dropna()
	return token_transfers_daily

# @st.cache
def load_transfers_daily():
	#transfers_daily = pd.read_json("https://node-api.flipsidecrypto.com/api/v2/queries/8476a152-0727-4866-9e21-67286bd1c1ad/data/latest")
	transfers_daily = load_flip_df(SQL_QUERY=transferes2_sql, API_KEY=API_KEY)
	transfers_daily['day'] = pd.to_datetime(transfers_daily['day'])
	transfers_daily = transfers_daily.sort_values(by='day')
	transfers_daily = transfers_daily.dropna()
	return transfers_daily
