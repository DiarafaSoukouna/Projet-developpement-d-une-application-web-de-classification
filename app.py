from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
import os
import time
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename

# from '/backend/api2.py' import DocumentProcessor
from backend.api2 import DocumentProcessor
import pymysql
import numpy as np
ALLOWED_EXTENSIONS = {'docs', 'txt', 'doc'}
app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Répertoire contenant app.py
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'documents')  # Chemin absolu pour le dossier 'documents'
# Configuration de la base de données MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Utilisateur MySQL
app.config['MYSQL_PASSWORD'] = ''  # Mot de passe MySQL
app.config['MYSQL_DB'] = 'danaya_file' 
app.config['MYSQL_PORT'] = 3306
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
        port=app.config['MYSQL_PORT'],
        cursorclass=pymysql.cursors.DictCursor
)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/documents", methods=['GET'])
def documents():
    
    conn = pymysql.connect(host=app.config['MYSQL_HOST'], user=app.config['MYSQL_USER'], password=app.config['MYSQL_PASSWORD'], db=app.config['MYSQL_DB'], port=app.config['MYSQL_PORT'])
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM `categories`")
    categories = cursor.fetchall()
    return render_template('documents.html', categories=categories)

@app.route("/settings")
def settings():
    return render_template("settings.html")
@app.route("/category/<category_id>", methods=['GET'])
def category(category_id):
    conn = pymysql.connect(host=app.config['MYSQL_HOST'], user=app.config['MYSQL_USER'], password=app.config['MYSQL_PASSWORD'], db=app.config['MYSQL_DB'], port=app.config['MYSQL_PORT'])
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM `files` WHERE `category_id` =  {category_id}")
    files = cursor.fetchall()
    cursor.execute(f"SELECT * FROM `categories` WHERE `id` =  {category_id}")
    category_name = cursor.fetchone()[2]

    return render_template('files.html', files=files, category_name=category_name)

@app.route("/help")
def help_page():
    return render_template("help.html")
def allowed_file(filename,):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def insert_file(filename, category):
    conn = pymysql.connect(host=app.config['MYSQL_HOST'], user=app.config['MYSQL_USER'], password=app.config['MYSQL_PASSWORD'], db=app.config['MYSQL_DB'], port=app.config['MYSQL_PORT'])
    cursor = conn.cursor()
    cursor.execute("INSERT INTO files (title, file_path, category_id, uploaded_by ) VALUES (%s, %s, %s, %s)", (filename, 'documents/'+filename, category, 1))
    conn.commit()
    cursor.close()
    conn.close()

@app.route('/upload', methods=['POST', 'GET'])
def file_upload():
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier détecté dans la requête'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400

    if file and allowed_file(file.filename):
        filename = f'{round(time.time())}'+(secure_filename(file.filename))
        
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        file.save(save_path)
        print(f"Fichier sauvegardé à : {save_path}")

        try:
            processor = DocumentProcessor(model_path='backend/models/document_classifier_model.pkl', vectorizer_path='backend/models/count_vectorizer.pkl')
            predictions = processor.predict_from_file(save_path)
            print(f"Prédictions : {predictions}")
            # Convert predictions to a list for JSON serialization
            predictions_list = predictions.tolist() if isinstance(predictions, np.ndarray) else predictions
            categories = {
                'tech': 1,
                'politics': 2,
                'sport': 3,
                'business': 4,
                'entertainment': 5,
            }
            category = categories[predictions_list[0]]
            insert_file(filename, category)

            return jsonify({'message': 'Fichier téléchargé avec succès', 'predictions': predictions_list, 'save_path': save_path, 'category': category}), 200
            # return redirect('/documents')
        except Exception as e:
            print(f"Erreur lors de la prédiction : {e}")
            return jsonify({'error': 'Erreur lors de la prédiction'}), 500
   

        # return jsonify({'message': 'Fichier téléchargé avec succès', "predictions": predictions, "save_path": save_path}), 200
      

    return jsonify({'error': 'Extension de fichier non autorisée'}), 400

def get_fichier_from_db(file_id):

        conn = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            db=app.config['MYSQL_DB'],
            port=app.config['MYSQL_PORT']
        )
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM `files` WHERE `id` = %s", (file_id,))
        fichier = cursor.fetchone()
        cursor.close()
        conn.close()
        return fichier


@app.route('/fichier/<int:id>', methods=['GET'])
def afficher_fichier(id):
    fichier = get_fichier_from_db(id)
    if not fichier:
        return jsonify({'error': 'Fichier introuvable'}), 404

    chemin_complet = os.path.join(app.config['UPLOAD_FOLDER'], fichier['title'])

    try:
            with open(chemin_complet, 'r', encoding='utf-8') as f:
                contenu = f.read()
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la lecture du fichier : {e}'}), 500
    
    nom=fichier['title']
    contenu=contenu
    id=fichier['id']
    category=fichier['category_id']

    return render_template("modal.html",nom=nom,contenu=contenu, id=id, category=category)


@app.route('/fichier/delete/<int:id>', methods=['DELETE'])
def supprimer(id):
    fichier = get_fichier_from_db(id)
    if not fichier:
        return jsonify({'error': 'Fichier introuvable'}), 404

    chemin_complet = os.path.join(app.config['UPLOAD_FOLDER'], fichier['title'])

    try:
        os.remove(chemin_complet)
    except FileNotFoundError:
        return jsonify({'error': 'Le fichier sur le disque est introuvable'}), 404
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la suppression du fichier : {e}'}), 500

    try:
        conn = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            db=app.config['MYSQL_DB'],
            port=app.config['MYSQL_PORT']
        )
        cursor = conn.cursor()
        cursor.execute("DELETE FROM `files` WHERE `id` = %s", (id,))
        conn.commit()
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la suppression dans la base de données : {e}'}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({'message': 'Fichier supprimé avec succès'}), 200


@app.route('/fichier/export/<int:id>', methods=['GET'])
def exporter_fichier(id):
    fichier = get_fichier_from_db(id)
    if not fichier:
        return jsonify({'error': 'Fichier introuvable'}), 404

    chemin_complet = os.path.join(app.config['UPLOAD_FOLDER'], fichier['file_path'])
    if not os.path.exists(chemin_complet):
        return jsonify({'error': 'Le fichier sur le disque est introuvable'}), 404

    try:
        return send_file(chemin_complet, as_attachment=True)
    except Exception as e:
        return jsonify({'error': f'Erreur lors de l\'exportation du fichier : {e}'}), 500



if __name__ == "__main__":
    app.run(debug=True)
