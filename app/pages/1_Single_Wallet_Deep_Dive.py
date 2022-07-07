import streamlit as st
import plotly.express as px

from utils.data_loaders import *
# from utils.df_grid_builder import df_grid_builder

st.title("Wallet Profiler")

def wallet_balance_section():
	st.header("Wallet Balance")
	balances = load_balances()

	filtered_balances = balances[balances['USER_ADDRESS']==wallet_address].dropna()
	filtered_balances = filtered_balances.sort_values(by=['TOTAL_BALANCE_USD','day'], ascending=False)
	title=f'Daily Total Balances for {wallet_address} <br><sup>Some tokens might not appear due to them being illiquid</sup>'
	fig = px.bar(filtered_balances, x='day', y='TOTAL_BALANCE_USD', color='SYMBOL', title=title)
	fig.update_layout(xaxis_title="Day", yaxis_title="Total Balance (USD)")
	fig.update_layout(height=600)
	st.write(fig)

def eth_counterparties_section():
	st.header("ETH Counterparties")
	transfers = load_transfers()
	outgoing = transfers[transfers['ORIGIN_FROM_ADDRESS']==wallet_address]
	incoming = transfers[transfers['ORIGIN_TO_ADDRESS']==wallet_address]

	incoming = incoming.sort_values(['TRANSFER_VOLUME_USD'], ascending=False).reset_index(drop=True)
	incoming = incoming[['FROM_ADDRESS_NAME', 'FROM_PROJECT_NAME', 'TRANSFER_COUNT', 'TRANSFER_VOLUME_USD', 'ORIGIN_FROM_ADDRESS']]
	outgoing = outgoing.sort_values(['TRANSFER_VOLUME_USD'], ascending=False).reset_index(drop=True)
	outgoing = outgoing[['TO_ADDRESS_NAME', 'TO_PROJECT_NAME', 'TRANSFER_COUNT', 'TRANSFER_VOLUME_USD', 'ORIGIN_TO_ADDRESS']]

	col1, col2 = st.columns(2)
	col1.metric('Total Incoming Transfers Count', value=incoming['TRANSFER_COUNT'].sum())
	col2.metric('Total Outgoing Transfers Count', value=outgoing['TRANSFER_COUNT'].sum())
	col1.metric('Total Incoming Transfers USD Volume', value=f"${incoming['TRANSFER_VOLUME_USD'].sum():20,.2f}")
	col2.metric('Total Outgoing Transfers USD Volume', value=f"${outgoing['TRANSFER_VOLUME_USD'].sum():20,.2f}")

	show_top_interacting_wallets = st.checkbox("Show top interacting wallets (ETH transfer)")
	if show_top_interacting_wallets:
		st.subheader("Top-Interacting Wallets (ETH Transfer)")
		st.text("Incoming")
		st.write(incoming)
		st.text("Outgoing")
		st.write(outgoing)
	
	show_agg_transfers = st.checkbox("Show aggregated transfers (ETH transfer)")
	if show_agg_transfers:
		st.subheader("Transfers Aggregated by Wallet Label (ETH Transfer)")
		st.text("Incoming")
		tmp = outgoing.groupby("TO_ADDRESS_NAME").sum().sort_values(by=['TRANSFER_VOLUME_USD'], ascending=False)
		st.write(tmp)
		st.text("Outgoing")
		incoming.groupby("FROM_ADDRESS_NAME").sum().sort_values(by=['TRANSFER_VOLUME_USD'], ascending=False)
		st.write(tmp)

def token_counterparties_section():
	st.header("Token Counterparties")
	token_transfers = load_token_transfers()
	outgoing = token_transfers[token_transfers['FROM_ADDRESS']==wallet_address]
	incoming = token_transfers[token_transfers['TO_ADDRESS']==wallet_address]
	incoming = incoming.sort_values(['TRANSFER_VOLUME_USD'], ascending=False).reset_index(drop=True)
	incoming = incoming[['SYMBOL', 'FROM_ADDRESS_NAME', 'FROM_PROJECT_NAME', 'TRANSFER_COUNT', 'TRANSFER_VOLUME_USD', 'ORIGIN_FROM_ADDRESS']]
	outgoing = outgoing.sort_values(['TRANSFER_VOLUME_USD'], ascending=False).reset_index(drop=True)
	outgoing = outgoing[['SYMBOL', 'TO_ADDRESS_NAME', 'TO_PROJECT_NAME', 'TRANSFER_COUNT', 'TRANSFER_VOLUME_USD', 'ORIGIN_TO_ADDRESS']]

	col1, col2 = st.columns(2)
	col1.metric('Total Incoming Transfers Count', value=incoming['TRANSFER_COUNT'].sum())
	col2.metric('Total Outgoing Transfers Count', value=outgoing['TRANSFER_COUNT'].sum())
	col1.metric('Total Incoming Transfers USD Volume', value=f"${incoming['TRANSFER_VOLUME_USD'].sum():20,.2f}")
	col2.metric('Total Outgoing Transfers USD Volume', value=f"${outgoing['TRANSFER_VOLUME_USD'].sum():20,.2f}")

	show_top_interacting_wallets = st.checkbox("Show top interacting wallets (ERC-20 transfer)")
	if show_top_interacting_wallets:
		st.subheader("Top-Interacting Wallets (ERC-20 Transfer)")
		st.text("Incoming")
		st.write(incoming)
		st.text("Outgoing")
		st.write(outgoing)

	show_agg_transfers = st.checkbox("Show aggregated transfers (ERC-20 transfer)")
	if show_agg_transfers:
		st.subheader("Transfers Aggregated by Wallet Label (ERC-20 Transfer)")
		st.text("Incoming")
		tmp = outgoing.groupby("TO_ADDRESS_NAME").sum().sort_values(by=['TRANSFER_VOLUME_USD'], ascending=False)
		st.write(tmp)
		st.text("Outgoing")
		tmp = incoming.groupby("FROM_ADDRESS_NAME").sum().sort_values(by=['TRANSFER_VOLUME_USD'], ascending=False)
		st.write(tmp)

		st.subheader("Transfers Aggregated by Token (ERC-20 Transfer)")
		st.text("Incoming")
		incoming_agg_symbol = incoming.groupby("SYMBOL").sum().sort_values(by=['TRANSFER_VOLUME_USD'], ascending=False)
		incoming_agg_symbol['TRANSFER_VOLUME_USD_PCT'] = 100*incoming_agg_symbol['TRANSFER_VOLUME_USD']/incoming_agg_symbol['TRANSFER_VOLUME_USD'].sum()
		st.write(incoming_agg_symbol)
		st.text("Outgoing")
		outgoing_agg_symbol = outgoing.groupby("SYMBOL").sum().sort_values(by=['TRANSFER_VOLUME_USD'], ascending=False)
		outgoing_agg_symbol['TRANSFER_VOLUME_USD_PCT'] = 100*outgoing_agg_symbol['TRANSFER_VOLUME_USD']/outgoing_agg_symbol['TRANSFER_VOLUME_USD'].sum()
		st.write(outgoing_agg_symbol)

wallet_address = st.selectbox("Choose a wallet", list(load_celsius_accounts()['ADDRESS'].unique()))
wallet_balance_section()
eth_counterparties_section()
token_counterparties_section()


