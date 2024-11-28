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
        print("Iniciando a inserção de disponibilidade no MySQL")
        print(f"Dados recebidos: {data}")
        connection = get_connection()
        print("Conexão com o banco de dados estabelecida")
        with connection.cursor() as cursor:
            # Extrair informações do professor
            nome = data.get('nome', 'N/A')
            email = data.get('email', 'N/A')
            print(f"Nome do professor: {nome}, Email: {email}")

            # Buscar o professor na tabela Professores
            select_professor_query = "SELECT id FROM Professores WHERE nome = %s AND email = %s"
            cursor.execute(select_professor_query, (nome, email))
            professor_result = cursor.fetchone()
            print(f"Resultado da busca do professor: {professor_result}")
            if professor_result:
                professor_id = professor_result['id']
                print(f"Professor encontrado com ID: {professor_id}")
            else:
                # Inserir novo professor se não encontrado
                insert_professor_query = "INSERT INTO Professores (nome, email) VALUES (%s, %s)"
                cursor.execute(insert_professor_query, (nome, email))
                professor_id = cursor.lastrowid
                print(f"Novo professor inserido com ID: {professor_id}")

            # Processar informações do campus
            campus = data.get('campus', 'N/A')
            print(f"Campus recebido: {campus}")
            campus_list = [c.strip() for c in campus.split(',')] if campus != 'N/A' else []
            print(f"Lista de campus: {campus_list}")

            # Mapeamento dos dias para os campos correspondentes na tabela
            day_mapping = {
                'Segunda': 'seg',
                'Terça': 'ter',
                'Quarta': 'quar',
                'Quinta': 'quin',
                'Sexta': 'sex',
            }

            # Para cada campus, processar dados de disponibilidade
            for c in campus_list:
                print(f"Processando dados para o campus: {c}")
                disponibilidade_data = {
                    'professor_id': professor_id,
                    'turno_id': None,  # Supondo que turno_id é opcional ou pode ser NULL
                    'campus_id': None,  # Será definido após buscar na tabela Campus
                    'consideracoes': '',
                    'segmanha': 0,
                    'termanha': 0,
                    'quarmanha': 0,
                    'quinmanha': 0,
                    'sexmanha': 0,
                    'segtarde': 0,
                    'tertarde': 0,
                    'quartarde': 0,
                    'quintarde': 0,
                    'sextarde': 0,
                    'segnoite': 0,
                    'ternoite': 0,
                    'quarnoite': 0,
                    'quinnoite': 0,
                    'sexnoite': 0,
                }

                # Buscar campus_id na tabela Campus
                select_campus_query = "SELECT id FROM Campus WHERE nome = %s"
                cursor.execute(select_campus_query, (c,))
                campus_result = cursor.fetchone()
                print(f"Resultado da busca do campus: {campus_result}")
                if campus_result:
                    campus_id = campus_result['id']
                    disponibilidade_data['campus_id'] = campus_id
                    print(f"Campus encontrado com ID: {campus_id}")
                else:
                    # Tratar erro: Campus não encontrado
                    print(f"Campus não encontrado: {c}")
                    continue  # Pular para o próximo campus

                # Para "Asa Norte", usar os campos sem sufixo
                if c == 'Asa Norte':
                    dias_manha = data.get('diasdemanha', '')
                    dias_tarde = data.get('diasdetarde', '')
                    dias_noite = data.get('diasdenoite', '')
                    observacao = data.get('observacao1', '')
                    print(f"Dias de manhã: {dias_manha}")
                    print(f"Dias de tarde: {dias_tarde}")
                    print(f"Dias de noite: {dias_noite}")
                    print(f"Observação: {observacao}")
                # Para "Taguatinga", usar os campos com sufixo 2/3
                elif c == 'Taguatinga':
                    dias_manha = data.get('diasdemanha2', '')
                    dias_tarde = data.get('diasdetarde2', '')
                    dias_noite = data.get('diasdenoite3', '')
                    observacao = data.get('observacao2', '')
                    print(f"Dias de manhã: {dias_manha}")
                    print(f"Dias de tarde: {dias_tarde}")
                    print(f"Dias de noite: {dias_noite}")
                    print(f"Observação: {observacao}")
                else:
                    # Campus desconhecido
                    print(f"Campus desconhecido: {c}")
                    continue

                disponibilidade_data['consideracoes'] = observacao

                # Processar disponibilidade de manhã
                if dias_manha and dias_manha != 'N/A':
                    dias_manha_list = [d.strip() for d in dias_manha.split(',')]
                    print(f"Lista de dias de manhã: {dias_manha_list}")
                    for dia in dias_manha_list:
                        field_prefix = day_mapping.get(dia)
                        if field_prefix:
                            field_name = f"{field_prefix}manha"
                            disponibilidade_data[field_name] = 1
                            print(f"Disponibilidade manhã atualizada: {field_name} = 1")
                        else:
                            print(f"Dia inválido encontrado na manhã: {dia}")

                # Processar disponibilidade de tarde
                if dias_tarde and dias_tarde != 'N/A':
                    dias_tarde_list = [d.strip() for d in dias_tarde.split(',')]
                    print(f"Lista de dias de tarde: {dias_tarde_list}")
                    for dia in dias_tarde_list:
                        field_prefix = day_mapping.get(dia)
                        if field_prefix:
                            field_name = f"{field_prefix}tarde"
                            disponibilidade_data[field_name] = 1
                            print(f"Disponibilidade tarde atualizada: {field_name} = 1")
                        else:
                            print(f"Dia inválido encontrado na tarde: {dia}")

                # Processar disponibilidade de noite
                if dias_noite and dias_noite != 'N/A':
                    dias_noite_list = [d.strip() for d in dias_noite.split(',')]
                    print(f"Lista de dias de noite: {dias_noite_list}")
                    for dia in dias_noite_list:
                        field_prefix = day_mapping.get(dia)
                        if field_prefix:
                            field_name = f"{field_prefix}noite"
                            disponibilidade_data[field_name] = 1
                            print(f"Disponibilidade noite atualizada: {field_name} = 1")
                        else:
                            print(f"Dia inválido encontrado na noite: {dia}")

                print(f"Dados de disponibilidade a serem inseridos: {disponibilidade_data}")
                # Inserir disponibilidade_data na tabela Disponibilidade
                fields = ', '.join(disponibilidade_data.keys())
                placeholders = ', '.join(['%s'] * len(disponibilidade_data))
                values = list(disponibilidade_data.values())
                insert_disponibilidade_query = f"INSERT INTO Disponibilidade ({fields}) VALUES ({placeholders})"
                cursor.execute(insert_disponibilidade_query, values)
                disponibilidade_id = cursor.lastrowid
                print(f"Disponibilidade inserida com ID: {disponibilidade_id}")

                # Inserir na tabela Professor_Disponibilidade
                insert_professor_disponibilidade_query = """
                    INSERT INTO Professor_Disponibilidade (professor_id, disponibilidade_id)
                    VALUES (%s, %s)
                """
                cursor.execute(insert_professor_disponibilidade_query, (professor_id, disponibilidade_id))
                print("Relação Professor_Disponibilidade inserida com sucesso")

            # Confirmar a transação
            connection.commit()
            print("Dados inseridos com sucesso.")

    except Exception as e:
        print(f"Erro ao inserir dados: {e}")
    finally:
        if connection:
            connection.close()
            print("Conexão com o banco de dados fechada")






