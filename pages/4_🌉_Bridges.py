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
st.set_page_config(page_title='Bridges - Optimism Mega Dashboard', page_icon=favicon, layout='wide')
st.title('🌉 Bridges')

# Style
with open('style.css')as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)

# Data Sources
@st.cache(ttl=3600)
def get_data(query):
    if query == 'Bridges Overview':
        return pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/0eb7ce61-825c-4047-8845-6e56950f0c46/data/latest')
    elif query == 'Bridges Daily':
        return pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/38b44e33-6817-4186-814d-423ca30a0470/data/latest')
    elif query == 'Bridges Protocols Overview':
        return pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/d74f6b01-ad6e-42a5-a56a-f9d59b71fbcb/data/latest')
    elif query == 'Bridges Protocols Daily':
        return pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/1fda50b0-f12a-4b8b-b5e4-48777a4a7801/data/latest')
    elif query == 'Bridges Tokens Overview':
        return pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/13c6741f-4097-47f8-bacf-fec9f105ca6e/data/latest')
    elif query == 'Bridges Tokens Daily':
        return pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/15172a48-0ee7-4926-b05d-d4bf579127d6/data/latest')
    return None

bridges_overview = get_data('Bridges Overview')
bridges_daily = get_data('Bridges Daily')
bridges_protocols_overview = get_data('Bridges Protocols Overview')
bridges_protocols_daily = get_data('Bridges Protocols Daily')
bridges_tokens_overview = get_data('Bridges Tokens Overview')
bridges_tokens_daily = get_data('Bridges Tokens Daily')

# Content
tab_overview, tab_protocols, tab_tokens = st.tabs(['**Overview**', '**Protocols**', '**Tokens**'])

with tab_overview:

    st.subheader('Overview of Rainbow Bridge')

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label='**Total Bridged Volume**', value=str(bridges_overview['Volume'].map('{:,.0f}'.format).values[0]), help='USD')
        st.metric(label='**Average Bridged Amount**', value=str(bridges_overview['AmountAverage'].map('{:,.0f}'.format).values[0]), help='USD')
    with c2:
        st.metric(label='**Total Bridge Transactions**', value=str(bridges_overview['Transactions'].map('{:,.0f}'.format).values[0]))
        st.metric(label='**Median Bridged Amount**', value=str(bridges_overview['AmountMedian'].map('{:,.0f}'.format).values[0]), help='USD')
    with c3:
        st.metric(label='**Total Bridgers**', value=str(bridges_overview['Bridgers'].map('{:,.0f}'.format).values[0]))
        st.metric(label='**Bridge Protocols**', value=str(bridges_overview['Protocols'].map('{:,.0f}'.format).values[0]))

    st.subheader('Activity Over Time')

    interval = st.radio('**Time Interval**', ['Daily', 'Weekly', 'Monthly'], key='bridges_interval', horizontal=True)

    if st.session_state.bridges_interval == 'Daily':
        bridges_over_time = bridges_daily
    elif st.session_state.bridges_interval == 'Weekly':
        bridges_over_time = bridges_daily
        bridges_over_time = bridges_over_time.groupby(pd.Grouper(freq='W', key='Date')).agg(
            {'Transactions': 'sum', 'Bridgers': 'sum', 'Volume': 'sum', 'AmountAverage': 'mean', 'AmountMedian': 'mean'}).reset_index()
    elif st.session_state.bridges_interval == 'Monthly':
        bridges_over_time = bridges_daily
        bridges_over_time = bridges_over_time.groupby(pd.Grouper(freq='M', key='Date')).agg(
            {'Transactions': 'sum', 'Bridgers': 'sum', 'Volume': 'sum', 'AmountAverage': 'mean', 'AmountMedian': 'mean'}).reset_index()

    fig = px.area(bridges_over_time, x='Date', y='Volume', title='Bridged Volume Over Time')
    fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title='Volume [USD]')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

    fig = sp.make_subplots()
    fig.add_trace(go.Bar(x=bridges_over_time['Date'], y=bridges_over_time['Transactions'], name='Transactions'))
    fig.add_trace(go.Line(x=bridges_over_time['Date'], y=bridges_over_time['Bridgers'], name='Bridgers'))
    fig.update_layout(title_text='Bridge Transactions and Bridgers Over Time')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

    fig = sp.make_subplots(specs=[[{'secondary_y': True}]])
    fig.add_trace(go.Line(x=bridges_over_time['Date'], y=bridges_over_time['AmountAverage'], name='Average'), secondary_y=False)
    fig.add_trace(go.Line(x=bridges_over_time['Date'], y=bridges_over_time['AmountMedian'], name='Median'), secondary_y=True)
    fig.update_layout(title_text='Average and Median Bridged Amount Over Time')
    fig.update_yaxes(title_text='Average [USD]', secondary_y=False)
    fig.update_yaxes(title_text='Median [USD]', secondary_y=True)
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

with tab_protocols:

    st.subheader('Market Shares')

    c1, c2, c3 = st.columns(3)
    with c1:
        fig = px.pie(bridges_protocols_overview, values='Volume', names='Protocol', title='Share of Total Bridged Volume', hole=0.4)
        fig.update_traces(showlegend=False, textinfo='percent+label', textposition='inside')
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
    with c2:
        fig = px.pie(bridges_protocols_overview, values='Transactions', names='Protocol', title='Share of Total Transactions', hole=0.4)
        fig.update_traces(showlegend=False, textinfo='percent+label', textposition='inside')
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
    with c3:
        fig = px.pie(bridges_protocols_overview, values='Bridgers', names='Protocol', title='Share of Total Bridgers', hole=0.4)
        fig.update_traces(showlegend=False, textinfo='percent+label', textposition='inside')
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

    st.subheader('Activity Over Time')

    interval = st.radio('**Time Interval**', ['Daily', 'Weekly', 'Monthly'], key='protocols_interval', horizontal=True)

    if st.session_state.protocols_interval == 'Daily':
        df = bridges_protocols_daily
        df = df.groupby(['Date', 'Protocol']).agg(
            {'Transactions': 'sum', 'Bridgers': 'sum', 'Volume': 'sum', 'AmountAverage': 'mean', 'AmountMedian': 'mean'}).reset_index()
        df['RowNumber'] = df.groupby('Date')['Volume'].rank(method='max', ascending=False)
        df.loc[df['RowNumber'] > 5, 'Protocol'] = 'Other'
        df = df.groupby(['Date', 'Protocol']).agg(
            {'Transactions': 'sum', 'Bridgers': 'sum', 'Volume': 'sum', 'AmountAverage': 'mean', 'AmountMedian': 'mean'}).reset_index()
    elif st.session_state.protocols_interval == 'Weekly':
        df = bridges_protocols_daily
        df = df.groupby([pd.Grouper(freq='W', key='Date'), 'Protocol']).agg(
            {'Transactions': 'sum', 'Bridgers': 'sum', 'Volume': 'sum', 'AmountAverage': 'mean', 'AmountMedian': 'mean'}).reset_index()
        df['RowNumber'] = df.groupby('Date')['Volume'].rank(method='max', ascending=False)
        df.loc[df['RowNumber'] > 5, 'Protocol'] = 'Other'
        df = df.groupby(['Date', 'Protocol']).agg(
            {'Transactions': 'sum', 'Bridgers': 'sum', 'Volume': 'sum', 'AmountAverage': 'mean', 'AmountMedian': 'mean'}).reset_index()
    elif st.session_state.protocols_interval == 'Monthly':
        df = bridges_protocols_daily
        df = df.groupby([pd.Grouper(freq='M', key='Date'), 'Protocol']).agg(
            {'Transactions': 'sum', 'Bridgers': 'sum', 'Volume': 'sum', 'AmountAverage': 'mean', 'AmountMedian': 'mean'}).reset_index()
        df['RowNumber'] = df.groupby('Date')['Volume'].rank(method='max', ascending=False)
        df.loc[df['RowNumber'] > 5, 'Protocol'] = 'Other'
        df = df.groupby(['Date', 'Protocol']).agg(
            {'Transactions': 'sum', 'Bridgers': 'sum', 'Volume': 'sum', 'AmountAverage': 'mean', 'AmountMedian': 'mean'}).reset_index()

    fig = px.bar(df, x='Date', y='Volume', color='Protocol', custom_data=['Protocol'], title='Bridged Volume Over Time')
    fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title='Volume [USD]', hovermode='x unified')
    fig.update_traces(hovertemplate='%{customdata}: %{y:,.0f}<extra></extra>')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

    fig = px.bar(df, x='Date', y='Transactions', color='Protocol', custom_data=['Protocol'], title='Bridge Transactions Over Time')
    fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title='Transactions', hovermode='x unified')
    fig.update_traces(hovertemplate='%{customdata}: %{y:,.0f}<extra></extra>')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

    fig = px.bar(df, x='Date', y='Bridgers', color='Protocol', custom_data=['Protocol'], title='Bridgers Over Time')
    fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title='Bridgers', hovermode='x unified')
    fig.update_traces(hovertemplate='%{customdata}: %{y:,.0f}<extra></extra>')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

    fig = px.line(df, x='Date', y='AmountAverage', color='Protocol', custom_data=['Protocol'], title='Average Bridged Amount Over Time')
    fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title='Average [USD]', hovermode='x unified')
    fig.update_traces(hovertemplate='%{customdata}: %{y:,.0f}<extra></extra>')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

    fig = px.line(df, x='Date', y='AmountMedian', color='Protocol', custom_data=['Protocol'], title='Median Bridged Amount Over Time')
    fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title='Median [USD]', hovermode='x unified')
    fig.update_traces(hovertemplate='%{customdata}: %{y:,.0f}<extra></extra>')
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

with tab_tokens:

    st.subheader('Market Shares')

    c1, c2, c3 = st.columns(3)
    with c1:
        df = bridges_tokens_overview.sort_values('Volume', ascending=False).reset_index(drop=True)
        df.loc[bridges_tokens_overview.index >= 5, 'Token'] = 'Other'
        fig = px.pie(df, values='Volume', names='Token', title='Share of Total Bridged Volume', hole=0.4)
        fig.update_layout(legend_title=None, legend_y=0.5)
        fig.update_traces(textinfo='percent+label', textposition='inside')
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
    with c2:
        df = bridges_tokens_overview.sort_values('Transactions', ascending=False).reset_index(drop=True)
        df.loc[bridges_tokens_overview.index >= 5, 'Token'] = 'Other'
        fig = px.pie(df, values='Transactions', names='Token', title='Share of Total Transactions', hole=0.4)
        fig.update_layout(legend_title=None, legend_y=0.5)
        fig.update_traces(textinfo='percent+label', textposition='inside')
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
    with c3:
        df = bridges_tokens_overview.sort_values('Bridgers', ascending=False).reset_index(drop=True)
        df.loc[bridges_tokens_overview.index >= 5, 'Token'] = 'Other'
        fig = px.pie(df, values='Bridgers', names='Token', title='Share of Total Bridgers', hole=0.4)
        fig.update_layout(legend_title=None, legend_y=0.5)
        fig.update_traces(textinfo='percent+label', textposition='inside')
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
    
    st.subheader('Bridged Amount')

    c1, c2 = st.columns(2)
    with c1:
        df = bridges_tokens_overview.sort_values('AmountAverage', ascending=False).reset_index(drop=True)
        df.loc[bridges_tokens_overview.index >= 10, 'Token'] = 'Other'
        df = df.groupby(['Token']).agg({'AmountAverage': 'mean'}).reset_index()
        fig = px.bar(df, x='Token', y='AmountAverage', color='Token', title='Average Bridged Amount')
        fig.update_layout(showlegend=False, yaxis_title='Average Amount [USD]')
        fig.update_xaxes(title=None, categoryorder='total ascending')
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
    with c2:
        df = bridges_tokens_overview.sort_values('AmountMedian', ascending=False).reset_index(drop=True)
        df.loc[bridges_tokens_overview.index >= 10, 'Token'] = 'Other'
        df = df.groupby(['Token']).agg({'AmountMedian': 'mean'}).reset_index()
        fig = px.bar(df, x='Token', y='AmountMedian', color='Token', title='Median Bridged Amount')
        fig.update_layout(showlegend=False, yaxis_title='Median Amount [USD]')
        fig.update_xaxes(title=None, categoryorder='total ascending')
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

    st.subheader('Activity Over Time')

    interval = st.radio('**Time Interval**', ['Daily', 'Weekly', 'Monthly'], key='tokens_interval', horizontal=True)

    if st.session_state.tokens_interval == 'Daily':
        df = bridges_tokens_daily
        df = df.groupby(['Date', 'Token']).agg(
            {'Transactions': 'sum', 'Bridgers': 'sum', 'Volume': 'sum', 'AmountAverage': 'mean', 'AmountMedian': 'mean'}).reset_index()
        df['RowNumber'] = df.groupby('Date')['Volume'].rank(method='max', ascending=False)
        df.loc[df['RowNumber'] > 3, 'Token'] = 'Other'
        df = df.groupby(['Date', 'Token']).agg(
            {'Transactions': 'sum', 'Bridgers': 'sum', 'Volume': 'sum', 'AmountAverage': 'mean', 'AmountMedian': 'mean'}).reset_index()
    elif st.session_state.tokens_interval == 'Weekly':
        df = bridges_tokens_daily
        df = df.groupby([pd.Grouper(freq='W', key='Date'), 'Token']).agg(
            {'Transactions': 'sum', 'Bridgers': 'sum', 'Volume': 'sum', 'AmountAverage': 'mean', 'AmountMedian': 'mean'}).reset_index()
        df['RowNumber'] = df.groupby('Date')['Volume'].rank(method='max', ascending=False)
        df.loc[df['RowNumber'] > 3, 'Token'] = 'Other'
        df = df.groupby(['Date', 'Token']).agg(
            {'Transactions': 'sum', 'Bridgers': 'sum', 'Volume': 'sum', 'AmountAverage': 'mean', 'AmountMedian': 'mean'}).reset_index()
    elif st.session_state.tokens_interval == 'Monthly':
        df = bridges_tokens_daily
        df = df.groupby([pd.Grouper(freq='M', key='Date'), 'Token']).agg(
            {'Transactions': 'sum', 'Bridgers': 'sum', 'Volume': 'sum', 'AmountAverage': 'mean', 'AmountMedian': 'mean'}).reset_index()
        df['RowNumber'] = df.groupby('Date')['Volume'].rank(method='max', ascending=False)
        df.loc[df['RowNumber'] > 3, 'Token'] = 'Other'
        df = df.groupby(['Date', 'Token']).agg(
            {'Transactions': 'sum', 'Bridgers': 'sum', 'Volume': 'sum', 'AmountAverage': 'mean', 'AmountMedian': 'mean'}).reset_index()

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(df.sort_values(['Date', 'Volume'], ascending=[True, False]), x='Date', y='Volume', color='Token', custom_data=['Token'], title='Bridged Volume Over Time')
        fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title='Volume [USD]', hovermode='x unified')
        fig.update_traces(hovertemplate='%{customdata}: %{y:,.0f}<extra></extra>')
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

        fig = px.bar(df.sort_values(['Date', 'Transactions'], ascending=[True, False]), x='Date', y='Transactions', color='Token', custom_data=['Token'], title='Bridge Transactions Over Time')
        fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title='Transactions', hovermode='x unified')
        fig.update_traces(hovertemplate='%{customdata}: %{y:,.0f}<extra></extra>')
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

        fig = px.bar(df.sort_values(['Date', 'Bridgers'], ascending=[True, False]), x='Date', y='Bridgers', color='Token', custom_data=['Token'], title='Bridgers Over Time')
        fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title='Bridgers', hovermode='x unified')
        fig.update_traces(hovertemplate='%{customdata}: %{y:,.0f}<extra></extra>')
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

        fig = px.line(df.sort_values(['Date', 'AmountAverage'], ascending=[True, False]), x='Date', y='AmountAverage', color='Token', custom_data=['Token'], title='Average Bridged Amount Over Time')
        fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title='Average Amount [USD]', hovermode='x unified')
        fig.update_traces(hovertemplate='%{customdata}: %{y:,.2f}<extra></extra>')
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
    with c2:
        fig = go.Figure()
        for i in df['Token'].unique():
            fig.add_trace(go.Scatter(
                name=i,
                x=df.query("Token == @i")['Date'],
                y=df.query("Token == @i")['Volume'],
                mode='lines',
                stackgroup='one',
                groupnorm='percent'
            ))
        fig.update_layout(title='Bridged Volume Over Time')
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
        
        fig = go.Figure()
        for i in df['Token'].unique():
            fig.add_trace(go.Scatter(
                name=i,
                x=df.query("Token == @i")['Date'],
                y=df.query("Token == @i")['Transactions'],
                mode='lines',
                stackgroup='one',
                groupnorm='percent'
            ))
        fig.update_layout(title='Bridge Transactions Over Time')
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
        
        fig = go.Figure()
        for i in df['Token'].unique():
            fig.add_trace(go.Scatter(
                name=i,
                x=df.query("Token == @i")['Date'],
                y=df.query("Token == @i")['Bridgers'],
                mode='lines',
                stackgroup='one',
                groupnorm='percent'
            ))
        fig.update_layout(title='Bridgers Over Time')
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

        fig = px.line(df.sort_values(['Date', 'AmountMedian'], ascending=[True, False]), x='Date', y='AmountMedian', color='Token', custom_data=['Token'], title='Median Bridged Amount Over Time')
        fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title='Median Amount [USD]', hovermode='x unified')
        fig.update_traces(hovertemplate='%{customdata}: %{y:,.2f}<extra></extra>')
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)