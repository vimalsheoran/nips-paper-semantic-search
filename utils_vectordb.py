import chromadb
from chromadb.config import Settings
import config

client = chromadb.Client(Settings(persist_directory=config.DB_DIRECTORY, chroma_db_impl='duckdb+parquet'))


def initialize_database_collection():
	client.create_collection(name=config.TITLE_COLLECTION,
							 metadata={"hnsw:space": config.DISTANCE_MEASURE})
	client.persist()

	client.create_collection(name=config.ABSTRACT_COLLECTION,
							 metadata={"hnsw:space": config.DISTANCE_MEASURE})
	return client.persist()


def list_collections():
	return client.list_collections()


def get_length():
	collection = client.get_collection(name='paper-titles')
	print(len(collection.peek()['embeddings'][0]))


def add_to_collection(collection_name, _id, document, embedding, metadata):
	collection = client.get_collection(name=collection_name)

	collection.add(
		documents=[document],
		metadatas=[metadata],
		ids=[str(_id)],
		embeddings=[embedding]
	)

	persisted = client.persist()


def query_collection(collection_name, embedding):
	collection = client.get_collection(name=collection_name)
	query_results = collection.query(query_embeddings=[embedding],
								 	 n_results=config.MAX_RESULTS_TO_RETURN)
	return query_results


def fetch_from_ids(collection_type, ids=None):
	if collection_type == 'title':
		collection_name = config.TITLE_COLLECTION
	else:
		collection_name = config.ABSTRACT_COLLECTION
	collection = client.get_collection(name=collection_name)
	query_results = collection.get(ids=ids)
	return query_results


def remove_ids(ids):
	title_collection = client.get_collection(name=config.TITLE_COLLECTION)
	abstract_collection = client.get_collection(name=config.ABSTRACT_COLLECTION)
	title_collection.delete(ids=ids)
	abstract_collection.delete(ids=ids)
	return client.persist()