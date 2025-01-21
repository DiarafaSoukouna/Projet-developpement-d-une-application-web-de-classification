from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import pymysql
ALLOWED_EXTENSIONS = {'docs', 'txt', 'doc'}
app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Répertoire contenant app.py
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'documents')  # Chemin absolu pour le dossier 'documents'
# Configuration de la base de données MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Utilisateur MySQL
app.config['MYSQL_PASSWORD'] = ''  # Mot de passe MySQL
app.config['MYSQL_DB'] = 'customers_base'  # Base de données MySQL
# mysql = MySQL(app)

# Initialisation de l'extension MySQL
#mysql = MySQL(app)

methods=['POST', 'PUT', 'GET', 'PATCH', 'DELETE']

def get_db():
    return pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB'],
        cursorclass=pymysql.cursors.DictCursor
)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/documents")
def documents():
    return render_template("documents.html")

@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/help")
def help_page():
    return render_template("help.html")
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @app.route('/')
# def home():
#     return 'Hello, World!'

@app.route('/upload', methods=['POST', 'GET'])
def file_upload():
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier détecté dans la requête'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        file.save(save_path)
        return jsonify({'message': 'Fichier téléchargé avec succès', 'filename': filename}), 200

    return jsonify({'error': 'Extension de fichier non autorisée'}), 400
    
    
    
# @app.route('/', methods=['GET'])
# def list_customers():
#     per_page = int(request.args.get('per_page', 10))
#     page = int(request.args.get('page', 1))
#     offset = (page - 1) * per_page
    
#     # Récupération d'une connexion à la base de données && Création d'un curseur pour exécuter des requêtes SQL
#     cur = get_db().cursor()
#     cur.execute(f"SELECT * FROM client LIMIT {offset}, {per_page}")
#     customers = cur.fetchall()

#     # Compter le nombre total de lignes
#     cur.execute("SELECT COUNT(*) FROM client")
#     total_customers = 1000 #cur.fetchone()[0]
    
#     total_pages = (total_customers // per_page) + (total_customers % per_page > 0)
    
#     return render_template('index.html', customers=customers, page=page, per_page=per_page, total_pages=total_pages)

if __name__ == "__main__":
    app.run(debug=True)
