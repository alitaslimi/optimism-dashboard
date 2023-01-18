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
st.set_page_config(page_title='Gas Fees - Optimism Mega Dashboard', page_icon=favicon, layout='wide')
st.title('🪙 Gas Fees')

# Style
with open('style.css')as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)

# Data Sources
@st.cache(ttl=1000, allow_output_mutation=True)
def get_data(query):
    if query == 'Transactions Overview':
        return pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/df60d653-c930-4c8b-923b-d4dfee9f22a9/data/latest')
    elif query == 'Transactions Daily':
        return pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/f3765691-7645-4bf8-81a7-488730e7536e/data/latest')
    elif query == 'Transactions Heatmap':
        return pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/656cd42b-7df3-492f-8046-6281fa027954/data/latest')
    return None

transactions_overview = get_data('Transactions Overview')
transactions_daily = get_data('Transactions Daily')
transactions_heatmap = get_data('Transactions Heatmap')

# Content
tab_overview, tab_heatmap = st.tabs(['**Overview**', '**Heatmap**'])

with tab_overview:

    st.subheader('Overview')

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(label='**Total Transaction Fees**', value=str(transactions_overview['Fees'].map('{:,.0f}'.format).values[0]), help='USD')
        st.metric(label='**Total Gas Used**', value=str(transactions_overview['Gas'].map('{:,.0f}'.format).values[0]), help='gas')
        st.metric(label='**Maximum Gas Price**', value=str(transactions_overview['GasPriceMax'].map('{:,.0f}'.format).values[0]), help='gwei')
    with c2:
        st.metric(label='**Average Fee Amount**', value=str(transactions_overview['FeeAverage'].map('{:,.2f}'.format).values[0]), help='USD')
        st.metric(label='**Average Gas Amount**', value=str(transactions_overview['GasAverage'].map('{:,.0f}'.format).values[0]), help='gas')
        st.metric(label='**Average Gas Price**', value=str(transactions_overview['GasPriceAverage'].map('{:,.4f}'.format).values[0]), help='gwei')
    with c3:
        st.metric(label='**Median Fee Amount**', value=str(transactions_overview['FeeMedian'].map('{:,.4f}'.format).values[0]), help='USD')
        st.metric(label='**Median Gas Amount**', value=str(transactions_overview['GasMedian'].map('{:,.0f}'.format).values[0]), help='gas')
        st.metric(label='**Median Gas Price**', value=str(transactions_overview['GasPriceMedian'].map('{:,.4f}'.format).values[0]), help='gwei')
    with c4:
        st.metric(label='**Average Fees/Block**', value=str(transactions_overview['Fees/Block'].map('{:,.2f}'.format).values[0]), help='USD')
        st.metric(label='**Average Gas/Block**', value=str(transactions_overview['Gas/Block'].map('{:,.0f}'.format).values[0]), help='gas')
        st.metric(label='**Minimum Gas Price**', value=str(transactions_overview['GasPriceMin'].map('{:,.2f}'.format).values[0]), help='gwei')

    st.subheader('Activity Over Time')

    interval = st.radio('**Time Interval**', ['Daily', 'Weekly', 'Monthly'], key='fees_interval', horizontal=True)

    if st.session_state.fees_interval == 'Daily':
        transactions_over_time = transactions_daily
    elif st.session_state.fees_interval == 'Weekly':
        transactions_over_time = transactions_daily
        transactions_over_time = transactions_over_time.groupby([pd.Grouper(freq='W', key='Date')]).agg(
            {'Fees': 'sum', 'FeeAverage': 'mean', 'FeeMedian': 'mean', 'Fees/Block': 'mean', 'Gas': 'sum', 'GasAverage': 'mean',
                'GasMedian': 'mean', 'Gas/Block': 'mean', 'GasPriceAverage': 'mean', 'GasPriceMedian': 'mean'}).reset_index()
    elif st.session_state.fees_interval == 'Monthly':
        transactions_over_time = transactions_daily
        transactions_over_time = transactions_over_time.groupby([pd.Grouper(freq='MS', key='Date')]).agg(
            {'Fees': 'sum', 'FeeAverage': 'mean', 'FeeMedian': 'mean', 'Fees/Block': 'mean', 'Gas': 'sum', 'GasAverage': 'mean',
                'GasMedian': 'mean', 'Gas/Block': 'mean', 'GasPriceAverage': 'mean', 'GasPriceMedian': 'mean'}).reset_index()

    fig = sp.make_subplots(specs=[[{'secondary_y': True}]])
    fig.add_trace(go.Line(x=transactions_over_time['Date'], y=transactions_over_time['Fees'].round(), name='Fees'), secondary_y=False)
    fig.add_trace(go.Line(x=transactions_over_time['Date'], y=transactions_over_time['Gas'].round(), name='Gas'), secondary_y=True)
    fig.update_layout(title_text='Transaction Fees and Gas Used Over Time')
    fig.update_yaxes(title_text='Fees [USD]', secondary_y=False)
    fig.update_yaxes(title_text='Gas [gas]', secondary_y=True)
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

    fig = sp.make_subplots(specs=[[{'secondary_y': True}]])
    fig.add_trace(go.Line(x=transactions_over_time['Date'], y=transactions_over_time['FeeAverage'].round(4), name='Average Fee'), secondary_y=False)
    fig.add_trace(go.Line(x=transactions_over_time['Date'], y=transactions_over_time['FeeMedian'].round(4), name='Median Fee'), secondary_y=True)
    fig.update_layout(title_text='Average and Median Transaction Fees Over Time')
    fig.update_yaxes(title_text='Average Fee [USD]', secondary_y=False)
    fig.update_yaxes(title_text='Median Fee [USD]', secondary_y=True)
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
    
    fig = sp.make_subplots(specs=[[{'secondary_y': True}]])
    fig.add_trace(go.Line(x=transactions_over_time['Date'], y=transactions_over_time['GasAverage'].round(), name='Average Gas'), secondary_y=False)
    fig.add_trace(go.Line(x=transactions_over_time['Date'], y=transactions_over_time['GasMedian'].round(), name='Median Gas'), secondary_y=True)
    fig.update_layout(title_text='Average and Median Gas Used Over Time')
    fig.update_yaxes(title_text='Average Gas [gas]', secondary_y=False)
    fig.update_yaxes(title_text='Median Gas [gas]', secondary_y=True)
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

    fig = sp.make_subplots(specs=[[{'secondary_y': True}]])
    fig.add_trace(go.Line(x=transactions_over_time['Date'], y=transactions_over_time['GasPriceAverage'], name='Average Gas Price'), secondary_y=False)
    fig.add_trace(go.Line(x=transactions_over_time['Date'], y=transactions_over_time['GasPriceMedian'], name='Median Gas Price'), secondary_y=True)
    fig.update_layout(title_text='Average and Median Gas Price Over Time')
    fig.update_yaxes(title_text='Average Gas Price [gwei]', secondary_y=False)
    fig.update_yaxes(title_text='Median Gas Price [gwei]', secondary_y=True)
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

    fig = sp.make_subplots(specs=[[{'secondary_y': True}]])
    fig.add_trace(go.Line(x=transactions_over_time['Date'], y=transactions_over_time['Fees/Block'].round(4), name='Fees/Block'), secondary_y=False)
    fig.add_trace(go.Line(x=transactions_over_time['Date'], y=transactions_over_time['Gas/Block'].round(2), name='Gas/Block'), secondary_y=True)
    fig.update_layout(title_text='Average Transaction Fees/Block and Gas Used/Block Over Time')
    fig.update_yaxes(title_text='Fees/Block [USD]', secondary_y=False)
    fig.update_yaxes(title_text='Gas/Block [gas]', secondary_y=True)
    st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

with tab_heatmap:

    st.subheader('Activity Heatmap')
    
    c1, c2 = st.columns(2)
    with c1:
        fig = px.density_heatmap(transactions_heatmap, x='Hour', y='Day', z='Fees', histfunc='avg', title='Heatmap of Transaction Fees', nbinsx=24)
        fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title=None, xaxis={'dtick': 1}, coloraxis_colorbar=dict(title='Fees [USD]'))
        fig.update_yaxes(categoryorder='array', categoryarray=week_days)
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

        fig = px.density_heatmap(transactions_heatmap, x='Hour', y='Day', z='FeeAverage', histfunc='avg', title='Heatmap of Average Fee', nbinsx=24)
        fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title=None, xaxis={'dtick': 1}, coloraxis_colorbar=dict(title='Average [USD]'))
        fig.update_yaxes(categoryorder='array', categoryarray=week_days)
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

        fig = px.density_heatmap(transactions_heatmap, x='Hour', y='Day', z='FeeMedian', histfunc='avg', title='Heatmap of Median Fee', nbinsx=24)
        fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title=None, xaxis={'dtick': 1}, coloraxis_colorbar=dict(title='Median [USD]'))
        fig.update_yaxes(categoryorder='array', categoryarray=week_days)
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

        fig = px.density_heatmap(transactions_heatmap, x='Hour', y='Day', z='Fees/Block', histfunc='avg', title='Heatmap of Average Fees/Block', nbinsx=24)
        fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title=None, xaxis={'dtick': 1}, coloraxis_colorbar=dict(title='Fees/Block [USD]'))
        fig.update_yaxes(categoryorder='array', categoryarray=week_days)
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

    with c2:
        fig = px.density_heatmap(transactions_heatmap, x='Hour', y='Day', z='Gas', histfunc='avg', title='Heatmap of Gas Used', nbinsx=24)
        fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title=None, xaxis={'dtick': 1}, coloraxis_colorbar=dict(title='Gas [Tgas]'))
        fig.update_yaxes(categoryorder='array', categoryarray=week_days)
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

        fig = px.density_heatmap(transactions_heatmap, x='Hour', y='Day', z='GasAverage', histfunc='avg', title='Heatmap of Average Gas Used', nbinsx=24)
        fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title=None, xaxis={'dtick': 1}, coloraxis_colorbar=dict(title='Average [Tgas]'))
        fig.update_yaxes(categoryorder='array', categoryarray=week_days)
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

        fig = px.density_heatmap(transactions_heatmap, x='Hour', y='Day', z='GasMedian', histfunc='avg', title='Heatmap of Median Gas Used', nbinsx=24)
        fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title=None, xaxis={'dtick': 1}, coloraxis_colorbar=dict(title='Median [Tgas]'))
        fig.update_yaxes(categoryorder='array', categoryarray=week_days)
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

        fig = px.density_heatmap(transactions_heatmap, x='Hour', y='Day', z='Gas/Block', histfunc='avg', title='Heatmap of Average Gas/Block', nbinsx=24)
        fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title=None, xaxis={'dtick': 1}, coloraxis_colorbar=dict(title='Gas/Block [Tgas]'))
        fig.update_yaxes(categoryorder='array', categoryarray=week_days)
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)