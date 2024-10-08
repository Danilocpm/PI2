import streamlit as st
import requests
import pandas as pd

st.title('Dashboard')

api_url = 'http://127.0.0.1:5000/dashboard'  

response = requests.get(api_url)

if response.status_code == 200:
    data = response.json()  # Converte os dados recebidos para JSON
    df = pd.DataFrame(data)  # Converte os dados em um DataFrame do Pandas

    # Exibe os dados no Streamlit
    st.write('Dados da API:', df)

    # Cria um gráfico simples usando os dados
    st.line_chart(df)
else:
    st.write('Falha ao conectar-se à API.', response)
