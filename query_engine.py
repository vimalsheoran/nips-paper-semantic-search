import pprint
import config, utils_vectordb, utils_vectorizer


def convert_to_records(matches, match_type='title'):
	match_ids = matches['ids'][0]
	additional_info_type = 'abstract' if match_type == 'title' else 'title'
	match_metadata = matches['metadatas'][0]
	match_documents = matches['documents'][0]
	additional_information = utils_vectordb.fetch_from_ids(additional_info_type, match_ids)
	addn_info_ids, addn_info_docs = additional_information['ids'], additional_information['documents']
	addn_info_map = {_id: doc for _id, doc in zip(addn_info_ids, addn_info_docs)}
	records = []
	for i in range(len(match_ids)):
		records.append({
			'id': match_ids[i],
			match_type: match_documents[i],
			additional_info_type: addn_info_map[match_ids[i]],
			**match_metadata[i]
		})
	return records


def run_query(query_on, query_text):
	query_embedding = utils_vectorizer.vectorize_query(query_text)
	if query_on == 'title':
		matches = utils_vectordb.query_collection(config.TITLE_COLLECTION, query_embedding)
	else:
		matches = utils_vectordb.query_collection(config.ABSTRACT_COLLECTION, query_embedding)
	records = convert_to_records(matches, query_on)
	return records