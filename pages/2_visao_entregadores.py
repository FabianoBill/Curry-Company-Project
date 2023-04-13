
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

st.set_page_config(page_title='Visão Entregadores', page_icon='📫', layout='wide')

#===============================================================================================
#-----------------------------------------------Funções-----------------------------------------
#===============================================================================================

def top_10(df1, top_ascending):
    df2 = (df1.loc[:,['Delivery_person_ID','City','Time_taken(min)']]
            .groupby(['City','Delivery_person_ID'])
            .min()
            .sort_values(['City','Time_taken(min)'], ascending=top_ascending)
            .reset_index())
    
    dfa = df2.loc[df2['City']=='Metropolitian',:].head(10)
    dfb = df2.loc[df2['City']=='Semi-Urban',:].head(10)
    dfc = df2.loc[df2['City']=='Urban',:].head(10)
    df_top = pd.concat([dfa,dfb,dfc]).reset_index()
    
    return df_top

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
df1 = limpa_df(df)

#--------------------------------------------------------------------------
#                                             Barra lateral
#--------------------------------------------------------------------------
st.header('Market place_Visão Entregadores')

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

        col1, col2, col3, col4  = st.columns(4)
        with col1:
            st.subheader('Maior idade')
            st.subheader(df1['Delivery_person_Age'].max())
        with col2:
            st.subheader('Menor idade')  
            st.subheader(df1['Delivery_person_Age'].min())
        with col3:
            st.subheader('Melhor condição de veículos')
            st.subheader(df1['Vehicle_condition'].max())
        with col4:
            st.subheader('Pior condição de veículos')
            st.subheader(df1['Vehicle_condition'].min())
            
            
    with st.container():
        st.markdown('''___''')
        st.title('Avaliações') 
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Média por entregador')
            df_avg_entregador = (df1.loc[:,['Delivery_person_ID', 'Delivery_person_Ratings']]
                                        .groupby('Delivery_person_ID')
                                        .mean()
                                        .reset_index())
                    
            st.dataframe(df_avg_entregador)
            
        with col2:
                with st.container():
                    st.subheader('Média e desvio padrão por tipo de tráfego')
                    df_avg_std_trafego = (df1.loc[:,['Road_traffic_density', 'Delivery_person_Ratings']]
                                              .groupby('Road_traffic_density')
                                              .agg({'Delivery_person_Ratings':['mean','std']}))
                    st.dataframe(df_avg_std_trafego)

                    
                with st.container():
                    st.subheader('Média e desvio padrão por condições climáticas')
                    df_avg_std_clima = (df1.loc[:,['Weatherconditions', 'Delivery_person_Ratings']]
                                            .groupby('Weatherconditions')
                                            .agg({'Delivery_person_Ratings':['mean','std']}))

                    st.dataframe(df_avg_std_clima)


    with st.container():
        st.markdown('''___''')
        st.title('Entregadores')
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader('10 entregadores mais rápidos por cidade.')
            df2 = top_10(df1, top_ascending=True)
            st.dataframe(df2)

        with col2:
            st.subheader('10 entregadores mais lentos por cidade.')
            df2 = top_10(df1, top_ascending=False)
            st.dataframe(df2)
                    
                    
                    
                    
                    
                    
                    
                    
