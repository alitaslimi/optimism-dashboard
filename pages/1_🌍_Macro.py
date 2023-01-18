# Libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.subplots as sp
import plotly.graph_objects as go
import PIL

# Global Variables
theme_plotly = None # None or streamlit
week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# Page Favicon
favicon = PIL.Image.open('favicon.png')

# Layout
st.set_page_config(page_title='Macro - Optimism Mega Dashboard', page_icon=favicon, layout='wide')
st.title('🌍 Macro KPIs')

# Style
with open('style.css')as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)

# Data Sources
@st.cache(ttl=1000, allow_output_mutation=True)
def get_data(query):
    if query == 'Prices Overview':
        return pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/6d1382f2-62fe-493e-8fec-73fb4923fe82/data/latest')
    elif query == 'Prices Daily':
        return pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/7497aa52-9d5a-4f87-9181-3460b9454598/data/latest')
    elif query == 'Blocks Overview':
        return pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/ae07b6ca-1ed1-4f33-9962-82248051615b/data/latest')
    elif query == 'Blocks Daily':
        return pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/305b2656-bb71-4010-b8b5-8bba63251aa4/data/latest')
    elif query == 'Transactions Overview':
        return pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/df60d653-c930-4c8b-923b-d4dfee9f22a9/data/latest')
    elif query == 'Transactions Daily':
        return pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/f3765691-7645-4bf8-81a7-488730e7536e/data/latest')
    elif query == 'Transactions Heatmap':
        return pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/656cd42b-7df3-492f-8046-6281fa027954/data/latest')
    elif query == 'Transactions Status Overview':
        return pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/d38298c5-e2b8-46c7-8e1e-3df5e1b1cebe/data/latest')
    elif query == 'Transactions Status Daily':
        return pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/caa89120-cdd2-4c04-8385-3a848a4d7f6c/data/latest')
    return None

prices_overview = get_data('Prices Overview')
prices_daily = get_data('Prices Daily')
blocks_overview = get_data('Blocks Overview')
blocks_daily = get_data('Blocks Daily')
transactions_overview = get_data('Transactions Overview')
transactions_daily = get_data('Transactions Daily')
transactions_heatmap = get_data('Transactions Heatmap')
transactions_status_overview = get_data('Transactions Status Overview')
transactions_status_daily = get_data('Transactions Status Daily')

# Content
tab_overview, tab_heatmap, tab_status, tab_price = st.tabs(['**Overview**', '**Heatmap**', '**Success Rate**', '**OP Price**'])

with tab_overview:
    
    st.subheader('Overview')

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label='**Total Blocks**', value=str(blocks_overview['Blocks'].map('{:,.0f}'.format).values[0]))
        st.metric(label='**Average Block Time**', value=blocks_overview['BlockTime'].round(2), help='seconds')
    with c2:
        st.metric(label='**Total Transactions**', value=str(transactions_overview['Transactions'].map('{:,.0f}'.format).values[0]))
        st.metric(label='**Average TPS**', value=str(transactions_overview['TPS'].map('{:,.2f}'.format).values[0]))
    with c3:
        st.metric(label='**Total Unique Addresses**', value=str(transactions_overview['Users'].map('{:,.0f}'.format).values[0]))
        st.metric(label='**Average Daily Active Users**', value=str(transactions_overview['Users/Day'].map('{:,.0f}'.format).values[0]))

    st.subheader('Activity Over Time')

    interval = st.radio('**Time Interval**', ['Daily', 'Weekly', 'Monthly'], key='transactions_interval', horizontal=True)

    if st.session_state.transactions_interval == 'Daily':
        blocks_over_time = blocks_daily
        transactions_over_time = transactions_daily
    elif st.session_state.transactions_interval == 'Weekly':
        blocks_over_time = blocks_daily
        blocks_over_time = blocks_over_time.groupby([pd.Grouper(freq='W', key='Date')]).agg(
            {'Blocks': 'sum', 'Transactions': 'sum', 'BlockTime': 'mean'}).reset_index()
        transactions_over_time = transactions_daily
        transactions_over_time = transactions_over_time.groupby([pd.Grouper(freq='W', key='Date')]).agg(
            {'Blocks': 'sum', 'Transactions': 'sum', 'Users': 'sum', 'TPS': 'mean'}).reset_index()
    elif st.session_state.transactions_interval == 'Monthly':
        blocks_over_time = blocks_daily
        blocks_over_time = blocks_over_time.groupby([pd.Grouper(freq='MS', key='Date')]).agg(
            {'Blocks': 'sum', 'Transactions': 'sum', 'BlockTime': 'mean'}).reset_index()
        transactions_over_time = transactions_daily
        transactions_over_time = transactions_over_time.groupby([pd.Grouper(freq='MS', key='Date')]).agg(
            {'Blocks': 'sum', 'Transactions': 'sum', 'Users': 'sum', 'TPS': 'mean'}).reset_index()

    fig = sp.make_subplots(specs=[[{'secondary_y': True}]])
    fig.add_trace(go.Bar(x=blocks_over_time['Date'], y=blocks_over_time['Blocks'], name='Blocks'), secondary_y=False)
    fig.add_trace(go.Line(x=transactions_over_time['Date'], y=transactions_over_time['Transactions'], name='Transactions'), secondary_y=True)
    fig.update_layout(title_text='Number of Blocks and Transactions Over Time')
    fig.update_yaxes(title_text='Blocks', secondary_y=False)
    fig.update_yaxes(title_text='Transactions', secondary_y=True)
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

    fig = sp.make_subplots(specs=[[{'secondary_y': True}]])
    fig.add_trace(go.Line(x=blocks_over_time['Date'], y=blocks_over_time['BlockTime'].round(2), name='Block Time'), secondary_y=False)
    fig.add_trace(go.Line(x=transactions_over_time['Date'], y=transactions_over_time['TPS'].round(2), name='TPS'), secondary_y=True)
    fig.update_layout(title_text='Average Block Time and TPS Over Time')
    fig.update_yaxes(title_text='Block Time [s]', secondary_y=False)
    fig.update_yaxes(title_text='TPS', secondary_y=True)
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

    fig = px.area(transactions_over_time, x='Date', y='Users', title='Active Addresses Over Time')
    fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title='Addresses')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

with tab_heatmap:

    st.subheader('Activity Heatmap')

    fig = px.density_heatmap(transactions_heatmap, x='Hour', y='Day', z='Transactions', histfunc='avg', title='Heatmap of Transactions', nbinsx=24)
    fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title=None, xaxis={'dtick': 1}, coloraxis_colorbar=dict(title='Transactions'))
    fig.update_yaxes(categoryorder='array', categoryarray=week_days)
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

    fig = px.density_heatmap(transactions_heatmap, x='Hour', y='Day', z='Blocks', histfunc='avg', title='Heatmap of Blocks', nbinsx=24)
    fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title=None, xaxis={'dtick': 1}, coloraxis_colorbar=dict(title='Blocks'))
    fig.update_yaxes(categoryorder='array', categoryarray=week_days)
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

    fig = px.density_heatmap(transactions_heatmap, x='Hour', y='Day', z='Users', histfunc='avg', title='Heatmap of Active Addresses', nbinsx=24)
    fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title=None, xaxis={'dtick': 1}, coloraxis_colorbar=dict(title='Users'))
    fig.update_yaxes(categoryorder='array', categoryarray=week_days)
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

with tab_status:

    st.subheader('Overview')

    c1, c2, c3 = st.columns(3)
    with c1:
        fig = px.pie(transactions_status_overview, values='Transactions', names='Status', title='Share of Total Transactions', hole=0.4)
        fig.update_traces(showlegend=False, textinfo='percent+label', textposition='inside')
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
    with c2:
        fig = px.pie(transactions_status_overview, values='Users', names='Status', title='Share of Total Users', hole=0.4)
        fig.update_traces(showlegend=False, textinfo='percent+label', textposition='inside')
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
    with c3:
        fig = px.pie(transactions_status_overview, values='Fees', names='Status', title='Share of Total Fees', hole=0.4)
        fig.update_traces(showlegend=False, textinfo='percent+label', textposition='inside')
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

    st.subheader('Success Rate Over Time')

    interval = st.radio('**Time Interval**', ['Daily', 'Weekly', 'Monthly'], key='success_interval', horizontal=True)

    if st.session_state.success_interval == 'Daily':
        df = transactions_status_daily
    elif st.session_state.success_interval == 'Weekly':
        df = transactions_status_daily
        df = df.groupby([pd.Grouper(freq='W', key='Date'), 'Status']).agg(
            {'Blocks': 'sum', 'Transactions': 'sum', 'Users': 'sum', 'Gas': 'sum', 'Fees': 'sum'}).reset_index()
    elif st.session_state.success_interval == 'Monthly':
        df = transactions_status_daily
        df = df.groupby([pd.Grouper(freq='MS', key='Date'), 'Status']).agg(
            {'Blocks': 'sum', 'Transactions': 'sum', 'Users': 'sum', 'Gas': 'sum', 'Fees': 'sum'}).reset_index()

    fig = px.line(df, x='Date', y='Transactions', color='Status', custom_data=['Status'], title='Transactions Over Time')
    fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title='Transactions', hovermode='x unified')
    fig.update_traces(hovertemplate='%{customdata}: %{y:,.0f}<extra></extra>')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

    fig = px.line(df, x='Date', y='Users', color='Status', custom_data=['Status'], title='Users Over Time')
    fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title='Transactions', hovermode='x unified')
    fig.update_traces(hovertemplate='%{customdata}: %{y:,.0f}<extra></extra>')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

    fig = px.line(df, x='Date', y='Fees', color='Status', custom_data=['Status'], title='Fees Over Time')
    fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title='Fees [USD]', hovermode='x unified')
    fig.update_traces(hovertemplate='%{customdata}: %{y:,.2f}<extra></extra>')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

with tab_price:

    st.subheader('Overview')

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(label='**Latest Price**', value=str(prices_overview['Price'].map('{:,.4f}'.format).values[0]), help='USD')
    with c2:
        st.metric(label='**7 Day Moving Average**', value=str(prices_overview['7D-MA'].map('{:,.4f}'.format).values[0]), help='USD')
    with c3:
        st.metric(label='**All Time High**', value=str(prices_overview['ATH'].map('{:,.4f}'.format).values[0]), help='USD')
    with c4:
        st.metric(label='**All Time Low**', value=str(prices_overview['ATL'].map('{:,.4f}'.format).values[0]), help='USD')

    st.subheader('Activity Over Time')

    interval = st.radio('**Time Interval**', ['Daily', 'Weekly', 'Monthly'], key='prices_interval', horizontal=True)

    if st.session_state.prices_interval == 'Daily':
        price_over_time = prices_daily
    elif st.session_state.prices_interval == 'Weekly':
        price_over_time = prices_daily
        price_over_time = price_over_time.groupby([pd.Grouper(freq='W', key='Date')]).agg('mean').reset_index()
    elif st.session_state.prices_interval == 'Monthly':
        price_over_time = prices_daily
        price_over_time = price_over_time.groupby([pd.Grouper(freq='MS', key='Date')]).agg('mean').reset_index()

    fig = sp.make_subplots(specs=[[{'secondary_y': True}]])
    fig.add_trace(go.Bar(x=price_over_time['Date'], y=price_over_time['Change'], name='Change'), secondary_y=False)
    fig.add_trace(go.Line(x=price_over_time['Date'], y=price_over_time['OP'], name='OP'), secondary_y=True)
    fig.update_layout(title_text='OP Price and Its Percentage Change Over Time')
    fig.update_yaxes(title_text='Change [%]', secondary_y=False)
    fig.update_yaxes(title_text='Price [USD]', secondary_y=True)
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

    fig = sp.make_subplots(specs=[[{'secondary_y': True}]])
    fig.add_trace(go.Line(x=price_over_time['Date'], y=price_over_time['OP'], name='OP'), secondary_y=False)
    fig.add_trace(go.Line(x=price_over_time['Date'], y=price_over_time['ETH'], name='ETH'), secondary_y=True)
    fig.update_layout(title_text='Price Correlation of OP with ETH Over Time')
    fig.update_yaxes(title_text='OP [OP]', secondary_y=False)
    fig.update_yaxes(title_text='ETH [USD]', secondary_y=True)
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

    fig = sp.make_subplots(specs=[[{'secondary_y': True}]])
    fig.add_trace(go.Line(x=price_over_time['Date'], y=price_over_time['OP'], name='OP'), secondary_y=False)
    fig.add_trace(go.Line(x=price_over_time['Date'], y=price_over_time['BTC'], name='BTC'), secondary_y=True)
    fig.update_layout(title_text='Price Correlation of OP with BTC Over Time')
    fig.update_yaxes(title_text='OP [OP]', secondary_y=False)
    fig.update_yaxes(title_text='BTC [USD]', secondary_y=True)
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)