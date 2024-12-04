from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
from db import get_connection, insert_data_to_mysql, insert_disponibilidade_to_mysql
from googlecloud import get_sheet_data

# Initialize the Flask application
app = Flask(__name__)

# Initialize the API with Flask-RESTx
api = Api(app, version='1.0', title='API Documentation',
          description='A simple API',)

# Function to get database connection
def get_db_connection():
    try:
        connection = get_connection()
        print("Successfully connected to the database!")
        return connection
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

# Function to safely close the connection
def close_connection(connection):
    if connection:
        connection.close()

# Define models for Swagger documentation

# Campus Model
campus_model = api.model('Campus', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a campus'),
    'nome': fields.String(required=True, description='The name of the campus')
})

# Curso Model
curso_model = api.model('Curso', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a course'),
    'name': fields.String(required=True, description='The name of the course')
})

# Turno Model
turno_model = api.model('Turno', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a shift'),
    'hturno': fields.Integer(required=True, description='Shift hours')
})

# Professor Model
professor_model = api.model('Professor', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a professor'),
    'nome': fields.String(required=True, description='The name of the professor'),
    'curriculo': fields.String(description='Curriculum of the professor'),
    'email': fields.String(description='Email of the professor')
})

# Materia Model
materia_model = api.model('Materia', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a subject'),
    'nome': fields.String(required=True, description='Name of the subject'),
    'semestre': fields.String(description='Semester of the subject'),
    'modalidade': fields.String(description='Modality of the subject'),
    'curriculo': fields.String(description='Curriculum of the subject'),
    'area': fields.String(description='Area of the subject', enum=['matematica', 'programacao', 'teoria'])
})

# Materia_Curso Model
materia_curso_model = api.model('MateriaCurso', {
    'id': fields.Integer(readOnly=True, description='The unique identifier'),
    'materia_id': fields.Integer(required=True, description='ID of the subject'),
    'curso_id': fields.Integer(required=True, description='ID of the course')
})

# Disponibilidade Model
disponibilidade_model = api.model('Disponibilidade', {
    'id': fields.Integer(readOnly=True, description='The unique identifier'),
    'professor_id': fields.Integer(required=True, description='ID of the professor'),
    'turno_id': fields.Integer(description='ID of the shift'),
    'campus_id': fields.Integer(required=True, description='ID of the campus'),
    'consideracoes': fields.String(description='Considerations'),
    'segmanha': fields.Boolean(description='Monday Morning'),
    'termanha': fields.Boolean(description='Tuesday Morning'),
    'quarmanha': fields.Boolean(description='Wednesday Morning'),
    'quinmanha': fields.Boolean(description='Thursday Morning'),
    'sexmanha': fields.Boolean(description='Friday Morning'),
    'segtarde': fields.Boolean(description='Monday Afternoon'),
    'tertarde': fields.Boolean(description='Tuesday Afternoon'),
    'quartarde': fields.Boolean(description='Wednesday Afternoon'),
    'quintarde': fields.Boolean(description='Thursday Afternoon'),
    'sextarde': fields.Boolean(description='Friday Afternoon'),
    'segnoite': fields.Boolean(description='Monday Night'),
    'ternoite': fields.Boolean(description='Tuesday Night'),
    'quarnoite': fields.Boolean(description='Wednesday Night'),
    'quinnoite': fields.Boolean(description='Thursday Night'),
    'sexnoite': fields.Boolean(description='Friday Night')
})

# Professor_Disponibilidade Model
professor_disponibilidade_model = api.model('ProfessorDisponibilidade', {
    'id': fields.Integer(readOnly=True, description='The unique identifier'),
    'professor_id': fields.Integer(required=True, description='ID of the professor'),
    'disponibilidade_id': fields.Integer(required=True, description='ID of the availability')
})

# Professor_Materia Model
professor_materia_model = api.model('ProfessorMateria', {
    'id': fields.Integer(readOnly=True, description='The unique identifier'),
    'professor_id': fields.Integer(required=True, description='ID of the professor'),
    'materia_id': fields.Integer(required=True, description='ID of the subject')
})

# Turma Model
turma_model = api.model('Turma', {
    'id': fields.Integer(readOnly=True, description='The unique identifier'),
    'semestre': fields.String(required=True, description='Semester of the class, e.g., 2024.1'),
    'materia_curso_id': fields.Integer(required=True, description='ID of the subject-course relation'),
    'professor_id': fields.Integer(description='ID of the professor'),
    'turno': fields.String(required=True, description='Shift of the class', enum=['tarde', 'noite', 'manha']),
    'dia_da_semana': fields.String(required=True, description='Day of the week', enum=['seg', 'ter', 'quar', 'quinta', 'sex']),
    'campus_id': fields.Integer(required=True, description='ID of the campus'),
    'materia_id': fields.Integer(required=True, description='ID of the subject')
})

# Endpoint for Campus
@api.route('/campus')
class CampusList(Resource):
    @api.marshal_list_with(campus_model)
    def get(self):
        """List all campuses"""
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM Campus")
                campuses = cursor.fetchall()
                return campuses, 200
            except Exception as e:
                return {"message": f"Error retrieving campuses: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

    @api.expect(campus_model)
    @api.response(201, 'Campus successfully created.')
    def post(self):
        """Create a new campus"""
        data = request.json
        nome = data.get('nome')
        if not nome:
            return {"message": "The field 'nome' is required!"}, 400
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("INSERT INTO Campus (nome) VALUES (%s)", (nome,))
                connection.commit()
                return {"message": "Campus successfully created."}, 201
            except Exception as e:
                return {"message": f"Error creating campus: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

@api.route('/campus/<int:id>')
class CampusResource(Resource):
    @api.marshal_with(campus_model)
    def get(self, id):
        """Get a campus by ID"""
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM Campus WHERE id = %s", (id,))
                campus = cursor.fetchone()
                if campus:
                    return campus, 200
                else:
                    return {"message": "Campus not found."}, 404
            except Exception as e:
                return {"message": f"Error retrieving campus: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

    @api.expect(campus_model)
    def put(self, id):
        """Update a campus"""
        data = request.json
        nome = data.get('nome')
        if not nome:
            return {"message": "The field 'nome' is required!"}, 400
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("UPDATE Campus SET nome = %s WHERE id = %s", (nome, id))
                connection.commit()
                return {"message": "Campus successfully updated."}, 200
            except Exception as e:
                return {"message": f"Error updating campus: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

    def delete(self, id):
        """Delete a campus"""
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("DELETE FROM Campus WHERE id = %s", (id,))
                connection.commit()
                return {"message": "Campus successfully deleted."}, 200
            except Exception as e:
                return {"message": f"Error deleting campus: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

# Endpoint for Curso
@api.route('/cursos')
class CursoList(Resource):
    @api.marshal_list_with(curso_model)
    def get(self):
        """List all courses"""
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM Curso")
                cursos = cursor.fetchall()
                return cursos, 200
            except Exception as e:
                return {"message": f"Error retrieving courses: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

    @api.expect(curso_model)
    @api.response(201, 'Course successfully created.')
    def post(self):
        """Create a new course"""
        data = request.json
        name = data.get('name')
        if not name:
            return {"message": "The field 'name' is required!"}, 400
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("INSERT INTO Curso (name) VALUES (%s)", (name,))
                connection.commit()
                return {"message": "Course successfully created."}, 201
            except Exception as e:
                return {"message": f"Error creating course: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

@api.route('/cursos/<int:id>')
class CursoResource(Resource):
    @api.marshal_with(curso_model)
    def get(self, id):
        """Get a course by ID"""
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM Curso WHERE id = %s", (id,))
                curso = cursor.fetchone()
                if curso:
                    return curso, 200
                else:
                    return {"message": "Course not found."}, 404
            except Exception as e:
                return {"message": f"Error retrieving course: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

    @api.expect(curso_model)
    def put(self, id):
        """Update a course"""
        data = request.json
        name = data.get('name')
        if not name:
            return {"message": "The field 'name' is required!"}, 400
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("UPDATE Curso SET name = %s WHERE id = %s", (name, id))
                connection.commit()
                return {"message": "Course successfully updated."}, 200
            except Exception as e:
                return {"message": f"Error updating course: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

    def delete(self, id):
        """Delete a course"""
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("DELETE FROM Curso WHERE id = %s", (id,))
                connection.commit()
                return {"message": "Course successfully deleted."}, 200
            except Exception as e:
                return {"message": f"Error deleting course: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

# Endpoint for Professores
@api.route('/professores')
class ProfessoresList(Resource):
    @api.marshal_list_with(professor_model)
    def get(self):
        """List all professors"""
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM Professores")
                professores = cursor.fetchall()
                return professores, 200
            except Exception as e:
                return {"message": f"Error retrieving professors: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

    @api.expect(professor_model)
    @api.response(201, 'Professor successfully created.')
    def post(self):
        """Create a new professor"""
        data = request.json
        nome = data.get('nome')
        curriculo = data.get('curriculo')
        email = data.get('email')
        if not nome:
            return {"message": "The field 'nome' is required!"}, 400
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("INSERT INTO Professores (nome, curriculo, email) VALUES (%s, %s, %s)", (nome, curriculo, email))
                connection.commit()
                return {"message": "Professor successfully created."}, 201
            except Exception as e:
                return {"message": f"Error creating professor: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

@api.route('/professores/<int:id>')
class ProfessorResource(Resource):
    @api.marshal_with(professor_model)
    def get(self, id):
        """Get a professor by ID"""
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM Professores WHERE id = %s", (id,))
                professor = cursor.fetchone()
                if professor:
                    return professor, 200
                else:
                    return {"message": "Professor not found."}, 404
            except Exception as e:
                return {"message": f"Error retrieving professor: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

    @api.expect(professor_model)
    def put(self, id):
        """Update a professor"""
        data = request.json
        nome = data.get('nome')
        curriculo = data.get('curriculo')
        email = data.get('email')
        if not nome:
            return {"message": "The field 'nome' is required!"}, 400
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("UPDATE Professores SET nome = %s, curriculo = %s, email = %s WHERE id = %s", (nome, curriculo, email, id))
                connection.commit()
                return {"message": "Professor successfully updated."}, 200
            except Exception as e:
                return {"message": f"Error updating professor: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

    def delete(self, id):
        """Delete a professor"""
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("DELETE FROM Professores WHERE id = %s", (id,))
                connection.commit()
                return {"message": "Professor successfully deleted."}, 200
            except Exception as e:
                return {"message": f"Error deleting professor: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

# Endpoint for Materia
@api.route('/materias')
class MateriaList(Resource):
    @api.marshal_list_with(materia_model)
    def get(self):
        """List all subjects"""
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM Materia")
                materias = cursor.fetchall()
                return materias, 200
            except Exception as e:
                return {"message": f"Error retrieving subjects: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

    @api.expect(materia_model)
    @api.response(201, 'Subject successfully created.')
    def post(self):
        """Create a new subject"""
        data = request.json
        nome = data.get('nome')
        semestre = data.get('semestre')
        modalidade = data.get('modalidade')
        curriculo = data.get('curriculo')
        area = data.get('area')
        if not nome:
            return {"message": "The field 'nome' is required!"}, 400
        if area not in ['matematica', 'programacao', 'teoria']:
            return {"message": "The field 'area' must be one of 'matematica', 'programacao', 'teoria'."}, 400
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("INSERT INTO Materia (nome, semestre, modalidade, curriculo, area) VALUES (%s, %s, %s, %s, %s)", (nome, semestre, modalidade, curriculo, area))
                connection.commit()
                return {"message": "Subject successfully created."}, 201
            except Exception as e:
                return {"message": f"Error creating subject: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

@api.route('/materias/<int:id>')
class MateriaResource(Resource):
    @api.marshal_with(materia_model)
    def get(self, id):
        """Get a subject by ID"""
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM Materia WHERE id = %s", (id,))
                materia = cursor.fetchone()
                if materia:
                    return materia, 200
                else:
                    return {"message": "Subject not found."}, 404
            except Exception as e:
                return {"message": f"Error retrieving subject: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

    @api.expect(materia_model)
    def put(self, id):
        """Update a subject"""
        data = request.json
        nome = data.get('nome')
        semestre = data.get('semestre')
        modalidade = data.get('modalidade')
        curriculo = data.get('curriculo')
        area = data.get('area')
        if not nome:
            return {"message": "The field 'nome' is required!"}, 400
        if area not in ['matematica', 'programacao', 'teoria']:
            return {"message": "The field 'area' must be one of 'matematica', 'programacao', 'teoria'."}, 400
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("UPDATE Materia SET nome = %s, semestre = %s, modalidade = %s, curriculo = %s, area = %s WHERE id = %s", (nome, semestre, modalidade, curriculo, area, id))
                connection.commit()
                return {"message": "Subject successfully updated."}, 200
            except Exception as e:
                return {"message": f"Error updating subject: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

    def delete(self, id):
        """Delete a subject"""
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("DELETE FROM Materia WHERE id = %s", (id,))
                connection.commit()
                return {"message": "Subject successfully deleted."}, 200
            except Exception as e:
                return {"message": f"Error deleting subject: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

# Endpoint for Materia_Curso
@api.route('/materia_cursos')
class MateriaCursoList(Resource):
    def get(self):
        """List all subject-course relations with full details"""
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                    SELECT mc.id, m.nome as materia_nome, c.name as curso_name
                    FROM Materia_Curso mc
                    JOIN Materia m ON mc.materia_id = m.id
                    JOIN Curso c ON mc.curso_id = c.id
                """
                cursor.execute(query)
                materia_cursos = cursor.fetchall()
                return {"materia_cursos": materia_cursos}, 200
            except Exception as e:
                return {"message": f"Error retrieving Materia_Curso: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

    @api.expect(materia_curso_model)
    @api.response(201, 'Relation successfully created.')
    def post(self):
        """Create a new subject-course relation"""
        data = request.json
        materia_id = data.get('materia_id')
        curso_id = data.get('curso_id')
        if not materia_id or not curso_id:
            return {"message": "Fields 'materia_id' and 'curso_id' are required!"}, 400
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("INSERT INTO Materia_Curso (materia_id, curso_id) VALUES (%s, %s)", (materia_id, curso_id))
                connection.commit()
                return {"message": "Relation successfully created."}, 201
            except Exception as e:
                return {"message": f"Error creating relation: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

@api.route('/materia_cursos/<int:id>')
class MateriaCursoResource(Resource):
    def get(self, id):
        """Get a subject-course relation by ID with full details"""
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                    SELECT mc.id, m.nome as materia_nome, c.name as curso_name
                    FROM Materia_Curso mc
                    JOIN Materia m ON mc.materia_id = m.id
                    JOIN Curso c ON mc.curso_id = c.id
                    WHERE mc.id = %s
                """
                cursor.execute(query, (id,))
                materia_curso = cursor.fetchone()
                if materia_curso:
                    return {"materia_curso": materia_curso}, 200
                else:
                    return {"message": "Relation not found."}, 404
            except Exception as e:
                return {"message": f"Error retrieving relation: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

    @api.expect(materia_curso_model)
    def put(self, id):
        """Update a subject-course relation"""
        data = request.json
        materia_id = data.get('materia_id')
        curso_id = data.get('curso_id')
        if not materia_id or not curso_id:
            return {"message": "Fields 'materia_id' and 'curso_id' are required!"}, 400
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("UPDATE Materia_Curso SET materia_id = %s, curso_id = %s WHERE id = %s", (materia_id, curso_id, id))
                connection.commit()
                return {"message": "Relation successfully updated."}, 200
            except Exception as e:
                return {"message": f"Error updating relation: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

    def delete(self, id):
        """Delete a subject-course relation"""
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("DELETE FROM Materia_Curso WHERE id = %s", (id,))
                connection.commit()
                return {"message": "Relation successfully deleted."}, 200
            except Exception as e:
                return {"message": f"Error deleting relation: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

# Endpoint for Professor_Materia
@api.route('/professor_materias')
class ProfessorMateriaList(Resource):
    def get(self):
        """List all professor-subject relations with full details"""
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                    SELECT pm.id, p.nome as professor_nome, m.nome as materia_nome
                    FROM Professor_Materia pm
                    JOIN Professores p ON pm.professor_id = p.id
                    JOIN Materia m ON pm.materia_id = m.id
                """
                cursor.execute(query)
                professor_materias = cursor.fetchall()
                return {"professor_materias": professor_materias}, 200
            except Exception as e:
                return {"message": f"Error retrieving Professor_Materia: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

    @api.expect(professor_materia_model)
    @api.response(201, 'Relation successfully created.')
    def post(self):
        """Create a new professor-subject relation"""
        data = request.json
        professor_id = data.get('professor_id')
        materia_id = data.get('materia_id')
        if not professor_id or not materia_id:
            return {"message": "Fields 'professor_id' and 'materia_id' are required!"}, 400
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("INSERT INTO Professor_Materia (professor_id, materia_id) VALUES (%s, %s)", (professor_id, materia_id))
                connection.commit()
                return {"message": "Relation successfully created."}, 201
            except Exception as e:
                return {"message": f"Error creating relation: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

@api.route('/professor_materias/<int:id>')
class ProfessorMateriaResource(Resource):
    def get(self, id):
        """Get a professor-subject relation by ID with full details"""
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                    SELECT pm.id, p.nome as professor_nome, m.nome as materia_nome
                    FROM Professor_Materia pm
                    JOIN Professores p ON pm.professor_id = p.id
                    JOIN Materia m ON pm.materia_id = m.id
                    WHERE pm.id = %s
                """
                cursor.execute(query, (id,))
                professor_materia = cursor.fetchone()
                if professor_materia:
                    return {"professor_materia": professor_materia}, 200
                else:
                    return {"message": "Relation not found."}, 404
            except Exception as e:
                return {"message": f"Error retrieving relation: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

    @api.expect(professor_materia_model)
    def put(self, id):
        """Update a professor-subject relation"""
        data = request.json
        professor_id = data.get('professor_id')
        materia_id = data.get('materia_id')
        if not professor_id or not materia_id:
            return {"message": "Fields 'professor_id' and 'materia_id' are required!"}, 400
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("UPDATE Professor_Materia SET professor_id = %s, materia_id = %s WHERE id = %s", (professor_id, materia_id, id))
                connection.commit()
                return {"message": "Relation successfully updated."}, 200
            except Exception as e:
                return {"message": f"Error updating relation: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

    def delete(self, id):
        """Delete a professor-subject relation"""
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("DELETE FROM Professor_Materia WHERE id = %s", (id,))
                connection.commit()
                return {"message": "Relation successfully deleted."}, 200
            except Exception as e:
                return {"message": f"Error deleting relation: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

# Endpoint for Turno
@api.route('/turnos')
class TurnoList(Resource):
    @api.marshal_list_with(turno_model)
    def get(self):
        """List all shifts"""
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM Turno")
                turnos = cursor.fetchall()
                return turnos, 200
            except Exception as e:
                return {"message": f"Error retrieving shifts: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

    @api.expect(turno_model)
    @api.response(201, 'Shift successfully created.')
    def post(self):
        """Create a new shift"""
        data = request.json
        hturno = data.get('hturno')
        if hturno is None:
            return {"message": "The field 'hturno' is required!"}, 400
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("INSERT INTO Turno (hturno) VALUES (%s)", (hturno,))
                connection.commit()
                return {"message": "Shift successfully created."}, 201
            except Exception as e:
                return {"message": f"Error creating shift: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

@api.route('/turnos/<int:id>')
class TurnoResource(Resource):
    @api.marshal_with(turno_model)
    def get(self, id):
        """Get a shift by ID"""
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM Turno WHERE id = %s", (id,))
                turno = cursor.fetchone()
                if turno:
                    return turno, 200
                else:
                    return {"message": "Shift not found."}, 404
            except Exception as e:
                return {"message": f"Error retrieving shift: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

    @api.expect(turno_model)
    def put(self, id):
        """Update a shift"""
        data = request.json
        hturno = data.get('hturno')
        if hturno is None:
            return {"message": "The field 'hturno' is required!"}, 400
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("UPDATE Turno SET hturno = %s WHERE id = %s", (hturno, id))
                connection.commit()
                return {"message": "Shift successfully updated."}, 200
            except Exception as e:
                return {"message": f"Error updating shift: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

    def delete(self, id):
        """Delete a shift"""
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("DELETE FROM Turno WHERE id = %s", (id,))
                connection.commit()
                return {"message": "Shift successfully deleted."}, 200
            except Exception as e:
                return {"message": f"Error deleting shift: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

# Endpoint for Disponibilidade
@api.route('/disponibilidades')
class DisponibilidadeList(Resource):
    def get(self):
        """List all availabilities with full details"""
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                    SELECT d.*, p.nome as professor_nome, t.hturno as turno_hturno, c.nome as campus_nome
                    FROM Disponibilidade d
                    JOIN Professores p ON d.professor_id = p.id
                    LEFT JOIN Turno t ON d.turno_id = t.id
                    JOIN Campus c ON d.campus_id = c.id
                """
                cursor.execute(query)
                disponibilidades = cursor.fetchall()
                return {"disponibilidades": disponibilidades}, 200
            except Exception as e:
                return {"message": f"Error retrieving Disponibilidade: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

    @api.expect(disponibilidade_model)
    @api.response(201, 'Availability successfully created.')
    def post(self):
        """Create a new availability"""
        data = request.json
        # Extract fields and validate as needed
        professor_id = data.get('professor_id')
        campus_id = data.get('campus_id')
        if not professor_id or not campus_id:
            return {"message": "Fields 'professor_id' and 'campus_id' are required!"}, 400
        # Additional validation and extraction of other fields
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                # Build INSERT query dynamically based on provided fields
                fields = []
                values = []
                for key in disponibilidade_model.keys():
                    if key in data:
                        fields.append(key)
                        values.append(data[key])
                fields_str = ', '.join(fields)
                placeholders = ', '.join(['%s'] * len(values))
                query = f"INSERT INTO Disponibilidade ({fields_str}) VALUES ({placeholders})"
                cursor.execute(query, values)
                connection.commit()
                return {"message": "Availability successfully created."}, 201
            except Exception as e:
                return {"message": f"Error creating availability: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

# Function to verify class compatibility
def verificar_compatibilidade_turma(turma_id):
    connection = get_db_connection()
    if not connection:
        return {"message": "Erro ao conectar ao banco de dados!"}, 500

    try:
        cursor = connection.cursor()

        # Step 1: Fetch class information
        query_turma = """
            SELECT id, semestre, materia_curso_id, professor_id, turno, dia_da_semana, campus_id 
            FROM Turma 
            WHERE id = %s
        """
        cursor.execute(query_turma, (turma_id,))
        turma = cursor.fetchone()
        if not turma:
            return {"message": "Turma não encontrada!"}, 404

        # Extract fields
        turma_id = turma['id']
        semestre = turma['semestre']
        materia_curso_id = turma['materia_curso_id']
        professor_id = turma['professor_id']
        turno = turma['turno']
        dia_da_semana = turma['dia_da_semana']
        campus_id = turma['campus_id']

        if not campus_id or not dia_da_semana or not turno:
            return {"message": "Dados incompletos na tabela Turma!"}, 500

        # Step 2: Get materia_id from materia_curso_id
        query_materia_curso = """
            SELECT materia_id
            FROM Materia_Curso
            WHERE id = %s
        """
        cursor.execute(query_materia_curso, (materia_curso_id,))
        materia_curso = cursor.fetchone()
        if not materia_curso:
            return {"message": "Materia_Curso não encontrado!"}, 404

        materia_id = materia_curso['materia_id']

        # Step 3: Find professors who teach the same subject
        query_professores = """
            SELECT pm.professor_id
            FROM Professor_Materia pm
            WHERE pm.materia_id = %s
        """
        cursor.execute(query_professores, (materia_id,))
        professores = cursor.fetchall()
        if not professores:
            return {"message": "Nenhum professor encontrado para a matéria da turma!"}, 404

        professor_ids = [p['professor_id'] for p in professores]

        # Step 4: Check availability of professors on the same campus and day/shift
        coluna_dia_turno = f"{dia_da_semana.lower()}{turno.lower()}"  # Ex.: segmanha or segnoite

        format_strings = ','.join(['%s'] * len(professor_ids))
        query_disponibilidade = f"""
            SELECT d.professor_id
            FROM Disponibilidade d
            WHERE d.campus_id = %s 
              AND d.{coluna_dia_turno} = 1 
              AND d.professor_id IN ({format_strings})
        """
        parametros_disponibilidade = [campus_id] + professor_ids
        cursor.execute(query_disponibilidade, parametros_disponibilidade)
        professores_disponiveis = cursor.fetchall()
        if not professores_disponiveis:
            return {"message": "Nenhum professor disponível para a turma!"}, 404

        professores_compativeis = [p['professor_id'] for p in professores_disponiveis]

        return {"professores_compatíveis": professores_compativeis}, 200

    except Exception as e:
        return {"message": f"Erro ao verificar compatibilidade: {repr(e)}"}, 500
    finally:
        close_connection(connection)

# ProfessoresCompatibilidade Model
professores_compatibilidade_model = api.model('ProfessoresCompatibilidade', {
    'professores_compatíveis': fields.List(fields.Integer, description='Lista de IDs dos professores compatíveis')
})

# Endpoint to check compatibility of professors with a class
@api.route('/turmas/<int:turma_id>/professores_compativeis')
class ProfessoresCompativeis(Resource):
    @api.doc(description="Verifica a compatibilidade de professores para uma turma com base na matéria e na disponibilidade.")
    @api.response(200, 'Professores encontrados', model=professores_compatibilidade_model)
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

# Existing endpoints for Campus, Curso, Professores, Materia, Materia_Curso, etc.

# Endpoint for Turma
@api.route('/turmas')
class TurmaList(Resource):
    def get(self):
        """List all classes with full details"""
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                    SELECT t.*, mc.materia_id, p.nome as professor_nome, c.nome as campus_nome
                    FROM Turma t
                    LEFT JOIN Materia_Curso mc ON t.materia_curso_id = mc.id
                    LEFT JOIN Professores p ON t.professor_id = p.id
                    JOIN Campus c ON t.campus_id = c.id
                """
                cursor.execute(query)
                turmas = cursor.fetchall()
                return {"turmas": turmas}, 200
            except Exception as e:
                return {"message": f"Error retrieving classes: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

    @api.expect(turma_model)
    @api.response(201, 'Class successfully created.')
    def post(self):
        """Create a new class"""
        data = request.json
        # Extract fields
        semestre = data.get('semestre')
        materia_curso_id = data.get('materia_curso_id')
        professor_id = data.get('professor_id')  # Optional
        turno = data.get('turno')
        dia_da_semana = data.get('dia_da_semana')
        campus_id = data.get('campus_id')
        materia_id = data.get('materia_id')
        # Validate required fields
        if not all([semestre, materia_curso_id, turno, dia_da_semana, campus_id, materia_id]):
            return {"message": "Missing required fields!"}, 400
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO Turma (semestre, materia_curso_id, professor_id, turno, dia_da_semana, campus_id, materia_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (semestre, materia_curso_id, professor_id, turno, dia_da_semana, campus_id, materia_id))
                connection.commit()
                return {"message": "Class successfully created."}, 201
            except Exception as e:
                return {"message": f"Error creating class: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

@api.route('/turmas/<int:id>')
class TurmaResource(Resource):
    def get(self, id):
        """Get a class by ID with full details"""
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                    SELECT t.*, mc.materia_id, p.nome as professor_nome, c.nome as campus_nome
                    FROM Turma t
                    LEFT JOIN Materia_Curso mc ON t.materia_curso_id = mc.id
                    LEFT JOIN Professores p ON t.professor_id = p.id
                    JOIN Campus c ON t.campus_id = c.id
                    WHERE t.id = %s
                """
                cursor.execute(query, (id,))
                turma = cursor.fetchone()
                if turma:
                    return {"turma": turma}, 200
                else:
                    return {"message": "Class not found."}, 404
            except Exception as e:
                return {"message": f"Error retrieving class: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

    @api.expect(turma_model)
    def put(self, id):
        """Update a class"""
        data = request.json
        # Extract fields
        semestre = data.get('semestre')
        materia_curso_id = data.get('materia_curso_id')
        professor_id = data.get('professor_id')  # Optional
        turno = data.get('turno')
        dia_da_semana = data.get('dia_da_semana')
        campus_id = data.get('campus_id')
        materia_id = data.get('materia_id')
        # Validate required fields
        if not all([semestre, materia_curso_id, turno, dia_da_semana, campus_id, materia_id]):
            return {"message": "Missing required fields!"}, 400
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("""
                    UPDATE Turma SET semestre = %s, materia_curso_id = %s, professor_id = %s, turno = %s, dia_da_semana = %s, campus_id = %s, materia_id = %s
                    WHERE id = %s
                """, (semestre, materia_curso_id, professor_id, turno, dia_da_semana, campus_id, materia_id, id))
                connection.commit()
                return {"message": "Class successfully updated."}, 200
            except Exception as e:
                return {"message": f"Error updating class: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500

    def delete(self, id):
        """Delete a class"""
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("DELETE FROM Turma WHERE id = %s", (id,))
                connection.commit()
                return {"message": "Class successfully deleted."}, 200
            except Exception as e:
                return {"message": f"Error deleting class: {e}"}, 500
            finally:
                close_connection(connection)
        else:
            return {"message": "Unable to connect to the database!"}, 500


if __name__ == "__main__":
    app.run(debug=True)
