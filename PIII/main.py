from flask import Flask
from db import get_connection

def main():
    try:
        # Estabelece a conexão com o banco de dados
        connection = get_connection()
        print("Conexão com o banco de dados estabelecida com sucesso!")
        
        while True:
            pass  

    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
    finally:

        if 'connection' in locals():
            connection.close()
            print("Conexão com o banco de dados fechada.")

if __name__ == "__main__":
    main()
