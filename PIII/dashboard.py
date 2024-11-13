import streamlit as st
import requests
import pandas as pd

st.title("Dashboard de Alocação Acadêmica")

# URL da API
api_url = 'http://127.0.0.1:5000/dados'  

# Requisição para obter dados da API
response = requests.get(api_url)

# Verifica se a resposta foi bem-sucedida
if response.status_code == 200:
    data = response.json()  # Converte os dados recebidos para JSON

    # Assume-se que a API retorna um dicionário de tabelas, onde cada tabela é uma chave com seus dados
    tabelas = data.keys()
    tabela_selecionada = st.sidebar.selectbox("Selecione a tabela para visualizar os dados", tabelas)

    # Converte a tabela selecionada em um DataFrame do Pandas
    df = pd.DataFrame(data[tabela_selecionada])

    # Exibe os dados no Streamlit
    st.write(f"Tabela: {tabela_selecionada}", df)

    # Visualização de dados específicos com base na tabela
    if tabela_selecionada == "Curso":
        st.subheader("Detalhes do Curso")
        cursos = df['name'].unique()
        curso_selecionado = st.selectbox("Selecione um curso", cursos)
        st.write(df[df['name'] == curso_selecionado])

    elif tabela_selecionada == "Professores":
        st.subheader("Currículo dos Professores")
        professores = df['nome'].unique()
        professor_selecionado = st.selectbox("Selecione um professor", professores)
        st.write(df[df['nome'] == professor_selecionado][['nome', 'curriculo']])

    elif tabela_selecionada == "Materia":
        st.subheader("Detalhes das Matérias")
        materias = df['nome'].unique()
        materia_selecionada = st.selectbox("Selecione uma matéria", materias)
        st.write(df[df['nome'] == materia_selecionada])

    elif tabela_selecionada == "Disponibilidade":
        st.subheader("Disponibilidade dos Professores")
        dias = df['dia_da_semana'].unique()
        dia_selecionado = st.selectbox("Selecione um dia da semana", dias)
        st.write(df[df['dia_da_semana'] == dia_selecionado])

    elif tabela_selecionada == "Alocacao":
        st.subheader("Alocações")
        data_selecionada = st.date_input("Selecione uma data", value=pd.to_datetime('today'))
        st.write(df[df['data'] == data_selecionada])

    # Gráfico simples usando os dados da tabela selecionada
    st.line_chart(df.select_dtypes(include=['number']))
else:
    st.write('Falha ao conectar-se à API.', response.status_code)