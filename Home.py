import streamlit as st
from PIL import Image

st.set_page_config(page_title='Home', page_icon='🎲')

#image_path='/Users/Bill/Documents/cds/'
image = Image.open('curry.jpg')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest delivery in town')
st.sidebar.markdown('''---''')

st.write('# Curry Company Grouth Dashboard')
st.markdown('''
             Grouth dashbord foi criado para acompanhar as métricas de crescimento dos entregadores e restaurantes.
             ### Como utilizar:
                . Visão Empresa:
                     - Visão Gerencial: Métricas gerais de comportamento.
                     - Visão Tática: Indicadores semanais de crescimento.
                     - Visão Geográfic: Insigthts de geolocalização.
                . Visão Entregador:
                    - Acompanhamento dos indicadores semanais de crescimento.
                . Visão Restaurante:
                    - Indicadores semanasi de crescimento dos restaurantes.
            ### Asck for help
             - Time de Data Science no discord
             - @fabianobill
             ''')