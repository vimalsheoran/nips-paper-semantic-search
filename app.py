from flask import Flask, request
import json

import config, query_engine, utils_vectordb, utils_vectorizer

app = Flask(__name__)


@app.route("/test")
def test_app():
	resp = {
		'status': 200,
		'data': 'This app is working.'
	}
	return json.dumps(resp)

@app.route("/init_database")
def initialize_database():
	try:
		utils_vectordb.initialize_database_collection()
		resp = {
			'status': 200,
			'data': 'Initialized vectorstore collections.'
		}	
	except Exception as e:
		resp = {
			'status': 500,
			'data': str(e)
		}
	return json.dumps(resp)



@app.route("/register", methods=['POST'])
def register_paper():
	try:
		data = request.get_json()
		data = json.loads(data)
		
		title = utils_vectorizer.preprocess_input(data['title'])
		abstract = utils_vectorizer.preprocess_input(data['abstract'])

		# Do not consider empty strings
		if (title == "") or (abstract == ""):
			resp = {
				'status': 400,
				'data': "Cannot Register. No Title or Abstract Provided"
			}
			return json.dumps(resp)

		title_embedding = utils_vectorizer.vectorize_query(title)
		abstract_embedding = utils_vectorizer.vectorize_query(abstract)

		metadata = {
			'authors': ",".join(data['authors']),
			'institutions': ",".join(data['institutions']),
			'publishing_year': data['publishing_year']
		}

		utils_vectordb.add_to_collection(config.TITLE_COLLECTION,
										 data['id'],
										 data['title'],
										 title_embedding,
										 metadata)

		utils_vectordb.add_to_collection(config.ABSTRACT_COLLECTION,
										 data['id'],
										 data['abstract'],
										 abstract_embedding,
										 metadata)

		resp = {
			'status': 200,
			'data': "Successfully registered data."
		}
	
	except Exception as e:
		resp = {
			'status': 500,
			'data': str(e)
		}
	return json.dumps(resp)

@app.route("/query", methods=['POST'])
def query():
	try:
		data = request.get_json()
		data = json.loads(data)

		results = query_engine.run_query(data['query_on'], data['query_text'])
		resp = {
			'status': 200,
			'data': results
		}
	except Exception as e:
		resp = {
			'status': 500,
			'data': str(e)
		}
	return json.dumps(resp)

@app.route("/delete", methods=['POST'])
def delete():
	try:
		data = request.get_json()
		data = json.loads(data)

		result = utils_vectordb.remove_ids(data['ids'])
		resp = {
			'status': 200,
			'deleted': result
		}
	except Exception as e:
		resp = {
			'status': 500,
			'data': str(e)
		}
	return json.dumps(resp)

if __name__ == '__main__':
	app.run(debug=True)