# Libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.subplots as sp
import plotly.graph_objects as go
import PIL

# Global Variables
theme_plotly = None # None or streamlit

# Page Favicon
favicon = PIL.Image.open('favicon.png')

# Layout
st.set_page_config(page_title='Governance - Optimism Mega Dashboard', page_icon=favicon, layout='wide')
st.title('🌍 Governance')

# Style
with open('style.css')as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)

# Data Sources
@st.cache(ttl=1000, allow_output_mutation=True)
def get_data(query):
    if query == 'Airdrops Overview':
        return pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/c9975ac7-ff80-4727-9871-50854a4d09c4/data/latest')
    elif query == 'Airdrops Daily':
        return pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/ed708971-8811-46cb-b905-414203330493/data/latest')
    elif query == 'Airdrops Holdings':
        return pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/9a7e04a7-00e2-4326-a988-eecdc0de73a7/data/latest')
    elif query == 'Delegations Overview':
        return pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/cc6eaf1d-b3db-4899-9ad9-16e1ca45bee4/data/latest')
    elif query == 'Delegations Daily':
        return pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/5a09b40d-0002-40df-a895-0e1d27d8bc24/data/latest')
    elif query == 'Delegations Delegates':
        return pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/e4db6425-591c-497d-95a9-59baf46c72b1/data/latest')
    return None

airdrops_overview = get_data('Airdrops Overview')
airdrops_daily = get_data('Airdrops Daily')
airdrops_holdings = get_data('Airdrops Holdings')
delegations_overview = get_data('Delegations Overview')
delegations_daily = get_data('Delegations Daily')
delegations_delegates = get_data('Delegations Delegates')

# Content
tab_airdrop, tab_delegations = st.tabs(['**Airdrops**', '**Delegations**'])

with tab_airdrop:
    st.subheader('Overview')

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label='**Eligible Users**', value=str(airdrops_overview['EligibleUsers'].map('{:,.0f}'.format).values[0]))
        st.metric(label='**Allocated OP Tokens**', value=str(airdrops_overview['AllocatedTokens'].map('{:,.0f}'.format).values[0]))
    with c2:
        st.metric(label='**Airdrop Receivers**', value=str(airdrops_overview['Receivers'].map('{:,.0f}'.format).values[0]))
        st.metric(label='**Airdropped OP Tokens**', value=str(airdrops_overview['Amount'].map('{:,.0f}'.format).values[0]))
    with c3:
        st.metric(label='**Claimed Users**', value=str(airdrops_overview['ClaimedUsers'].map('{:,.0f}'.format).values[0]), help='%')
        st.metric(label='**Claimed OP Tokens**', value=str(airdrops_overview['ClaimedAmount'].map('{:,.0f}'.format).values[0]), help='%')

    st.subheader('Holding Behavior')

    st.write("""
        Eligible addresses who claimed their OP tokens have shown different behavior towards their tokens.
        These addresses were divided into three different categories based on their holdings.
        If the holdings was higher than the airdropped amount, it meant that not only the address held its OP,
        but also it added more tokens to its balance. If the holdings of the address was equal to the airdropped
        amount, it meant that the address was an idle wallet which neither add nor remove tokens from its holding.
        Ultimately, if the holdings of the address was less than the airdropped amount, it meant that the address
        sold or transferred its tokens and did not hold them for longer period.
    """)

    c1, c2, c3 = st.columns(3)
    with c1:
        fig = px.pie(airdrops_holdings, values='Claimers', names='Status', title='Share of Claimers', hole=0.4)
        fig.update_traces(showlegend=False, textinfo='percent+label', textposition='inside')
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
    with c2:
        fig = px.bar(airdrops_holdings, x='Status', y='HoldingsAverage', color='Status', title='Average Holding Volume')
        fig.update_layout(showlegend=False, yaxis_title='Volume [OP]')
        fig.update_xaxes(title=None, categoryorder='total ascending')
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
    with c3:
        fig = px.pie(airdrops_holdings, values='Volume', names='Status', title='Share of Holding Volume', hole=0.4)
        fig.update_traces(showlegend=False, textinfo='percent+label', textposition='inside')
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

    st.subheader('Activity Over Time')

    interval = st.radio('**Time Interval**', ['Daily', 'Weekly', 'Monthly'], key='airdrops_interval', horizontal=True)

    if st.session_state.airdrops_interval == 'Daily':
        df = airdrops_daily
    elif st.session_state.airdrops_interval == 'Weekly':
        df = airdrops_daily.groupby([pd.Grouper(freq='W', key='Date')]).agg('sum').reset_index()
    elif st.session_state.airdrops_interval == 'Monthly':
        df = airdrops_daily.groupby([pd.Grouper(freq='MS', key='Date')]).agg('sum').reset_index()

    fig = sp.make_subplots(specs=[[{'secondary_y': True}]])
    fig.add_trace(go.Line(x=df['Date'], y=df['Amount'], name='Amount'), secondary_y=False)
    fig.add_trace(go.Line(x=df['Date'], y=df['Receivers'], name='Receivers'), secondary_y=True)
    fig.update_layout(title_text='OP Airdropped Amount and Receivers Over Time')
    fig.update_yaxes(title_text='Amount [OP]', secondary_y=False, type='log')
    fig.update_yaxes(title_text='Receivers', secondary_y=True, type='log')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

with tab_delegations:
    st.subheader('Overview')

    c1, c2, c3 = st.columns(3)
    with c1:
        fig = px.pie(delegations_overview, values='Delegations', names='Type', title='Share of Total Delegations', hole=0.4)
        fig.update_traces(showlegend=False, textinfo='percent+label', textposition='inside')
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
    with c2:
        fig = px.pie(delegations_overview, values='Delegators', names='Type', title='Share of Total Delegators', hole=0.4)
        fig.update_traces(showlegend=False, textinfo='percent+label', textposition='inside')
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
    with c3:
        fig = px.pie(delegations_overview, values='Delegates', names='Type', title='Share of Total Delegates', hole=0.4)
        fig.update_traces(showlegend=False, textinfo='percent+label', textposition='inside')
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

    st.subheader('Activity Over Time')

    interval = st.radio('**Time Interval**', ['Daily', 'Weekly', 'Monthly'], key='delegations_interval', horizontal=True)

    if st.session_state.delegations_interval == 'Daily':
        df = delegations_daily
    elif st.session_state.delegations_interval == 'Weekly':
        df = delegations_daily.groupby([pd.Grouper(freq='W', key='Date'), 'Type']).agg('sum').reset_index()
    elif st.session_state.delegations_interval == 'Monthly':
        df = delegations_daily.groupby([pd.Grouper(freq='MS', key='Date'), 'Type']).agg('sum').reset_index()

    fig = px.line(df, x='Date', y='Delegations', color='Type', custom_data=['Type'], title='Delegations Over Time', log_y=True)
    fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title='Addresses', hovermode='x unified')
    fig.update_traces(hovertemplate='%{customdata}: %{y:,.0f}<extra></extra>')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

    fig = px.line(df, x='Date', y='Delegators', color='Type', custom_data=['Type'], title='Delegators Over Time', log_y=True)
    fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title='Addresses', hovermode='x unified')
    fig.update_traces(hovertemplate='%{customdata}: %{y:,.0f}<extra></extra>')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

    fig = px.line(df, x='Date', y='Delegates', color='Type', custom_data=['Type'], title='Delegates Over Time', log_y=True)
    fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title='Addresses', hovermode='x unified')
    fig.update_traces(hovertemplate='%{customdata}: %{y:,.0f}<extra></extra>')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
    
    st.subheader('Top Delegates')

    df = delegations_delegates.sort_values(by='Amount', ascending=False).head(20)
    fig = px.bar(df, x='Delegate', y='Amount', color='Delegate', title='Total Delegated OP of Top Delegates')
    fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title='Amount [OP]')
    fig.update_xaxes(type='category', categoryorder='total ascending')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)