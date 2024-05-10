from haversine import haversine as hs
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
import streamlit as st
from streamlit_folium import folium_static
import datetime as dt
from PIL import Image
import folium
import emoji

st.set_page_config( page_title='Visão Empresa', page_icon='📈', layout='wide')

#========================================================
# FUNÇÕES
#========================================================
def clean_code(df1):
    ''' Esta função tem a responsabilidade de limpar o dataframe 

        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo (remoção do texto da variável numérica)

        Input: Dataframe
        Output: Dataframe
    '''

    df1.loc[ :, 'ID'] = df1.loc[ :, 'ID'].str.strip()
    df1.loc[ :, 'Delivery_person_ID'] = df1.loc[ :, 'Delivery_person_ID'].str.strip()
    df1.loc[ :, 'Road_traffic_density'] = df1.loc[ :, 'Road_traffic_density'].str.strip()
    df1.loc[ :, 'Type_of_order'] = df1.loc[ :, 'Type_of_order'].str.strip()
    df1.loc[ :, 'Type_of_vehicle'] = df1.loc[ :, 'Type_of_vehicle'].str.strip()
    df1.loc[ :, 'City'] = df1.loc[ :, 'City'].str.strip()

    linha_vazias = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linha_vazias, : ]

    df1 = df1.loc[df1['City'] != 'NaN', :]
    df1 = df1.loc[df1['Road_traffic_density'] != 'NaN', :]
    df1 = df1.loc[df1['Time_taken(min)'] != 'NaN', :]
    df1 = df1.loc[df1['Festival'] != 'NaN ', :]

    df1['Time_taken(min)'] = df1['Time_taken(min)'].str.split(' ').str[1]
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    linha_vazias = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linha_vazias, : ]
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    df1 = df1.reset_index(drop=True)
    for i in range(len(df1)):
        df.loc[i, 'Time_taken(min)'] = re.findall(r'\d+', df.loc[i, 'Time_taken(min)'])

    return df1

def order_metric( df1 ):
    ''' Conta os pedidos por dia '''
    colunas = ['ID', 'Order_Date']
    df_aux = (df1.loc[:, colunas]
                 .groupby(['Order_Date'])
                 .count()
                 .reset_index())
    
    fig = px.bar(df_aux, x='Order_Date', y='ID')
    return fig 

def traffic_order_share( df1 ):
    ''' Distribuição dos pedidos por tipo de tráfego '''
    df_aux = (df1.loc[:, ['ID', 'Road_traffic_density']]
                 .groupby('Road_traffic_density')
                 .count()
                 .reset_index())
    
    df_aux['entregas_percentual'] = df_aux['ID'] / df_aux['ID'].sum()
    fig = px.pie(df_aux, values='entregas_percentual', names='Road_traffic_density')
    return fig

def traffic_order_city( df1 ):
    ''' Comparação do volume por cidade e por tipo de tráfego '''
    df_aux = (df1.loc[:, ['ID', 'City', 'Road_traffic_density']]
                    .groupby(['City', 'Road_traffic_density'])
                    .count()
                    .reset_index())
    
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
    return fig

def order_by_week( df1 ):
    # Quantidade de pedidos por semana
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    fig = px.line(df_aux, x='week_of_year', y='ID')
    return fig

def order_share_by_week( df1 ):
    df_aux01 = df1.loc[:, ['ID', 'week_of_year']].groupby(['week_of_year']).count().reset_index()
    df_aux02 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby(['week_of_year']).nunique().reset_index()
    df_aux = pd.merge( df_aux01, df_aux02, how='inner')
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x='week_of_year', y='order_by_deliver')
    return fig

def country_maps( df1 ):
    df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()

    map_ = folium.Map()

    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude']],
                        popup=location_info[['City', 'Road_traffic_density']]).add_to(map_)
        
    folium_static(map_, width=1024, height=600)

    return None

# ======================= Início da estrutura lógica ===========================

# ===================
# Importando dataset
# ===================
# df = pd.read_csv('C:\\Users\\torre\\repos\\exercicios\\ftc_dataframe\\train.csv')
df = pd.read_csv('train.csv')
df1 = df.copy()

df1 = clean_code(df1)

# ====================
# Side Bar
# ====================

st.header('Marketplace - Visão Cliente')

# image_path = 'C:\\Users\\torre\\repos\\logo.png'
image = Image.open('logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('''---''')

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=dt.datetime(2022, 4, 13),
    min_value=dt.datetime(2022, 2, 11),
    max_value=dt.datetime(2022, 4, 6),
    format='DD-MM-YYYY'
)

st.sidebar.markdown('''---''')

traffic_options = st.sidebar.multiselect(
    'Quais as condições de trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam']
)

st.sidebar.markdown('''---''')
st.sidebar.markdown('### Powered by Eric Souza')

# Filtro de Data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

#Filtro de Trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

# ====================
# Layout
# ====================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])


with tab1:
    with st.container():
        st.markdown('# Orders By Day')
        fig = order_metric( df1 )
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            st.header('Traffic Order Share')
            fig = traffic_order_share( df1 )
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.header('Traffic Order City')
            fig = traffic_order_city( df1 )
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    with st.container():
        st.header('Order By Week')
        fig = order_by_week( df1 )
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.header('Order Share by Week')
        fig = order_share_by_week( df1 )
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header('Country Maps')
    country_maps( df1 )
