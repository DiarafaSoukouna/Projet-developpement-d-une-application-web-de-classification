from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file, session
import os
import time
import bcrypt
from functools import wraps
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
app.secret_key = "deb1ebfbbd96561584a3284b3a77cbb6348968654c2f2aa982cc6922539aa1c7"
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
def files():
    conn = pymysql.connect(host=app.config['MYSQL_HOST'], user=app.config['MYSQL_USER'], password=app.config['MYSQL_PASSWORD'], db=app.config['MYSQL_DB'], port=app.config['MYSQL_PORT'])
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM `files`")
    categories = cursor.fetchall()
    return categories
# 🔑 Déco pour protéger les routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash("Vous devez être connecté pour accéder à cette page.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/home")
@login_required
def home():
    document = files()
    nombre_doc= len(document)
    return render_template("home.html", document=nombre_doc)

@app.route("/documents", methods=['GET'])
@login_required
def documents():
    
    conn = pymysql.connect(host=app.config['MYSQL_HOST'], user=app.config['MYSQL_USER'], password=app.config['MYSQL_PASSWORD'], db=app.config['MYSQL_DB'], port=app.config['MYSQL_PORT'])
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM `categories`")
    categories = cursor.fetchall()
    return render_template('documents.html', categories=categories)


@app.route("/settings")
@login_required
def settings():
    conn = pymysql.connect(host=app.config['MYSQL_HOST'], user=app.config['MYSQL_USER'], password=app.config['MYSQL_PASSWORD'], db=app.config['MYSQL_DB'], port=app.config['MYSQL_PORT'])
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM `users`")
    users = cursor.fetchall()
    return render_template('params.html', users=users)
@app.route("/delete_user/<int:user_id>", methods=['POST'])
@login_required
def delete_user(user_id):
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        flash('Utilisateur supprimé avec succès!', 'success')
    except Exception as e:
        flash(f'Erreur lors de la suppression de l\'utilisateur: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('settings'))

@app.route("/add_user", methods=['POST'])
@login_required
def add_user():
    username = request.form['username']
    email = request.form['email'] 
    password = request.form['password']

    # Hash du mot de passe
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, hashed_password)
        )
        conn.commit()
        flash('Utilisateur ajouté avec succès!', 'success')
    except pymysql.err.IntegrityError:
        flash('Erreur: Cet email est déjà utilisé', 'danger')
    except Exception as e:
        flash(f'Erreur lors de l\'ajout de l\'utilisateur: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('settings'))


@app.route("/chart")
@login_required
def chart():
    return render_template("chart.html")
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
@login_required
def help_page():
    return render_template("help.html")
def allowed_file(filename,):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def insert_file(filename, category):
    conn = pymysql.connect(host=app.config['MYSQL_HOST'], user=app.config['MYSQL_USER'], password=app.config['MYSQL_PASSWORD'], db=app.config['MYSQL_DB'], port=app.config['MYSQL_PORT'])
    cursor = conn.cursor()
    cursor.execute("INSERT INTO files (title, file_path, category_id, uploaded_by ) VALUES (%s, %s, %s, %s)", (filename, 'documents/'+filename, category, None))
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
            # Count occurrences of each word
            # word_counts = {}
            # for word in predictions_list:
            #     word_counts[word] = word_counts.get(word, 0) + 1
            # # Get the most frequent word
            # predictions_list = [max(word_counts.items(), key=lambda x: x[1])[0]]
            
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
@login_required
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


@app.route('/fichier/delete/<int:id>', methods=['GET'])
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

    return redirect('/documents')


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
@app.route("/profil")
@login_required
def profil():
    conn = pymysql.connect(host=app.config['MYSQL_HOST'], user=app.config['MYSQL_USER'], password=app.config['MYSQL_PASSWORD'], db=app.config['MYSQL_DB'], port=app.config['MYSQL_PORT'])
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, username, email FROM users WHERE username = '{session['username']}'")
    user_data = cursor.fetchall()
    # Récupérer les informations de l'utilisateur connecté
    return render_template("profil.html", user=user_data)
        
    

@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')  # Convertir en bytes pour bcrypt
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 🔍 Vérifier si l'utilisateur existe
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if user and bcrypt.checkpw(password, user['password'].encode('utf-8')):  # Comparer les mots de passe
            session['logged_in'] = True
            session['username'] = username
            flash('Connexion réussie !', 'success')
            return redirect(url_for('home'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect', 'danger')
    
    return render_template("login.html")

# 🔑 Déco pour protéger les routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash("Vous devez être connecté pour accéder à cette page.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# 🚪 Déconnexion
@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Vous êtes déconnecté.", "info")
    return redirect(url_for('login'))

@app.route("/update_password", methods=['POST'])
@login_required
def update_password():
    current_password = request.form['current_password'].encode('utf-8')
    new_password = request.form['new_password'].encode('utf-8')
    confirm_password = request.form['confirm_password'].encode('utf-8')
    
    # Vérifier que les nouveaux mots de passe correspondent
    if new_password != confirm_password:
        flash("Les nouveaux mots de passe ne correspondent pas.", "danger")
        return redirect(url_for('profil'))
        
    conn = get_db()
    cursor = conn.cursor()
    
    # Vérifier le mot de passe actuel
    cursor.execute("SELECT password FROM users WHERE username = %s", (session['username'],))
    user = cursor.fetchone()
    
    if not bcrypt.checkpw(current_password, user['password'].encode('utf-8')):
        cursor.close()
        conn.close()
        flash("Le mot de passe actuel est incorrect.", "danger")
        return redirect(url_for('profil'))
    
    # Hasher et mettre à jour le nouveau mot de passe
    hashed_password = bcrypt.hashpw(new_password, bcrypt.gensalt())
    cursor.execute("UPDATE users SET password = %s WHERE username = %s", 
                  (hashed_password.decode('utf-8'), session['username']))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    flash("Votre mot de passe a été mis à jour avec succès!", "success")
    return redirect(url_for('profil'))

if __name__ == "__main__":
    app.run(debug=True)
