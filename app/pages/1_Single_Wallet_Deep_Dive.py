import streamlit as st
import plotly.express as px

from utils.data_loaders import *
from utils.df_grid_builder import df_grid_builder

st.title("Wallet Profiler")
transfers = load_transfers()
transfers_x = transfers.set_index("ORIGIN_TO_ADDRESS")
transfers_x = pd.DataFrame(transfers_x.index.unique())

# st.write(transfers_x)
transfers_y = transfers.set_index("ORIGIN_FROM_ADDRESS")
transfers_y = pd.DataFrame(transfers_y.index.unique())
# st.write(transfers_y)
merged_Frame = pd.merge(transfers_y, transfers_x, right_on = "ORIGIN_TO_ADDRESS", left_on= "ORIGIN_FROM_ADDRESS" , how = 'outer')
# st.write(merged_Frame)

merged_Frame = merged_Frame.dropna()
merged_Frame_fix = pd.DataFrame()
merged_Frame_fix['addy'] = merged_Frame['ORIGIN_FROM_ADDRESS']
# st.write(merged_Frame_fix)

# st.write(celsius_accounts)
wallet_address = st.selectbox("Choose a wallet", merged_Frame_fix)



# if 'error' in response:
# 	wallet_address = st.selectbox("Choose a wallet", transfers_x.index.unique())

# else:
# 	wallet_address_2 = st.selectbox("Choose a wallet", transfers_y.index.unique())

def wallet_balance_section():

	try:
		st.header("Wallet Balance")
		balances = load_balances()
		filtered_balances = balances.set_index("USER_ADDRESS").loc[wallet_address]
		filtered_balances = filtered_balances.sort_values(by=['TOTAL_BALANCE_USD','day'], ascending=False)
		title=f'Daily Total Balances for {wallet_address} <br><sup>Some tokens might not appear due to them being illiquid</sup>'
		fig = px.bar(filtered_balances, x='day', y='TOTAL_BALANCE_USD', color='SYMBOL', title=title)
		fig.update_layout(xaxis_title="Day", yaxis_title="Total Balance (USD)")
		fig.update_layout(height=600)
		st.write(fig)

	except KeyError as e:
		st.write("try anouther")


def eth_counterparties_section():

	try:
		
		st.header("ETH Counterparties")
		transfers = load_transfers()


		transfers_O = transfers
		transfers_I = transfers
		incoming = transfers_I.set_index("ORIGIN_TO_ADDRESS").loc[wallet_address]
		outgoing = transfers_O.set_index("ORIGIN_FROM_ADDRESS").loc[wallet_address]

		# st.write(outgoing)
		# st.write(incoming)
		# incoming = incoming.sort_values(['TRANSFER_VOLUME_USD'], ascending=False).reset_index(drop=True)
		incoming = incoming[['FROM_ADDRESS_NAME', 'FROM_PROJECT_NAME', 'TRANSFER_COUNT', 'TRANSFER_VOLUME_USD', 'ORIGIN_FROM_ADDRESS']]
		# outgoing = outgoing.sort_values(['TRANSFER_VOLUME_USD'], ascending=False).reset_index(drop=True)
		outgoing = outgoing[['TO_ADDRESS_NAME', 'TO_PROJECT_NAME', 'TRANSFER_COUNT', 'TRANSFER_VOLUME_USD', 'ORIGIN_TO_ADDRESS']]

		col1, col2 = st.columns(2)
		col1.metric('Total Incoming Transfers Count', value=incoming['TRANSFER_COUNT'].sum())
		col2.metric('Total Outgoing Transfers Count', value=outgoing['TRANSFER_COUNT'].sum())
		col1.metric('Total Incoming Transfers USD Volume', value=f"${incoming['TRANSFER_VOLUME_USD'].sum():20,.2f}")
		col2.metric('Total Outgoing Transfers USD Volume', value=f"${outgoing['TRANSFER_VOLUME_USD'].sum():20,.2f}")

		show_top_interacting_wallets = st.checkbox("Show top interacting wallets (ETH transfer)")
		if show_top_interacting_wallets:
			try:
				st.subheader("Top-Interacting Wallets (ETH Transfer)")
				st.text("Incoming")
				df_grid_builder(incoming)
				st.text("Outgoing")
				df_grid_builder(outgoing)
			except AttributeError as e:
				st.write("empty here")
		show_agg_transfers = st.checkbox("Show aggregated transfers (ETH transfer)")
		if show_agg_transfers:
			try:
				st.subheader("Transfers Aggregated by Wallet Label (ETH Transfer)")
				st.text("Incoming")
				tmp = outgoing.groupby("TO_ADDRESS_NAME").sum().sort_values(by=['TRANSFER_VOLUME_USD'], ascending=False)
				df_grid_builder(tmp)
				st.text("Outgoing")
				incoming.groupby("FROM_ADDRESS_NAME").sum().sort_values(by=['TRANSFER_VOLUME_USD'], ascending=False)
				df_grid_builder(tmp)
			except AttributeError as e:
				st.write("empty here")
	except KeyError as e:
		st.write("try anouther")





	# transfers = transfers.set_index("ORIGIN_TO_ADDRESS")

	# st.write("transfers", transfers.index)
	# st.write(wallet_address)





def token_counterparties_section():




	try:
		st.header("Token Counterparties")
		token_transfers = load_token_transfers()
		transfers_O_T = token_transfers
		transfers_I_T = token_transfers

		outgoing = transfers_O_T.set_index("FROM_ADDRESS").loc[wallet_address]
		incoming = transfers_I_T.set_index("TO_ADDRESS").loc[wallet_address]
		incoming = incoming.sort_values(['TRANSFER_VOLUME_USD'], ascending=False).reset_index(drop=True)
		incoming = incoming[['SYMBOL', 'FROM_ADDRESS_NAME', 'FROM_PROJECT_NAME', 'TRANSFER_COUNT', 'TRANSFER_VOLUME_USD', 'FROM_ADDRESS']]
		outgoing = outgoing.sort_values(['TRANSFER_VOLUME_USD'], ascending=False).reset_index(drop=True)
		outgoing = outgoing[['SYMBOL', 'TO_ADDRESS_NAME', 'TO_PROJECT_NAME', 'TRANSFER_COUNT', 'TRANSFER_VOLUME_USD', 'TO_ADDRESS']]

		col1, col2 = st.columns(2)
		col1.metric('Total Incoming Transfers Count', value=incoming['TRANSFER_COUNT'].sum())
		col2.metric('Total Outgoing Transfers Count', value=outgoing['TRANSFER_COUNT'].sum())
		col1.metric('Total Incoming Transfers USD Volume', value=f"${incoming['TRANSFER_VOLUME_USD'].sum():20,.2f}")
		col2.metric('Total Outgoing Transfers USD Volume', value=f"${outgoing['TRANSFER_VOLUME_USD'].sum():20,.2f}")

		show_top_interacting_wallets = st.checkbox("Show top interacting wallets (ERC-20 transfer)")
		if show_top_interacting_wallets:
			st.subheader("Top-Interacting Wallets (ERC-20 Transfer)")
			st.text("Incoming")
			df_grid_builder(incoming)
			st.text("Outgoing")
			df_grid_builder(outgoing)

		show_agg_transfers = st.checkbox("Show aggregated transfers (ERC-20 transfer)")
		if show_agg_transfers:
			st.subheader("Transfers Aggregated by Wallet Label (ERC-20 Transfer)")
			st.text("Incoming")
			tmp = outgoing.groupby("TO_ADDRESS_NAME").sum().sort_values(by=['TRANSFER_VOLUME_USD'], ascending=False)
			df_grid_builder(tmp)
			st.text("Outgoing")
			tmp = incoming.groupby("FROM_ADDRESS_NAME").sum().sort_values(by=['TRANSFER_VOLUME_USD'], ascending=False)
			df_grid_builder(tmp)

			st.subheader("Transfers Aggregated by Token (ERC-20 Transfer)")
			st.text("Incoming")
			incoming_agg_symbol = incoming.groupby("SYMBOL").sum().sort_values(by=['TRANSFER_VOLUME_USD'], ascending=False)
			incoming_agg_symbol['TRANSFER_VOLUME_USD_PCT'] = 100*incoming_agg_symbol['TRANSFER_VOLUME_USD']/incoming_agg_symbol['TRANSFER_VOLUME_USD'].sum()
			df_grid_builder(incoming_agg_symbol)
			st.text("Outgoing")
			outgoing_agg_symbol = outgoing.groupby("SYMBOL").sum().sort_values(by=['TRANSFER_VOLUME_USD'], ascending=False)
			outgoing_agg_symbol['TRANSFER_VOLUME_USD_PCT'] = 100*outgoing_agg_symbol['TRANSFER_VOLUME_USD']/outgoing_agg_symbol['TRANSFER_VOLUME_USD'].sum()
			df_grid_builder(outgoing_agg_symbol)

	except KeyError as e:
		st.write("try anouther")




wallet_balance_section()
eth_counterparties_section()
token_counterparties_section()


