from flask import Flask, request, jsonify
from flask_restx import Api, Resource
from db import get_connection, insert_data_to_mysql
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



if __name__ == "__main__":
    app.run(debug=True)
