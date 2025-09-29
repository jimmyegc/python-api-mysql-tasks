import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow

# Cargar variables de .env
load_dotenv()

app = Flask(__name__)

# Construir la URL de conexión desde el .env
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS") == "True"

db = SQLAlchemy(app)
ma = Marshmallow(app)

# ---------------------------
# MODELO
# ---------------------------
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(70), unique=True, nullable=False)
    description = db.Column(db.String(100), nullable=True)
    
    def __init__(self, title, description):
        self.title = title
        self.description = description

# ---------------------------
# SCHEMA
# ---------------------------
class TaskSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        load_instance = True

task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)

# ---------------------------
# RUTAS CRUD
# ---------------------------

# Crear tarea
@app.route('/tasks', methods=['POST'])
def create_task():
    title = request.json.get('title')
    description = request.json.get('description')

    new_task = Task(title, description)
    db.session.add(new_task)
    db.session.commit()

    return task_schema.jsonify(new_task), 201


# Listar todas las tareas
@app.route('/tasks', methods=['GET'])
def get_tasks():
    all_tasks = Task.query.all()
    return jsonify(tasks_schema.dump(all_tasks))


# Obtener una sola tarea por ID
@app.route('/tasks/<int:id>', methods=['GET'])
def get_task(id):
    task = Task.query.get_or_404(id)
    return task_schema.jsonify(task)


# Actualizar una tarea
@app.route('/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    task = Task.query.get_or_404(id)

    task.title = request.json.get('title', task.title)
    task.description = request.json.get('description', task.description)

    db.session.commit()
    return task_schema.jsonify(task)


# Eliminar una tarea
@app.route('/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.get_or_404(id)

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": f"Tarea {id} eliminada"}), 200


# ---------------------------
# MAIN
# ---------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # crea tablas si no existen
    app.run(debug=True)
