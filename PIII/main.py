from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
from db import get_connection, insert_data_to_mysql, insert_disponibilidade_to_mysql
from googlecloud import get_sheet_data


# Inicializa o aplicativo Flask
app = Flask(__name__)

# Inicializa a API com Flask-RESTx
api = Api(app)

# Função para conectar ao banco de dados
def get_db_connection():
    try:
        connection = get_connection()
        print("Conexão com o banco de dados estabelecida com sucesso!")
        return connection
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None
    
# Função de fechamento seguro da conexão
def close_connection(connection):
    if connection:
        connection.close()

# Rota principal da API
@api.route('/status')
class Status(Resource):
    def get(self):
        # Verifica a conexão com o banco de dados
        connection = None
        try:
            connection = get_db_connection()
            if connection:
                return {"message": "Conexão com o banco de dados está ativa!"}, 200
            else:
                return {"message": "Erro ao conectar ao banco de dados!"}, 500
        except Exception as e:
            return {"message": f"Erro durante a verificação: {e}"}, 500
        finally:
            if connection:
                connection.close()



# Rota de exemplo para operações com o banco de dados
@api.route('/dados')
class Dados(Resource):
    def get(self):
        # Obtém conexão com o banco de dados
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM Professores")
                dados = cursor.fetchall()
                return {"dados": dados}, 200
            except Exception as e:
                return {"message": f"Erro ao consultar dados: {e}"}, 500
            finally:
                connection.close()
        else:
            return {"message": "Não foi possível conectar ao banco de dados!"}, 500
        
# Função para inserir dados
@api.route('/dados', methods=['POST'])
class InserirDados(Resource):
    def post(self):
        connection = get_db_connection()
        if connection:
            try:
                data = request.json  # Recebe os dados no formato JSON
                nome = data.get('nome')
                valor = data.get('valor')

                cursor = connection.cursor()
                cursor.execute("INSERT INTO tabela_exemplo (nome, valor) VALUES (%s, %s)", (nome, valor))
                connection.commit()
                
                return {"message": "Dados inseridos com sucesso!"}, 201
            except Exception as e:
                return {"message": f"Erro ao inserir dados: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Não foi possível conectar ao banco de dados!"}, 500
        
# Função para atualizar dados
@api.route('/dados/<int:id>', methods=['PUT'])
class AtualizarDados(Resource):
    def put(self, id):
        connection = get_db_connection()
        if connection:
            try:
                data = request.json  # Recebe os dados no formato JSON
                nome = data.get('nome')
                valor = data.get('valor')

                cursor = connection.cursor()
                cursor.execute("UPDATE tabela_exemplo SET nome = %s, valor = %s WHERE id = %s", (nome, valor, id))
                connection.commit()

                return {"message": "Dados atualizados com sucesso!"}, 200
            except Exception as e:
                return {"message": f"Erro ao atualizar dados: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Não foi possível conectar ao banco de dados!"}, 500
        
# Função para deletar dados
@api.route('/dados/<int:id>', methods=['DELETE'])
class DeletarDados(Resource):
    def delete(self, id):
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("DELETE FROM tabela_exemplo WHERE id = %s", (id,))
                connection.commit()

                return {"message": "Dados deletados com sucesso!"}, 200
            except Exception as e:
                return {"message": f"Erro ao deletar dados: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Não foi possível conectar ao banco de dados!"}, 500

        
# Google Sheets para DB

@app.route('/insert_data', methods=['POST'])
def insert_data():
    data = request.get_json()  # Obter o JSON da requisição
    print("Dados recebidos:", data)  # Adiciona esta linha para verificar o conteúdo de 'data'
    
    if not data:
        return jsonify({"error": "Nenhum dado recebido"}), 400

    # Passe o `data` para a função de inserção no banco de dados
    insert_data_to_mysql(data)
    return jsonify({"status": "Dados inseridos com sucesso"}), 200

@app.route('/insert_data2', methods=['POST'])
def insert_data2():
    data = request.get_json()  # Obter o JSON da requisição
    print("Dados recebidos:", data)  # Verificar o conteúdo de 'data'
    
    if not data:
        return jsonify({"error": "Nenhum dado recebido"}), 400

    # Chamar a função de inserção passando 'data'
    insert_disponibilidade_to_mysql(data)
    return jsonify({"status": "Dados inseridos com sucesso"}), 200

# Endpoint para consultar a tabela Curso
@api.route('/cursos')
class Cursos(Resource):
    def get(self):
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM Curso")
                cursos = cursor.fetchall()
                return {"cursos": cursos}, 200
            except Exception as e:
                return {"message": f"Erro ao consultar Cursos: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Não foi possível conectar ao banco de dados!"}, 500


# Endpoint para consultar a tabela Materia_Curso
@api.route('/materia_cursos')
class MateriaCursos(Resource):
    def get(self):
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM Materia_Curso")
                materia_cursos = cursor.fetchall()
                return {"materia_cursos": materia_cursos}, 200
            except Exception as e:
                return {"message": f"Erro ao consultar Materia_Curso: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Não foi possível conectar ao banco de dados!"}, 500


# Endpoint para consultar a tabela Professor_Materia
@api.route('/professor_materias')
class ProfessorMaterias(Resource):
    def get(self):
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM Professor_Materia")
                professor_materias = cursor.fetchall()
                return {"professor_materias": professor_materias}, 200
            except Exception as e:
                return {"message": f"Erro ao consultar Professor_Materia: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Não foi possível conectar ao banco de dados!"}, 500


# Endpoint para consultar a tabela Professor_Disponibilidade
@api.route('/professor_disponibilidades')
class ProfessorDisponibilidades(Resource):
    def get(self):
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM Professor_Disponibilidade")
                professor_disponibilidades = cursor.fetchall()
                return {"professor_disponibilidades": professor_disponibilidades}, 200
            except Exception as e:
                return {"message": f"Erro ao consultar Professor_Disponibilidade: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Não foi possível conectar ao banco de dados!"}, 500

turma_model = api.model('Turma', {
    'semestre': fields.String(required=True, description='Semestre da turma, ex: 2024.1'),
    'materia_curso_id': fields.Integer(required=True, description='ID da matéria do curso'),
    'campus_id': fields.Integer(required=True, description='ID do campus associado à turma'),
    'turno': fields.String(required=True, description='Turno da turma, ex: Matutino'),
    'dia_da_semana': fields.String(required=True, description='Dia da semana da aula, ex: Segunda-feira')
})

# Endpoint para criar uma turma com a FK do campus
@api.route('/turmas')
class CriarTurma(Resource):
    @api.expect(turma_model, validate=True)
    @api.doc(description="Cria uma turma sem professor associado e vincula a um campus.")
    def post(self):
        connection = get_db_connection()
        if connection:
            try:
                data = request.json  # Recebe os dados no formato JSON

                # Obtém os valores do JSON
                semestre = data['semestre']
                materia_curso_id = data['materia_curso_id']
                campus_id = data['campus_id']
                turno = data['turno']
                dia_da_semana = data['dia_da_semana']

                # Validação básica para campus_id
                if not isinstance(campus_id, int) or campus_id <= 0:
                    return {"message": "O campo campus_id deve ser um número inteiro positivo!"}, 400

                # Insere os dados na tabela Turma, professor_id como NULL
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO Turma (semestre, materia_curso_id, professor_id, campus_id, turno, dia_da_semana)
                    VALUES (%s, %s, NULL, %s, %s, %s)
                """, (semestre, materia_curso_id, campus_id, turno, dia_da_semana))
                connection.commit()

                return {"message": "Turma criada com sucesso!"}, 201
            except Exception as e:
                return {"message": f"Erro ao criar a turma: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Não foi possível conectar ao banco de dados!"}, 500
        
def verificar_compatibilidade_turma(turma_id):
    connection = get_db_connection()
    if not connection:
        return {"message": "Erro ao conectar ao banco de dados!"}, 500

    try:
        cursor = connection.cursor()

        # Passo 1: Buscar informações da turma
        query_turma = """
            SELECT id, semestre, materia_id, professor_id, turno, dia_da_semana, campus_id 
            FROM Turma 
            WHERE id = %s
        """
        print("Consulta SQL (Turma):", query_turma)
        cursor.execute(query_turma, (turma_id,))
        turma = cursor.fetchone()
        print("Resultado da consulta da turma:", turma)
        if not turma:
            return {"message": "Turma não encontrada!"}, 404

        # Extrair os campos
        turma_id = turma['id']
        semestre = turma['semestre']
        materia_id = turma['materia_id']
        professor_id = turma['professor_id']
        turno = turma['turno']
        dia_da_semana = turma['dia_da_semana']
        campus_id = turma['campus_id']

        print(f"Campus ID: {campus_id}, Dia: {dia_da_semana}, Turno: {turno}, Materia_ID: {materia_id}")

        if not campus_id or not dia_da_semana or not turno:
            return {"message": "Dados incompletos na tabela Turma!"}, 500

        # Passo 2: Buscar professores com a mesma matéria da turma
        query_professores = """
            SELECT pm.professor_id
            FROM Professor_Materia pm
            WHERE pm.materia_id = %s
        """
        print("Consulta SQL (Professor_Materia):", query_professores)
        print(f"Parâmetro (Materia_ID): {materia_id}")
        cursor.execute(query_professores, (materia_id,))
        professores = cursor.fetchall()
        print("Professores encontrados na Professor_Materia:", professores)

        if not professores:
            return {"message": "Nenhum professor encontrado para a matéria da turma!"}, 404

        professor_ids = [p['professor_id'] for p in professores]
        print("Lista de IDs de professores:", professor_ids)

        # Passo 3: Verificar disponibilidade dos professores no mesmo campus e dia/turno
        coluna_dia_turno = f"{dia_da_semana.lower()}{turno.lower()}"  # Ex.: segmanha ou segnoite
        print(f"Coluna do dia/turno a ser verificada: {coluna_dia_turno}")

        # Montar a consulta SQL dinâmica corretamente
        format_strings = ','.join(['%s'] * len(professor_ids))
        query_disponibilidade = f"""
            SELECT d.professor_id
            FROM Disponibilidade d
            WHERE d.campus_id = %s 
              AND d.{coluna_dia_turno} = 1 
              AND d.professor_id IN ({format_strings})
        """
        parametros_disponibilidade = [campus_id] + professor_ids
        print("Consulta SQL (Disponibilidade):", query_disponibilidade)
        print("Parâmetros (Disponibilidade):", parametros_disponibilidade)
        cursor.execute(query_disponibilidade, parametros_disponibilidade)
        professores_disponiveis = cursor.fetchall()
        print("Professores disponíveis encontrados:", professores_disponiveis)

        if not professores_disponiveis:
            return {"message": "Nenhum professor disponível para a turma!"}, 404

        professores_compativeis = [p['professor_id'] for p in professores_disponiveis]
        print("Professores compatíveis:", professores_compativeis)

        return {"professores_compatíveis": professores_compativeis}, 200

    except Exception as e:
        print("Erro capturado (detalhado):", repr(e))
        return {"message": f"Erro ao verificar compatibilidade: {repr(e)}"}, 500
    finally:
        close_connection(connection)




professores_model = api.model('ProfessoresCompatibilidade', {
    'professores_compatíveis': fields.List(fields.Integer, description='Lista de IDs dos professores compatíveis')
})

# Endpoint para verificar compatibilidade de professores com uma turma
@api.route('/turmas/<int:turma_id>/professores_compativeis')
class ProfessoresCompativeis(Resource):
    @api.doc(description="Verifica a compatibilidade de professores para uma turma com base na matéria e na disponibilidade.")
    @api.response(200, 'Professores encontrados', model=professores_model)
    @api.response(404, 'Nenhum professor encontrado ou disponível')
    @api.response(500, 'Erro interno ao processar a solicitação')
    def get(self, turma_id):
        """
        Retorna uma lista de professores compatíveis para uma turma específica.
        """
        try:
            resultado, status = verificar_compatibilidade_turma(turma_id)
            return resultado, status
        except Exception as e:
            return {"message": f"Erro ao processar a solicitação: {e}"}, 500

if __name__ == "__main__":
    app.run(debug=True)
