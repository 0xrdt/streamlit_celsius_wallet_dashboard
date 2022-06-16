import pandas as pd
import streamlit as st

@st.cache
def load_token_transfers():
	#token_transfers = pd.read_json('https://node-api.flipsidecrypto.com/api/v2/queries/ed9ec9a3-5465-48a5-b9a2-fd43f17b9b46/data/latest')
	token_transfers = pd.read_json("data/token_transfers.json")
	return token_transfers

@st.cache
def load_transfers():
	#transfers = pd.read_json("https://node-api.flipsidecrypto.com/api/v2/queries/06fbdc78-926e-473a-9a24-ab6076003601/data/latest")
	transfers = pd.read_json("data/transfers.json")
	return transfers

@st.cache
def load_approvals():
	#approvals = pd.read_json("https://node-api.flipsidecrypto.com/api/v2/queries/afc06e0c-768b-4228-bee1-7ae5a56e173e/data/latest")
	approvals = pd.read_json("data/approvals.json")
	return approvals

@st.cache
def load_txs():
	#txs = pd.read_json("https://node-api.flipsidecrypto.com/api/v2/queries/8b31c403-abdc-4fcf-8aba-46c7b7812a1f/data/latest")
	txs = pd.read_json("data/txs.json")
	return txs

@st.cache
def load_daily_txs():
	#daily_txs = pd.read_json("https://node-api.flipsidecrypto.com/api/v2/queries/9312140e-c66d-4f74-995f-a66c4197a493/data/latest")
	daily_txs = pd.read_json("data/daily_txs.json")
	daily_txs['day'] = pd.to_datetime(daily_txs['day'])
	daily_txs = daily_txs.sort_values(by='day')
	return daily_txs

@st.cache
def load_balances():
	#balances = pd.read_json("https://node-api.flipsidecrypto.com/api/v2/queries/f8f8f8f8-f8f8-f8f8-f8f8-f8f8f8f8f8f8/data/latest")
	balances = pd.read_json("data/balances.json")
	balances['day'] = pd.to_datetime(balances['day'])
	balances = balances.sort_values(by='day')
	return balances

@st.cache
def load_celsius_accounts():
	celsius_accounts = pd.read_json("https://node-api.flipsidecrypto.com/api/v2/queries/8daf6411-fd29-4737-961c-71b08b7ffe30/data/latest")
	return celsius_accounts

@st.cache
def load_token_transfers_daily():
	token_transfers_daily = pd.read_json("https://node-api.flipsidecrypto.com/api/v2/queries/a0f06d3b-01c8-4745-baa2-5f122d5e1c11/data/latest")
	token_transfers_daily['day'] = pd.to_datetime(token_transfers_daily['day'])
	token_transfers_daily = token_transfers_daily.sort_values(by='day')
	token_transfers_daily = token_transfers_daily.dropna()
	return token_transfers_daily

@st.cache
def load_transfers_daily():
	transfers_daily = pd.read_json("https://node-api.flipsidecrypto.com/api/v2/queries/8476a152-0727-4866-9e21-67286bd1c1ad/data/latest")
	transfers_daily['day'] = pd.to_datetime(transfers_daily['day'])
	transfers_daily = transfers_daily.sort_values(by='day')
	transfers_daily = transfers_daily.dropna()
	return transfers_daily