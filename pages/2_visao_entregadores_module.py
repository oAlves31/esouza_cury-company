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

st.set_page_config( page_title='Visão Entregadores', page_icon='🚚', layout='wide')

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

def top_delivers( df1 , top_asc ):
    st.dataframe(df1.loc[:, ['City','Time_taken(min)', 'Delivery_person_ID']]
                    .groupby(['City', 'Delivery_person_ID'])
                    .max()
                    .sort_values(['City','Time_taken(min)'], ascending=top_asc)
                    .groupby('City')
                    .head(10)
                    .reset_index())

# Importando arquivo
# df = pd.read_csv('C:\\Users\\torre\\repos\\exercicios\\ftc_dataframe\\train.csv')
df = pd.read_csv('train.csv')
df1 = clean_code( df )

# ====================
# Side Bar
# ====================

st.header('Marketplace - Visão Entregadores')

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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overall Metrics')

        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior Idade', maior_idade)

        with col2:
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor Idade', menor_idade)

        with col3:
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor Condição', melhor_condicao)

        with col4:
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior Condição', pior_condicao)

    with st.container():
        st.markdown('''---''')
        st.title('Avaliações')

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliação Média Por Entregador')
            df_aux = (df1.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']]
                      .groupby(['Delivery_person_ID'])
                      .mean()
                      .reset_index())

            st.dataframe(df_aux)

        with col2:
            with st.container():
                # A avaliação média e o desvio padrão por tipo de tráfego
                st.markdown('##### Avaliação Média Por Trânsito')
                df_aux = (df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                             .groupby(['Road_traffic_density'])
                             .agg({'Delivery_person_Ratings': ['mean', 'std']}))

                df_aux.columns = ['Delivery_mean', 'Delivery_std']
                df_aux.reset_index()
                st.dataframe(df_aux)

                # A avaliação média e o desvio padrão por condições climáticas
                st.markdown('##### Avaliação Média Por Condição Climática')
                df_aux = (df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                             .groupby(['Weatherconditions'])
                             .agg({'Delivery_person_Ratings': ['mean', 'std']}))

                df_aux.columns = ['Delivery_mean', 'Delivery_std']
                df_aux.reset_index()
                st.dataframe(df_aux)

    with st.container():
        st.markdown('''---''')
        st.title('Top Entregadores')

        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Top Entregadores Mais Rápidos')
            top_delivers( df1, top_asc=True)

        with col2:
            st.subheader('Top Entregadores Mais Lentos')
            top_delivers( df1, top_asc=False)
            