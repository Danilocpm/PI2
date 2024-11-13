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









