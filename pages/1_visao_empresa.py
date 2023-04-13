## 1. Quantidade de pedidos por dia.
#Saída: Um gráfico de barra com a quantidade de entregas no eixo Y e os dias no eixo X. Processo: Fazer um contagem da colunas “ID” agrupado “Order Date” e usar uma bibliotecas de visualização para mostrar o gráfico de barras. Entrada: Eu posso usar o comando groupby() para agrupar os dados e o comando count() para contar a coluna de IDs e um comando para desenhar um gráfico de barras.

# Libs
import pandas as pd
#pip install plotly
import plotly.express as px
#$ pip install haversine
from haversine import haversine
import streamlit as st
from PIL import Image
import folium
from pandas.core.reshape.concat import Mapping
# pip install streamlit-folium
from streamlit_folium import folium_static
#$ pip install streamlit --upgrade

st.set_page_config(page_title='Visão Empresa', page_icon='📈', layout='wide')

#===============================================================================================
#-----------------------------------------------Funções-----------------------------------------
#===============================================================================================
def mapa_cidade(df1):
    cols = ['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']
    df2 = (df1.loc[:, cols]
               .groupby(['City','Road_traffic_density'])
               .median()
               .reset_index())
    df2 = df2.head()
    map = folium.Map( )
    for index, location_info in df2.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude']],
                        popup=location_info[['City', 'Road_traffic_density']] ).add_to( map )

        folium_static(map, width=1024, height=600)
        
    return None

def distribuicao_entregador_semana(df1):
    
        df1['week_of_year']=df1['Order_Date'].dt.strftime('%U')
        df2 = df1.loc[:,['ID','week_of_year']].groupby('week_of_year').count().reset_index()
        df3 = (df1.loc[:,['week_of_year','Delivery_person_ID']]
                   .groupby('week_of_year')
                   .nunique()
                   .reset_index())
        df4 = pd.merge(df2,df3,how='inner')
        df4['order_by_deliver']=df4['ID']/df4['Delivery_person_ID']
        fig = px.line(df4,x='week_of_year',y='order_by_deliver')
        
        return fig

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

# Importação dataset
df = pd.read_csv('dataset/train.csv')

# Limpando dados
df1 = limpa_df(df)

#-----------------------
# Barra lateral streamlit
#-----------------------
st.header('Market place_Visão Empresa')

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
# -----------------------Layout streamlit
#--------------------------------------------------------------------------

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','Visão Tática','Visão Geográfica'])

with tab1:
    with st.container():
        st.markdown('# Entregas por dia')
        df2=df1.loc[:,['ID','Order_Date']].groupby('Order_Date').count().reset_index()
        st.plotly_chart(px.bar(df2,x='Order_Date',y='ID'), use_container_width=True)


    with st.container():
        col1, col2  = st.columns(2)
        with col1:
            st.markdown('Distribuição por trafego')
            df2 = (df1.loc[:,['ID','Road_traffic_density']]
                       .groupby('Road_traffic_density')
                       .count()
                       .reset_index())
            df2 = df2.loc[df2['Road_traffic_density']!='NaN',:]
            df2['entregas_perc']=df2['ID']/df2['ID'].sum()
            st.plotly_chart(px.pie(df2,values='entregas_perc'), use_container_width=True) 
        
        with col2:
            st.markdown('Distribuição por cidade e por trafego')
            df2 = (df1.loc[:,['ID','City','Road_traffic_density']]
                       .groupby(['City','Road_traffic_density'])
                       .count()
                       .reset_index())
            df2 = df2.loc[df2['City']!='NaN',:]
            df2 = df2.loc[df2['Road_traffic_density']!='NaN',:]
            st.plotly_chart(px.scatter(df2,x='City',y='Road_traffic_density',size="ID",color='City'), use_container_width=True)
            
with tab2:
    with st.container():
        st.markdown('Entregas por semana')
        df1['week_of_year']=df1['Order_Date'].dt.strftime('%U')
        df2 = df1.loc[:,['ID','week_of_year']].groupby('week_of_year').count().reset_index()
        st.plotly_chart(px.line(df2,x='week_of_year',y='ID'), use_container_width=True)

    with st.container(): 
        st.markdown('Entregas por entregador por semana')
        fig = distribuicao_entregador_semana(df1)
        st.plotly_chart(fig, use_container_width=True)
    
with tab3:
    st.markdown('Mapa da entregas na cidade')
    mapa_cidade(df1)

    