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
import numpy as np
import emoji

st.set_page_config( page_title='Visão Restaurante', page_icon='🍽', layout='wide')

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
    df1.loc[ :, 'Festival'] = df1.loc[ :, 'Festival'].str.strip()

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

def distance( df1 ):
    cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']

    df1['distance'] = (df1.loc[:, cols].apply( lambda x: 
                                        hs((x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                        (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1))

    avg_distance = np.round(df1['distance'].mean(), 2)

    return avg_distance

def media_desvio( df1, yn, calculo ):
    df_aux = (df1.loc[:, ['Time_taken(min)', 'Festival']]
    .groupby(['Festival'])
    .agg({'Time_taken(min)': ['mean', 'std']}))

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = df_aux.loc[df_aux['Festival'] == yn, calculo]
    df_aux = np.round(df_aux, 2)

    return df_aux

def tempo_medio_entrega_por_cidade( df1 ):
    cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']

    df1['distance'] = (df1.loc[:, cols]
                    .apply( lambda x: hs((x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                         (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1))

    avg_distance = df1.loc[:, ['City', 'distance']].groupby(['City']).mean().reset_index()

    fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])
    fig.update_layout(width=500, height=500)

    return fig

def avg_std_time_graph( df1 ):
    df_aux = (df1.loc[:, ['City', 'Time_taken(min)']]
                .groupby('City')
                .agg({'Time_taken(min)': ['mean', 'std']}))

    df_aux.columns = ['avg_time', 'std_time']

    df_aux = df_aux.reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control',
                        x=df_aux['City'],
                        y=df_aux['avg_time'],
                        error_y=dict(type='data', array=df_aux['std_time'])))

    fig.update_layout(barmode='group', width=300, height=500)

    return fig

# Importando arquivo
# df = pd.read_csv('C:\\Users\\torre\\repos\\exercicios\\ftc_dataframe\\train.csv')
df = pd.read_csv('train.csv')
df1 = clean_code( df )

# ====================
# Side Bar
# ====================

st.header('Marketplace - Visão Restaurante')

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

        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            entregadores_unicos = df1['Delivery_person_ID'].nunique()
            col1.metric('Entregadores', entregadores_unicos)

        with col2:
            avg_distance = distance( df1 )
            col2.metric('Distância Média', avg_distance)

        with col3:
            df_aux = media_desvio( df1, yn='Yes', calculo='avg_time')
            col3.metric('Tempo Médio Entregas c/ Festival', df_aux)

        with col4:
            df_aux = media_desvio( df1, yn='Yes', calculo='std_time')
            col4.metric('Desvio Padão Entregas c/ Festival', df_aux)
            
        with col5:
            df_aux = media_desvio( df1, yn='No', calculo='avg_time')
            col5.metric('Tempo Médio Entregas s/ Festival', df_aux)

        with col6:
            df_aux = media_desvio( df1, yn='No', calculo='std_time')
            col6.metric('Desvio Padão Entregas s/ Festival', df_aux)

    with st.container():
        st.markdown('''---''')
        st.title('Tempo Médio de Entrega por Cidade')
        fig = tempo_medio_entrega_por_cidade( df1 )
        st.plotly_chart(fig)
    
    with st.container():
        st.markdown('''---''')
        st.title('Distribuição do Tempo')

        col1, col2 = st.columns(2)

        with col1:
            fig = avg_std_time_graph( df1 )
            st.plotly_chart(fig)
            
        with col2:
            df_aux = (df1.loc[:, ['City', 'Time_taken(min)', 'Road_traffic_density']]
                        .groupby(['City', 'Road_traffic_density'])
                        .agg({'Time_taken(min)': ['mean', 'std']}))

            df_aux.columns = ['avg_time', 'std_time']

            df_aux = df_aux.reset_index()

            fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                            color='std_time', color_continuous_scale='RdBu',
                            color_continuous_midpoint=np.average(df_aux['std_time']))

            fig.update_layout(width=500, height=500)
            st.plotly_chart(fig)

    with st.container():
        st.markdown('''---''')
        st.title('Tempo Médio e Desvio Padão Por Cidade e Tipo de Tráfego')
        df_aux = df1.loc[:, ['Time_taken(min)', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})

        df_aux.columns = ['Avg_time', 'Std_time']

        df_aux.reset_index()
        st.dataframe(df_aux)

