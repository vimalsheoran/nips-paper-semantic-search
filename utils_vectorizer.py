import chromadb
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sentence_transformers import SentenceTransformer

import config
import utils_vectordb

english_stopwords = stopwords.words('english')
wordnet_lemmatizer = WordNetLemmatizer()
embedding_model = SentenceTransformer(config.PRODUCTION_EMBEDDING_MODEL)

def preprocess_input(ip):
	if type(ip) is not str:
		return ""
	ip = ip.lower().split(" ")
	ip = [wordnet_lemmatizer.lemmatize(i) for i in ip if i not in english_stopwords]
	return " ".join(ip)

def vectorize_query(query):
	return embedding_model.encode(query).tolist()