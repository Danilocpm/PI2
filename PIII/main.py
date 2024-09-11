from flask import Flask
from flask_restx import Api, Resource
from db import get_connection

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
                cursor.execute("SELECT * FROM tabela_exemplo")  # Exemplo de consulta SQL
                dados = cursor.fetchall()
                return {"dados": dados}, 200
            except Exception as e:
                return {"message": f"Erro ao consultar dados: {e}"}, 500
            finally:
                connection.close()
        else:
            return {"message": "Não foi possível conectar ao banco de dados!"}, 500

if __name__ == "__main__":
    app.run(debug=True)
