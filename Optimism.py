# Libraries
import streamlit as st
import PIL

# Page Favicon
favicon = PIL.Image.open('favicon.png')

# Layout
st.set_page_config(page_title='Optimism Mega Dashboard', page_icon=favicon, layout='wide')
st.title('Optimism Mega Dashboard')

# Style
with open('style.css')as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)

# Content
st.subheader('Introduction')

st.write(
    """
    [**Optimism**](https://www.optimism.io) is a low-cost and lightning-fast Ethereum L2
    blockchain. Built as a minimal extension to existing Ethereum software, EVM-equivalent
    architecture of Optimism scales your Ethereum apps without surprises. If it works on
    Ethereum, it works on Optimism at a fraction of the cost.
    """
)

st.subheader('Methodology')

st.write(
    """
    The data for this mega dashboard were selected from the [**Flipside Crypto**](https://flipsidecrypto.xyz)
    data platform by using its **REST API**. These queries are currently set to **re-run every 24 hours** to
    cover the latest data and are imported as a JSON file directly to each page. The code for this tool is
    saved and accessible in its [**GitHub Repository**](https://github.com/alitaslimi/optimism-dashboard).

    This mega dashboard is designed and structured in multiple **Pages** that are accessible using the sidebar.
    Each of these Pages addresses a different segment of the Optimism ecosystem. By browsing each page
    (Macro, Transfers, Swaps, NFTs, etc.) you are able to dive deeper into each secotr of the Optimism's
    network.

    Links to the data **queries** are available in the GitHub repository of this tool. 
    """
)

st.write("#")

# Credits
c1, c2, c3 = st.columns(3)
with c1:
    st.info('**Data Analyst: [@AliTslm](https://twitter.com/AliTslm)**', icon="💡")
with c2:
    st.info('**GitHub: [@alitaslimi](https://github.com/alitaslimi)**', icon="💻")
with c3:
    st.info('**Data: [Flipside Crypto](https://flipsidecrypto.xyz)**', icon="🧠")