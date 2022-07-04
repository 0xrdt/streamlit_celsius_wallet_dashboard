import streamlit as st
import pandas as pd
import pandas as pd
import plotly.express as px

from utils.data_loaders import *
from utils.df_grid_builder import df_grid_builder

st.set_page_config(
     page_title="Celsius Wallet Analyzoor",
     page_icon="🌡️",
     layout="wide",
     initial_sidebar_state="expanded",
     menu_items={
         'About': 'https://0xrdt.notion.site/Celsius-Wallet-725174fa3c8348059dc2fa6b105ddf82'}
 )


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
  	-- DATE_TRUNC('day', BLOCK_TIMESTAMP) as "day",
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
  	-- AND block_timestamp>'2022-05-01'
  	AND AMOUNT_USD IS NOT null
GROUP BY 
  -- DATE_TRUNC('day', BLOCK_TIMESTAMP),
  CONTRACT_ADDRESS,SYMBOL,ORIGIN_FROM_ADDRESS,ORIGIN_TO_ADDRESS,tt.FROM_ADDRESS,tt.TO_ADDRESS,FROM_LABEL_TYPE,FROM_LABEL_SUBTYPE,FROM_ADDRESS_NAME,FROM_PROJECT_NAME,TO_LABEL_TYPE,TO_LABEL_SUBTYPE,TO_ADDRESS_NAME,TO_PROJECT_NAME
ORDER BY transfer_volume_usd DESC LIMIT 100000
"""
st.code(token_transfers_sql)

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
st.code(approvals_sql)

transfers_sql = """with celsius_addr as (
  select distinct address from crosschain.address_labels
  where address_name = 'celsius wallet'
)

, TMP AS (
SELECT 
    COUNT(TX_HASH) AS transfer_count,
    SUM(AMOUNT) as transfer_volume,
    SUM(AMOUNT_USD) as transfer_volume_usd,
    -- DATE_TRUNC('day', BLOCK_TIMESTAMP) AS "day",
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
  	-- AND block_timestamp>'2021-06-01'
GROUP BY 
  -- DATE_TRUNC('day', BLOCK_TIMESTAMP),
  ORIGIN_FROM_ADDRESS,ORIGIN_TO_ADDRESS,ETH_FROM_ADDRESS,ETH_TO_ADDRESS,FROM_LABEL_TYPE,FROM_LABEL_SUBTYPE,FROM_ADDRESS_NAME,FROM_PROJECT_NAME,TO_LABEL_TYPE,TO_LABEL_SUBTYPE,TO_ADDRESS_NAME,TO_PROJECT_NAME
-- HAVING transfer_volume_usd>500
)
SELECT * FROM TMP ORDER BY transfer_volume_usd DESC LIMIT 100000
"""
st.code(transfers_sql)


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
HAVING total_balance_usd>25
ORDER BY total_balance_usd DESC LIMIT 100000
"""
st.code(balances_sql)

txs_sql = """with celsius_addr as (
  select distinct address from crosschain.address_labels
  where address_name = 'celsius wallet'
)

SELECT 
  	-- DATE_TRUNC('day', block_timestamp) as "day",
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
  	-- AND block_timestamp>'2021-06-01'
GROUP BY 
  -- DATE_TRUNC('day', block_timestamp),
  ft.FROM_ADDRESS,ft.TO_ADDRESS,FROM_LABEL_TYPE,FROM_LABEL_SUBTYPE,FROM_ADDRESS_NAME,FROM_PROJECT_NAME,TO_LABEL_TYPE,TO_LABEL_SUBTYPE,TO_ADDRESS_NAME,TO_PROJECT_NAME
HAVING num_txs>5"""

st.code(txs_sql)

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
st.code(daily_txs_sql)

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
ORDER BY transfer_volume_usd DESC LIMIT 100000"""
st.code(token_transfers2_sql)

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
-- HAVING transfer_volume_usd>500
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
-- HAVING transfer_volume_usd>500
)
SELECT * FROM TMP ORDER BY transfer_volume_usd DESC LIMIT 100000"""
st.code(transferes2_sql)

st.title('Celsius Wallets Analysis')
st.markdown("Check out the [article about this dashboard](https://0xrdt.notion.site/Celsius-Wallet-725174fa3c8348059dc2fa6b105ddf82)! ")

def daily_txs_section():
	st.header('Daily Transactions')
	daily_txs = load_daily_txs()
	daily_txs_without_side = daily_txs.groupby(["day", 'ADDRESS'])['NUM_TXS'].sum().reset_index()

	fig = px.bar(daily_txs_without_side, x='day', y='NUM_TXS', color='ADDRESS', title='Daily Transactions (to and from) for all celsius wallets')
	fig.update_layout(xaxis_title="Day", yaxis_title="Number of Transactions")
	fig.update_layout(showlegend=False)
	fig.update_layout(height=500)
	st.write(fig)

	fig = px.bar(daily_txs, x='day', y='NUM_TXS', color='ADDRESS', facet_row='SIDE', title='Daily Transactions for all celsius wallets')
	fig.update_yaxes(matches=None)
	fig.update_layout(xaxis_title="Day", yaxis_title="Number of Transactions")
	fig.update_layout(showlegend=False)
	fig.update_layout(height=900)
	st.write(fig)

	cum_daily_txs = daily_txs.groupby(['SIDE', 'day']).sum().groupby(level=0).cumsum()['NUM_TXS'].reset_index()
	fig = px.bar(cum_daily_txs, x='day', y='NUM_TXS', facet_row='SIDE', title='Cumulative Daily Transactions from for all celsius wallets')
	fig.update_yaxes(matches=None)
	fig.update_layout(height=900)
	st.write(fig)


def balances_section():
	st.header('Balances')
	balances = load_balances()
	total_balance = balances[balances['day']==balances['day'].max()].groupby("SYMBOL")['TOTAL_BALANCE_USD'].sum()
	total_balance = total_balance.sort_values(ascending=False)

	# black magic
	top10 = total_balance.sort_values(ascending=False).head(10)
	top10 = pd.concat([top10, pd.Series({"others":total_balance[~total_balance.isin(top10)].sum()})]) 
	top10 = top10.reset_index()
	top10.columns = ['SYMBOL', 'TOTAL_BALANCE_USD']

	title='Top 10 Tokens by Total Balance <br><sup>Some tokens might not appear due to them being illiquid</sup>'

	fig = px.pie(top10.reset_index(), values='TOTAL_BALANCE_USD', names='SYMBOL', title=title)
	fig.update_layout(height=500)
	st.write(fig)

	daily_total_balances = balances.groupby(["SYMBOL", "day"])['TOTAL_BALANCE_USD'].sum().reset_index()
	daily_total_balances.loc[daily_total_balances['TOTAL_BALANCE_USD']<1_000_000, 'SYMBOL'] = 'others'
	daily_total_balances = daily_total_balances.groupby(["SYMBOL", "day"])['TOTAL_BALANCE_USD'].sum().reset_index()
	daily_total_balances = daily_total_balances.sort_values(by=['day', 'TOTAL_BALANCE_USD'], ascending=False).reset_index(drop=True)

	title='Daily Total Balances for all celsius wallets <br><sup>Some tokens might not appear due to them being illiquid</sup>'
	fig = px.bar(daily_total_balances, x='day', y='TOTAL_BALANCE_USD', color='SYMBOL', title=title)
	fig.update_layout(xaxis_title="Day", yaxis_title="Total Balance (USD)")
	fig.update_layout(height=600)
	st.write(fig)

	normalized_daily_total_balances = (daily_total_balances.groupby(['SYMBOL', 'day'])['TOTAL_BALANCE_USD'].sum()/daily_total_balances.groupby(['day'])['TOTAL_BALANCE_USD'].sum()).reset_index()
	normalized_daily_total_balances = normalized_daily_total_balances.sort_values(by=['day', 'TOTAL_BALANCE_USD'], ascending=False).reset_index(drop=True)

	title = 'Normalized Daily Total Balances for all celsius wallets <br><sup>Some tokens might not appear due to them being illiquid</sup>'

	fig = px.bar(normalized_daily_total_balances, x='day', y='TOTAL_BALANCE_USD', color='SYMBOL', title=title)
	fig.update_layout(xaxis_title="Day", yaxis_title="Total Balance (USD)")
	fig.update_layout(height=600)
	st.write(fig)


def token_transfers_section():
	st.header('Token Transfers')
	token_transfers_daily = load_token_transfers_daily()
	token_transfers_daily = token_transfers_daily.sort_values(by=['TRANSFER_VOLUME_USD', 'day'], ascending=False).reset_index(drop=True)
	
	fig = px.bar(token_transfers_daily, x='day', y='TRANSFER_VOLUME_USD', color='SYMBOL', facet_row='SIDE', title='Daily Token ERC-20 Transfers for all celsius wallets')
	fig.update_layout(barmode='stack', xaxis={'categoryorder':'total descending'})
	fig.update_layout(height=900)
	st.write(fig)

	token_transfers_daily_agg = token_transfers_daily.copy()
	token_transfers_daily_agg['SIDE'] = token_transfers_daily_agg['SIDE'].apply(lambda x: 1 if x=='from' else -1)
	token_transfers_daily_agg['TRANSFER_VOLUME_USD'] = token_transfers_daily_agg['SIDE']*token_transfers_daily_agg['TRANSFER_VOLUME_USD']
	token_transfers_daily_agg = token_transfers_daily_agg.groupby(['day', 'SYMBOL'])['TRANSFER_VOLUME_USD'].sum().reset_index()

	token_transfers_daily_agg = token_transfers_daily_agg.sort_values(by=['TRANSFER_VOLUME_USD', 'day', 'SYMBOL'], ascending=False).reset_index(drop=True)
	fig = px.bar(token_transfers_daily_agg, x='day', y='TRANSFER_VOLUME_USD', color='SYMBOL', title='Daily Net ERC-20 Transfers (from minus to) for all celsius wallets')
	fig.update_layout(barmode='stack', xaxis={'categoryorder':'total descending'})
	fig.update_layout(height=500)
	st.write(fig)

	cum_token_transfers = token_transfers_daily.groupby(['SIDE', 'SYMBOL'])['TRANSFER_VOLUME_USD'].sum().reset_index()

	# black magic
	tmp = cum_token_transfers[cum_token_transfers['SIDE']=='to']
	del tmp['SIDE']
	tmp = tmp.set_index('SYMBOL')['TRANSFER_VOLUME_USD']
	top10 = tmp.sort_values(ascending=False).head(10)
	top10 = pd.concat([top10, pd.Series({"others":tmp[~tmp.isin(top10)].sum()})])
	top10 = top10.reset_index()
	top10.columns = ['SYMBOL', 'TRANSFER_VOLUME_USD']

	title='Top 10 Net ERC-20 Transfers To Celsius Wallets'

	fig = px.pie(top10.reset_index(), values='TRANSFER_VOLUME_USD', names='SYMBOL', title=title)
	fig.update_layout(height=500)
	st.write(fig)

	# black magic
	tmp = cum_token_transfers[cum_token_transfers['SIDE']=='from']
	del tmp['SIDE']
	tmp = tmp.set_index('SYMBOL')['TRANSFER_VOLUME_USD']
	top10 = tmp.sort_values(ascending=False).head(10)
	top10 = pd.concat([top10, pd.Series({"others":tmp[~tmp.isin(top10)].sum()})])
	top10 = top10.reset_index()
	top10.columns = ['SYMBOL', 'TRANSFER_VOLUME_USD']

	title='Top 10 Net ERC-20 Transfers From Celsius Wallets'

	fig = px.pie(top10.reset_index(), values='TRANSFER_VOLUME_USD', names='SYMBOL', title=title)
	fig.update_layout(height=500)
	st.write(fig)

	should_show = st.checkbox('Show top 100 ETH transfers')
	if should_show:
		token_transfers = load_token_transfers()
		token_transfers = token_transfers.sort_values(['TRANSFER_VOLUME_USD'], ascending=False)
		df = token_transfers[['FROM_ADDRESS_NAME', 'FROM_PROJECT_NAME', 'TO_ADDRESS_NAME', 'TO_PROJECT_NAME', 'TRANSFER_COUNT', 'TRANSFER_VOLUME_USD', 'SYMBOL', 'FROM_ADDRESS', 'TO_ADDRESS']].head(100)
		df_grid_builder(df)


def eth_transfers_section():
	st.header('ETH Transfers')
	transfers_daily = load_transfers_daily()

	transfers_daily = transfers_daily.sort_values(by=['SIDE', 'day', 'TRANSFER_VOLUME_USD'], ascending=False).reset_index(drop=True)
	fig = px.bar(transfers_daily, x='day', y='TRANSFER_VOLUME_USD', facet_row='SIDE', title='Daily ETH Transfers for all celsius wallets')
	fig.update_layout(barmode='stack', xaxis={'categoryorder':'total descending'})
	fig.update_layout(height=900)
	st.write(fig)

	transfers_daily_agg = transfers_daily.copy()
	transfers_daily_agg['SIDE'] = transfers_daily_agg['SIDE'].apply(lambda x: 1 if x=='from' else -1)
	transfers_daily_agg['TRANSFER_VOLUME_USD'] = transfers_daily_agg['SIDE']*transfers_daily_agg['TRANSFER_VOLUME_USD']
	transfers_daily_agg = transfers_daily_agg.groupby(['day'])['TRANSFER_VOLUME_USD'].sum().reset_index()
	transfers_daily = transfers_daily.sort_values(by=['SIDE' , 'day', 'TRANSFER_VOLUME_USD'], ascending=False).reset_index(drop=True)
	fig = px.bar(transfers_daily_agg, x='day', y='TRANSFER_VOLUME_USD', title='Daily Net ETH Transfers (from minus to) for all celsius wallets')
	fig.update_layout(barmode='stack', xaxis={'categoryorder':'total descending'})
	fig.update_layout(height=500)
	st.write(fig)

	should_show = st.checkbox('Show top 100 token transfers')
	if should_show:
		transfers = load_transfers()
		transfers = transfers.sort_values(['TRANSFER_VOLUME_USD'], ascending=False)
		df = transfers[['FROM_ADDRESS_NAME', 'FROM_PROJECT_NAME', 'TO_ADDRESS_NAME', 'TO_PROJECT_NAME', 'TRANSFER_COUNT', 'TRANSFER_VOLUME_USD', 'ORIGIN_FROM_ADDRESS', 'ORIGIN_TO_ADDRESS']].head(100)
		df_grid_builder(df)


#st.sidebar.title('Choose what you want to see')
selected_sections = st.sidebar.multiselect('Choose the sections you want to see:', ['Transactions', 'Balances', 'ETH Transfers', 'ERC-20 Transfers'], default=['Balances'])

if 'Transactions' in selected_sections:
	daily_txs_section()

if 'Balances' in selected_sections:
	balances_section()

if 'ERC-20 Transfers' in selected_sections:
	token_transfers_section()

if 'ETH Transfers' in selected_sections:
	eth_transfers_section()
