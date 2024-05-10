import streamlit as st
from PIL import Image

st.set_page_config(page_title='Home')

# image_path = 'C:\\Users\\torre\\repos\\logo.png'
image = Image.open('logo.png')

st.sidebar.image( image, width=120 )

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('''---''')

st.write('# Cury Company Growth Dashboard')

st.markdown(
    '''
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar este Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento;
        - Visão Tática: Indicadores semanais de crescimento;
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregadores:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Restaurante:
        - Indicadores semanais de crescimento do restaurante.
    ### Ask for help
        email: torre.eric@gmail.com
'''
)