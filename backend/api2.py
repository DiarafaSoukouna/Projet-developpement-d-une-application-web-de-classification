import numpy as np
import pandas as pd
import string
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import pickle

# nltk.download('stopwords')
# nltk.download('wordnet')

class DocumentProcessor:
    def __init__(self, model_path, vectorizer_path):
        """
        Initialise le processeur de documents.
        model_path : Chemin vers le fichier pickle du modèle entraîné.
        vectorizer_path : Chemin vers le fichier pickle du vectorizer.
        """
        with open(model_path, 'rb') as model_file:
            self.model = pickle.load(model_file)
        with open(vectorizer_path, 'rb') as vectorizer_file:
            self.vectorizer = pickle.load(vectorizer_file)
        self.french_stopwords = stopwords.words('french')
        self.english_stopwords = stopwords.words('english')
        self.lemmatizer = WordNetLemmatizer()

    @staticmethod
    def remove_punctuation(text):
        """Supprime les ponctuations d'un texte."""
        return ''.join([t for t in text if t not in string.punctuation])

    @staticmethod
    def tokenize_text(text):
        """Tokenise un texte."""
        return ' '.join(word for word in re.split(r'\W+', text.lower()))

    def apply_stopwords(self, text):
        """Supprime les stopwords (français et anglais) d'un texte."""
        return ' '.join(
            word for word in text.split() 
            if (word not in self.english_stopwords) and (word not in self.french_stopwords)
        )

    def apply_lemmatization(self, text):
        """Applique la lemmatisation sur un texte."""
        return ' '.join(self.lemmatizer.lemmatize(word) for word in text.split())

    def process_file(self, file_path):
        """
        Traite un fichier pour en extraire les caractéristiques nettoyées et vectorisées.
        file_path : Chemin vers le fichier à traiter.
        """
        # Lecture du contenu du fichier
        file_content = []
        with open(file_path, 'r', encoding='utf8') as file_reader:
            for line in file_reader:
                file_content.append(line.strip())

        # Création d'un DataFrame
        df = pd.DataFrame(data={'content': file_content})

        # Suppression des doublons et des lignes vides
        df.drop_duplicates(inplace=True)
        df['content'] = df['content'].str.strip().replace('', np.nan)
        df.dropna(inplace=True)

        # Application des étapes de nettoyage et de prétraitement
        df['cleaned_content'] = df['content'].apply(self.remove_punctuation)
        df['cleaned_content'] = df['cleaned_content'].apply(self.tokenize_text)
        df['cleaned_content'] = df['cleaned_content'].apply(self.apply_stopwords)
        df['cleaned_content'] = df['cleaned_content'].apply(self.apply_lemmatization)

        # Transformation en vecteur
        cleaned_content_vectorized = self.vectorizer.transform(df['cleaned_content'])

        return cleaned_content_vectorized.toarray()

    def predict_from_file(self, file_path):
        """
        Prédit les classes pour le contenu d'un fichier.
        file_path : Chemin vers le fichier à traiter.
        """
        processed_data = self.process_file(file_path)
        predictions = self.model.predict(processed_data)
        return predictions