import pymysql
import json

timeout = 60

def load_config():
    with open('configdb.json') as f:
        return json.load(f)

def get_connection():
    config = load_config()
    connection = pymysql.connect(
        charset="utf8mb4",
        connect_timeout=timeout,
        cursorclass=pymysql.cursors.DictCursor,
        db=config["db"],
        host=config["host"],
        password=config["password"],
        read_timeout=timeout,
        port=config["port"],
        user=config["user"],
        write_timeout=timeout,
    )
    return connection

def insert_data_to_mysql(rows):
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            insert_professor_query = "INSERT INTO Professores (nome, curriculo, email) VALUES (%s, %s, %s)"
            select_materia_id_query = "SELECT id FROM Materia WHERE nome = %s"
            insert_professor_materia_query = "INSERT INTO Professor_Materia (professor_id, materia_id) VALUES (%s, %s)"
            
            for row in rows:
                print(f"Processando linha: {row}")
                print(f"Chaves disponíveis no row: {row.keys()}")

                nome = row.get('nome', 'N/A')
                curriculo = row.get('curriculo', 'N/A')
                email = row.get('email', 'N/A')
                
                # Inserir o professor
                cursor.execute(insert_professor_query, (nome, curriculo, email))
                professor_id = cursor.lastrowid

                if not professor_id:
                    print("Nenhum professor foi inserido.")
                    continue
                
                print(f"Professor inserido com ID: {professor_id}")

                # Processar matérias de `materia3`, `materia4`, `materia5`
                materias = []
                for materia_key in ['materia3', 'materia4', 'materia5']:
                    if row.get(materia_key):
                        materias.extend(row[materia_key].split(","))

                materias = [m.strip() for m in materias]  # Remover espaços adicionais
                print(f"Matérias processadas: {materias}")

                # Buscar IDs das matérias e inserir na tabela Professor_Materia
                materia_ids = set()  # Usar um conjunto para evitar duplicatas
                for materia in materias:
                    cursor.execute(select_materia_id_query, (materia,))
                    result = cursor.fetchone()
                    print(f"Resultado da busca por matéria: {result}")
                    
                    # Verifica se o resultado é um dicionário e acessa o ID corretamente
                    if result and 'id' in result:
                        materia_id = result['id']  # ID da matéria encontrada
                        print(f"ID da matéria encontrada: {materia_id} para {materia}")

                        # Adicionar o materia_id ao conjunto para inserção
                        materia_ids.add(materia_id)
                    else:
                        print(f"Materia não encontrada: {materia}")

                # Inserir Professor_Materia para cada materia_id único
                for materia_id in materia_ids:
                    try:
                        cursor.execute(insert_professor_materia_query, (professor_id, materia_id))
                        print(f"Inserido Professor_Materia: professor_id={professor_id}, materia_id={materia_id}")
                    except Exception as e:
                        print(f"Erro ao inserir Professor_Materia: {e}")
                        print(f"Dados que causaram o erro: professor_id={professor_id}, materia_id={materia_id}")

            connection.commit()  # Commit após todas as inserções
            print("Todas as inserções foram confirmadas.")
    
    except Exception as e:
        print(f"Erro ao inserir dados no banco de dados: {e}")
        print(f"Tipo de erro: {type(e).__name__}")
        if hasattr(e, 'args'):
            print(f"Código do erro: {e.args}")
    
    finally:
        if connection:
            connection.close()  # Garantir que a conexão seja fechada


def insert_disponibilidade_to_mysql(data):
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            # Extract professor information
            nome = data.get('nome', 'N/A')
            email = data.get('email', 'N/A')

            # Search for the professor in the Professores table
            select_professor_query = "SELECT id FROM Professores WHERE nome = %s AND email = %s"
            cursor.execute(select_professor_query, (nome, email))
            professor_result = cursor.fetchone()
            if professor_result:
                professor_id = professor_result['id']
            else:
                # Insert new professor if not found
                insert_professor_query = "INSERT INTO Professores (nome, email) VALUES (%s, %s)"
                cursor.execute(insert_professor_query, (nome, email))
                professor_id = cursor.lastrowid

            # Process campus information
            campus = data.get('campus', 'N/A')
            campus_list = [c.strip() for c in campus.split(',')] if campus != 'N/A' else []

            # Define day mappings
            day_mapping = {
                'Segunda': 'seg',
                'Terça': 'ter',
                'Quarta': 'quarta',
                'Quinta': 'quinta',
                'Sexta': 'sex',
            }

            # For each campus, process availability data
            for c in campus_list:
                disponibilidade_data = {
                    'professor_id': professor_id,
                    'turno_id': None,  # Assuming turno_id is optional or can be NULL
                    'campus_id': None,  # To be set after fetching from Campus table
                    'consideracoes': '',
                    'seg': 0,
                    'ter': 0,
                    'quarta': 0,
                    'quinta': 0,
                    'sex': 0,
                    'segtarde': 0,
                    'tertarde': 0,
                    'quartarde': 0,
                    'quintatarde': 0,
                    'sextarde': 0,
                    'segnoite': 0,
                    'ternoite': 0,
                    'quartanoite': 0,
                    'quintanoite': 0,
                    'sexnoite': 0,
                }

                # Fetch campus_id from Campus table
                select_campus_query = "SELECT id FROM Campus WHERE nome = %s"
                cursor.execute(select_campus_query, (c,))
                campus_result = cursor.fetchone()
                if campus_result:
                    campus_id = campus_result['id']
                    disponibilidade_data['campus_id'] = campus_id
                else:
                    # Handle error: Campus not found
                    print(f"Campus não encontrado: {c}")
                    continue  # Skip to next campus

                # For "Asa Norte", use the fields without suffix
                if c == 'Asa Norte':
                    dias_manha = data.get('diasdemanha', '')
                    dias_tarde = data.get('diasdetarde', '')
                    dias_noite = data.get('diasdenoite', '')
                    observacao = data.get('observacao1', '')
                # For "Taguatinga", use the fields with suffix 2/3
                elif c == 'Taguatinga':
                    dias_manha = data.get('diasdemanha2', '')
                    dias_tarde = data.get('diasdetarde2', '')
                    dias_noite = data.get('diasdenoite3', '')
                    observacao = data.get('observacao2', '')
                else:
                    # Unknown campus
                    print(f"Campus desconhecido: {c}")
                    continue

                disponibilidade_data['consideracoes'] = observacao

                # Process morning availability
                if dias_manha and dias_manha != 'N/A':
                    dias_manha_list = [d.strip() for d in dias_manha.split(',')]
                    for dia in dias_manha_list:
                        field_name = day_mapping.get(dia)
                        if field_name:
                            disponibilidade_data[field_name] = 1

                # Process afternoon availability
                if dias_tarde and dias_tarde != 'N/A':
                    dias_tarde_list = [d.strip() for d in dias_tarde.split(',')]
                    for dia in dias_tarde_list:
                        field_name = day_mapping.get(dia)
                        if field_name:
                            disponibilidade_data[f"{field_name}tarde"] = 1

                # Process night availability
                if dias_noite and dias_noite != 'N/A':
                    dias_noite_list = [d.strip() for d in dias_noite.split(',')]
                    for dia in dias_noite_list:
                        field_name = day_mapping.get(dia)
                        if field_name:
                            disponibilidade_data[f"{field_name}noite"] = 1

                # Insert disponibilidade_data into disponibilidade table
                fields = ', '.join(disponibilidade_data.keys())
                placeholders = ', '.join(['%s'] * len(disponibilidade_data))
                values = list(disponibilidade_data.values())
                insert_disponibilidade_query = f"INSERT INTO Disponibilidade ({fields}) VALUES ({placeholders})"
                cursor.execute(insert_disponibilidade_query, values)
                disponibilidade_id = cursor.lastrowid

                # Insert into Professor_Disponibilidade table
                insert_professor_disponibilidade_query = """
                    INSERT INTO Professor_Disponibilidade (professor_id, disponibilidade_id)
                    VALUES (%s, %s)
                """
                cursor.execute(insert_professor_disponibilidade_query, (professor_id, disponibilidade_id))

            # Commit the transaction
            connection.commit()
            print("Dados inseridos com sucesso.")

    except Exception as e:
        print(f"Erro ao inserir dados: {e}")
    finally:
        if connection:
            connection.close()






