import numpy as np
import pandas as pd
import string
import re
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.stem import WordNetLemmatizer
nltk.download('wordnet')
import pickle

base_dir = 'backend'

with open(f'{base_dir}/models/count_vectorizer.pkl', 'rb') as file:
    countVectorizer = pickle.load(file)

with open(f'{base_dir}/models/document_classifier_model.pkl', 'rb') as file:
    load_model = pickle.load(file)

###On définit une fonction qui supprime les ponctuations
def remove_punctuation(text):
    return ''.join([t for t in text if t not in string.punctuation])

###On définit une fonction qui applique la tokenisation sur nos données.
def tokenizeText(text):
    return ' '.join(word for word in re.split('\W+', text.lower()))

###On définit une fonction qui enlève les stopwords (Anglais et Français)
def applyStopwords(text):
    french_stopwords = stopwords.words('french')
    english_stopwords = stopwords.words('english')
    return ' '.join(word for word in text.split() if (word not in english_stopwords) and (word not in french_stopwords))

###On applique la lemmatisation sur nos données
def applyLemmatization(text):
    lemmatizer = WordNetLemmatizer()
    return ' '.join(lemmatizer.lemmatize(word) for word in text.split())

def find_most_frequent_item(arr):
  unique, counts = np.unique(arr, return_counts=True)
  return unique[np.argmax(counts)]

def predict_file_label(file_content: list[str]):
    df = pd.DataFrame(data={'content': file_content})

    ###Suppression des doublons
    df.drop_duplicates(inplace = True)

    ###Suppression de tous les espaces (' ', \n, ...)
    df['content'] = df['content'].str.strip().replace('', np.nan)
    df.dropna(inplace=True)

    ###Suppression des ponctuations
    df['cleaned_content'] = df['content'].apply(lambda x: remove_punctuation(x))

    ###On applique la tokenisation
    df['cleaned_content'] = df['cleaned_content'].apply(lambda x: tokenizeText(x))

    ###On applique les stopwords
    df['cleaned_content'] = df['cleaned_content'].apply(lambda x: applyStopwords(x))

    ###On applique la lemmatisation
    df["cleaned_content"] = df["cleaned_content"].apply(lambda x: applyLemmatization(x))

    ###On va transformer nos données (textuelles) en vecteur (utiliser transform sur les nouvelles données)
    cleaned_content_vectorized= countVectorizer.transform(df['cleaned_content'])

    X = cleaned_content_vectorized.toarray()
    y_predict = load_model.predict(X)

    return find_most_frequent_item(y_predict)