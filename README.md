# Introduction
This repository contains the code for the blog written [here](https://dev.to/vimalsheoran/applied-semantic-search-search-for-research-papers-5nk?preview=a6b5318b02b5cdba0dcaf4b48c39a871ffe6b02c5d69327830859d26b31cfcb49ec794168846a11030fe987f5da2c5d4499a8dab53935ff28657ac25). You can setup this repository and run the application inside it to spin up your own search engine for searching through academic paper. The original implementation here searches on the paper data from the [Papers of the NIPS Conference](https://www.kaggle.com/datasets/rowhitswami/nips-papers-1987-2019-updated). You can change the code to make it work on your own data or change the implementation to try out different embedding/querying and retrieval methods.

**For a detailed information about the implementation visit the blog [here](https://dev.to/vimalsheoran/applied-semantic-search-search-for-research-papers-5nk?preview=a6b5318b02b5cdba0dcaf4b48c39a871ffe6b02c5d69327830859d26b31cfcb49ec794168846a11030fe987f5da2c5d4499a8dab53935ff28657ac25)**

# Setting Up
In order to setup the repostiory please follow the steps given below.
1. Setup and activate a virtual environment. Don't know how to setup a virtual environment? Follow the steps mentioned [here](https://docs.python.org/3/library/venv.html).
2. Install the required libraries and packages using the following command
	`pip install -r requirements.txt`
3. Once you've installed the requirements, you would need to download data that helps the NLTK library to do language processing tasks. To do this navigate to the folder `initializer_scripts` and run the following command,
	`python download_nltk_corpora.py`
4. Next we initalize some data in our vector database to begin working. Navigate to the `initializer_sripts` folder and run the following command,
	`LIB_PATH=/path/to/your/local/nips-paper-semantic-search python populate_vectorstore.py`
	*Please ensure to provide the* `LIB_PATH` *environment variable which contains the path to the repository you downloaded in order to run the script.*
5. Now we can run the application server by running
	`python app.py`

# Exploring with `eda.ipynb`
You will find a Jupyter notebook in the repository called `eda.ipynb` you can explore the notebook to see the kind of data we have and also explore the available APIs that the application server provides to interact with the data.

# APIs
There are 4 APIs in the application,

### Test Application Status

This API tests to see if the application is running or not
**Usage**:
*Path*: `http://localhost:5000/test`
*Method*: GET
*Parameters*: None
*Response*: ```json
{
	'data': 'This app is working.', 
	'status': 200
}
```

### Register New Paper Data

Register data for a new paper in the vector store.
**Usage**:
*Path*: `http://localhost:5000/register`
*Method*: POST
*Request Type*: JSON
*Request*: ```json
{
	'id': 0,
    'title': "A sample paper title.",
    'abstract': "A sample paper abstract",
    'authors': ["Jon Doe", "Don Joe"],
    'institutions': ["Dunder and Mufflin", "Munder and Dufflin"],
    'publishing_year': 2023
}
```
*Response*: ```json
{
	'data': 'Successfully registered data.', 
	'status': 200
}
```

### Query Database

Query data present in the vector database. The user can select whether to run the query on the *title* of the paper or on the *abstract* of the paper. The application by default returns top 10 results based on the best match.
**Usage**:
*Path*: `http://localhost:5000/query`
*Method*: POST
*Request Type*: JSON
*Request*: ```json
{
    'query_text': "Sample paper",
    'query_on': "title/abstract"
}
```
*Response*: ```json
{
	'data': [
				{
					'abstract': 'A sample paper abstract',
		            'authors': 'Jon Doe,Don Joe',
		            'id': '0',
		            'institutions': 'Dunder and Mufflin,Munder and Dufflin',
		            'publishing_year': 2023,
		            'title': 'A sample paper title.'
		        },
          	    {
          	    	'abstract': 'Thompson sampling has emerged as an effective '
                       'heuristic for a broad range of online decision '
                       'problems. In its basic form, the algorithm requires '
                       'computing and sampling from a posterior distribution '
                       'over models, which is tractable only for simple '
                       'special cases. This paper develops ensemble sampling, '
                       'which aims to approximate Thompson sampling while '
                       'maintaining tractability even in the face of complex '
                       'models such as neural networks. Ensemble sampling '
                       'dramatically expands on the range of applications for '
                       'which Thompson sampling is viable. We establish a '
                       'theoretical basis that supports the approach and '
                       'present computational results that offer further '
                       'insight.',
           			'authors': 'Xiuyuan Lu,Benjamin Van Roy',
           			'id': '1854_2017',
           			'institutions': 'Stanford University,Stanford University',
           			'publishing_year': 2017,
           			'title': 'Ensemble Sampling'
           		}...
           ]
 }
```

### Delete from Database

Deletion can be performed from the database by providing the IDs of the data items which are to be removed.
**Usage**:
*Path*: `http://localhost:5000/delete`
*Method*: POST
*Request Type*: JSON
*Request*: ```json
{
	'ids': ['0']
}
```
*Response*: ```json
{
	'deleted': True, 
	'status': 200
}
```

# Application Configurations
The `config.py` files contains variables which control the configurations for the application and the database. You can alter these configurations to customize the application for yourself.

**For a detailed information about the implementation visit the blog [here](https://dev.to/vimalsheoran/applied-semantic-search-search-for-research-papers-5nk?preview=a6b5318b02b5cdba0dcaf4b48c39a871ffe6b02c5d69327830859d26b31cfcb49ec794168846a11030fe987f5da2c5d4499a8dab53935ff28657ac25)**
