import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import seaborn as sns

st.title("Dashboard de Alocação Acadêmica")

# URL da API
api_url = 'http://127.0.0.1:5000/dashboard'

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
        
    elif tabela_selecionada == "sala":
        st.subheader("Análises para a Tabela 'Sala'")
        
        st.subheader("Detalhes da Sala")
        sala = df['id'].unique()
        sala_selecionada = st.selectbox("Selecione uma sala", sala)
        st.write(df[df['id'] == sala_selecionada])

        # Gráfico de barras: Número de salas por campus
        st.subheader("Número de Salas por Campus")
        salas_por_campus = df['campus_id'].value_counts()
        fig, ax = plt.subplots()
        sns.barplot(x=salas_por_campus.index, y=salas_por_campus.values, ax=ax)
        ax.set_xlabel("Campus")
        ax.set_ylabel("Número de Salas")
        st.pyplot(fig)

        # Gráfico de barras: Distribuição de turnos
        st.subheader("Distribuição de Salas por Turno")
        salas_por_turno = df['turno_id'].value_counts()
        fig, ax = plt.subplots()
        sns.barplot(x=salas_por_turno.index, y=salas_por_turno.values, ax=ax)
        ax.set_xlabel("Turno")
        ax.set_ylabel("Número de Salas")
        st.pyplot(fig)

        # Gráfico de dispersão: Capacidade das salas por campus
        st.subheader("Capacidade das Salas por Campus")
        fig, ax = plt.subplots()
        sns.scatterplot(data=df, x="campus_id", y="capacidade", ax=ax, hue="turno_id", palette="viridis")
        ax.set_xlabel("Campus")
        ax.set_ylabel("Capacidade")
        st.pyplot(fig)

        # Gráfico de pizza: Distribuição de matérias por campus
        st.subheader("Distribuição de Matérias por Campus")
        materias_por_campus = df['campus_id'].value_counts()
        fig, ax = plt.subplots()
        ax.pie(materias_por_campus, labels=materias_por_campus.index, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        st.pyplot(fig)


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

        # Gráfico de barras para o número de matérias por área
        st.subheader("Número de Matérias por Área")

        # Contar o número de matérias em cada área
        materias_por_area = df['area'].value_counts()
        # Exibir gráfico de barras
        st.bar_chart(materias_por_area)        
        # Gráfico de barras para o número de matérias por área
        st.subheader("Número de Matérias por Semestre")
        # Contar o número de matérias em cada semestre
        materias_por_semestre= df['semestre'].value_counts()

        # Exibir gráfico de barras
        st.bar_chart(materias_por_semestre)   

    elif tabela_selecionada == "Alocacao":
        st.subheader("Alocações")
        
        st.write("Colunas disponíveis na tabela 'Alocacao':", df.columns)
        st.write("Exemplo de dados:", df.head())


        # Gráfico 1: Número de alocações por professor
        st.subheader("Número de Alocações por Professor")
        alocacoes_por_professor = df['professor_id'].value_counts()
        fig1, ax1 = plt.subplots()
        sns.barplot(x=alocacoes_por_professor.index, y=alocacoes_por_professor.values, ax=ax1, palette="viridis")
        ax1.set_xlabel("ID do Professor")
        ax1.set_ylabel("Número de Alocações")
        ax1.set_title("Distribuição de Alocações por Professor")
        st.pyplot(fig1)

        # Gráfico 2: Número de alocações por matéria
        st.subheader("Número de Alocações por Matéria")
        alocacoes_por_materia = df['materia_id'].value_counts()
        fig2, ax2 = plt.subplots()
        sns.barplot(x=alocacoes_por_materia.index, y=alocacoes_por_materia.values, ax=ax2, palette="coolwarm")
        ax2.set_xlabel("ID da Matéria")
        ax2.set_ylabel("Número de Alocações")
        ax2.set_title("Distribuição de Alocações por Matéria")
        st.pyplot(fig2)

        # Gráfico 3: Distribuição de alocações por turno
        st.subheader("Distribuição de Alocações por Turno")
        alocacoes_por_turno = df['turno_id'].value_counts()
        fig3, ax3 = plt.subplots()
        sns.barplot(x=alocacoes_por_turno.index, y=alocacoes_por_turno.values, ax=ax3, palette="Blues")
        ax3.set_xlabel("ID do Turno")
        ax3.set_ylabel("Número de Alocações")
        ax3.set_title("Distribuição de Alocações por Turno")
        st.pyplot(fig3)

        # Gráfico 4: Distribuição de alocações por sala
        st.subheader("Distribuição de Alocações por Sala")
        alocacoes_por_sala = df['sala_id'].value_counts()
        fig4, ax4 = plt.subplots()
        sns.barplot(x=alocacoes_por_sala.index, y=alocacoes_por_sala.values, ax=ax4, palette="mako")
        ax4.set_xlabel("ID da Sala")
        ax4.set_ylabel("Número de Alocações")
        ax4.set_title("Distribuição de Alocações por Sala")
        st.pyplot(fig4)

        # Gráfico 5: Distribuição de alocações por turma
        st.subheader("Distribuição de Alocações por Turma")
        alocacoes_por_turma = df['turma_id'].value_counts()
        fig5, ax5 = plt.subplots()
        sns.barplot(x=alocacoes_por_turma.index, y=alocacoes_por_turma.values, ax=ax5, palette="cubehelix")
        ax5.set_xlabel("ID da Turma")
        ax5.set_ylabel("Número de Alocações")
        ax5.set_title("Distribuição de Alocações por Turma")
        st.pyplot(fig5)


else:
    st.write('Falha ao conectar-se à API.', response.status_code)