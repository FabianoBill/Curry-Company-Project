
# Libs
import pandas as pd
#pip install plotly
import plotly.express as px
#pip install haversine
from haversine import haversine
import streamlit as st
from PIL import Image
import folium
from pandas.core.reshape.concat import Mapping
#pip install streamlit-folium
#from streamlit_folium import folium_static
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title='Visão Restaurantes', page_icon='🍽', layout='wide')

#===============================================================================================
#-----------------------------------------------Funções-----------------------------------------
#===============================================================================================
            
def tempo_festival(df1, festival, avg_std):
    ''' 
        festival='Yes' or 'No'
        avg_std= 'avg_time' or 'std_time'
    '''
    df2 = (df1.loc[:, ['Festival', 'Time_taken(min)']]
           .groupby(['Festival'])
           .agg({'Time_taken(min)':['mean', 'std']}))
    df2.columns = ['avg_time', 'std_time']
    df2 = df2.reset_index()
    df2 =  np.round(df2.loc[df2['Festival']==festival, avg_std], 2)
    
    return df2

def tempo_cidade_entrega(df1):        
        df2 = (df1.loc[:, ['City', 'Type_of_order', 'Time_taken(min)']].groupby(['City','Type_of_order']).agg({'Time_taken(min)':['mean','std']}))
        df2.columns = ['avg_time', 'std_time']
        df2.reset_index()
        
        return df2 
    
def tempo_entrega(df1):           
            df2 = df1.loc[:, ['City', 'Road_traffic_density', 'Time_taken(min)']].groupby(['City','Road_traffic_density']).agg({'Time_taken(min)':['mean','std']})
            df2.columns = ['avg_time', 'std_time']
            df2 = df2.reset_index()
            fig = px.sunburst(df2, path = ['City', 'Road_traffic_density'], values = 'avg_time', color = 'std_time', color_continuous_scale = 'RdBu', color_continuous_midpoint = np.average(df2['std_time']))
            
            return fig

def distribuicao_tempo_cidade(df1):
            df2 = df1.loc[:, ['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)':['mean','std']})
            df2.columns = ['avg_time','std_time']
            df2 = df2.reset_index()
            fig = go.Figure()
            fig.add_trace(go.Bar(name = 'Control', x = df2['City'], y = df2['avg_time'], error_y = dict(type = 'data', array = df2['std_time'])))
            
            return fig

def distribuicao_avg_cidade(df1):        
        df1['distance'] = df1.loc[:,['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude', 'Delivery_location_longitude']].apply(lambda x: haversine((x['Restaurant_latitude'],x['Restaurant_longitude']),(x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
        avg_distance = df1.loc[: , ['City', 'distance']].groupby('City').mean().reset_index()
        fig = go.Figure(data = [go.Pie(labels = avg_distance['City'], values = avg_distance['distance'], pull = [0,0.1, 0])])
        return fig

def distancia_media(df1):
    df1['distance'] = df1.loc[:,['Restaurant_latitude',	'Restaurant_longitude','Delivery_location_latitude', 'Delivery_location_longitude']].apply(lambda x: haversine((x['Restaurant_latitude'],x['Restaurant_longitude']),(x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1 )
    df2 = np.round(df1['distance'].mean(), 2)
    return df2

def limpa_df(df1):
    ''' Limpa o dataframe.
    
        Tipos de limpesa:
        1. Remove espaços de inicio e fim das variáveis.
        2. Remove todas as linhas com dados NaN.
        3. Converte o tipo de algumas variáveis.
        4. Remove o texto '(min) ' da coluna de tempo.
        
        Input: Dataframe
        Output: Dataframe
    '''
        # strip em todas as colunas de strings
    for i in range(len(df1.columns)):
      if type(df1.iloc[0,i])==str:
        df1.iloc[:,i]=df1.iloc[:,i].str.strip()
    # Limpeza das células NaN
    for i in df1.columns:
      df1=df1.loc[df1[i]!='NaN',:]
    # 1. Convertendo coluna Age de texto para inteiro
    df1['Delivery_person_Age']=df1['Delivery_person_Age'].astype(int)
    # 2. Convertendo coluna Ratings para numeros decimais
    df1['Delivery_person_Ratings']=df1['Delivery_person_Ratings'].astype(float)
    # 3. Convertendo coluna 'Order_Date' de srt para data
    df1['Order_Date']=pd.to_datetime(df1['Order_Date'], infer_datetime_format=True)
    # 4. Convertendo  coluna multiple_deliveries para int
    df1['multiple_deliveries']=df1['multiple_deliveries'].astype(int)
    # 5. Limpando e convertendo coluna Time_taken(min)
    df1['Time_taken(min)']=df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df1['Time_taken(min)']=df1['Time_taken(min)'].astype(int)
                      
    return df1


#-------------------------------------------------------------------------------------------------
#-------------------------------------------- Estrutura do código --------------------------------
#-------------------------------------------------------------------------------------------------

# Import dataset
df = pd.read_csv('dataset/train.csv')
#Limpesa
df1 = limpa_df(df)

#--------------------------------------------------------------------------
#                                             Barra lateral
#--------------------------------------------------------------------------
st.header('Market place_Visão Restaurantes')

image = Image.open('curry.jpg')
st.sidebar.image(image, width = 120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest delivery in town')
st.sidebar.markdown('''---''')

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider('Até qual valor', value = pd.datetime(2022,4,13), min_value = pd.datetime(2022,2,11), max_value = pd.datetime(2022,4,6), format = 'DD-MM-YY')
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]
st.sidebar.markdown('''---''')

st.sidebar.markdown('## Condições de trânsito')
trafic_options = st.sidebar.multiselect('Quais as condições de trânsito?', ['Low','High','Medium','Jam'], default = ['Low','High','Medium','Jam'])
linhas_selecionadas = df1['Road_traffic_density'].isin(trafic_options)
df1 = df1.loc[linhas_selecionadas, :]

st.sidebar.markdown('''---''')
st.sidebar.markdown('Powered by Bill DS')

#--------------------------------------------------------------------------
#                                             Layout streamlit
#--------------------------------------------------------------------------

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','_','_'])


with tab1:
    with st.container():
        st.title('Metricas gerais')

        col1, col2, col3, col4, col5, col6  = st.columns(6)
        with col1:
            entregadores = df1['Delivery_person_ID'].nunique()
            col1.metric('Entregadores', entregadores)
            
        with col2:
            df2 = distancia_media(df1)
            col2.metric('Distância média', df2) 
            
        with col3:
            df2 = tempo_festival(df1, festival='Yes', avg_std='avg_time')
            col3.metric('Tempo c/ festival', df2)
            
        with col4:
            df2 = tempo_festival(df1, festival='Yes', avg_std='std_time')
            col4.metric('Desvio c/ festival', df2)
            
        with col5:
            df2 = tempo_festival(df1, festival='No', avg_std='avg_time')
            col5.metric('Tempo s/ festival', df2)
            
        with col6:
            df2 = tempo_festival(df1, festival='No', avg_std='std_time')
            col6.metric('Desvio s/ festival', df2)

    with st.container():
        st.markdown('''___''')
        st.markdown('Distribuição média por cidade') 
        fig = distribuicao_avg_cidade(df1)
        st.plotly_chart(fig)
   
    with st.container():
        st.markdown('''___''')
       
        col1, col2  = st.columns(2)
        with col1:
            st.markdown('Distribuição do tempo por cidades')
            fig = distribuicao_tempo_cidade(df1)
            st.plotly_chart(fig)
            
        with col2:
            st.markdown('Tempo médio por tipo de entrega')
            fig = tempo_entrega(df1) 
            st.plotly_chart(fig)
 
    with st.container():
        st.markdown('''___''')
        st.markdown('Tempo médio por cidades e por tipo de entrega')
        df2 = tempo_cidade_entrega(df1)
        st.dataframe(df2)