import os
import pandas as pd
import numpy as np
import pickle
import sys
import tqdm

lib_path = os.environ['LIB_PATH']
sys.path.append(lib_path)

import config
import utils_vectordb
import utils_vectorizer

print("Loading Datasets...")
authors_file = "../data/authors.csv"
papers_file = "../data/papers.csv"

authors = pd.read_csv(authors_file)
papers = pd.read_csv(papers_file)

authors['first_name'] = authors['first_name'].fillna("")
authors['last_name'] = authors['last_name'].fillna("")
authors['institution'] = authors['institution'].fillna("")

print("Creating Collection in Chroma...")
os.makedirs(config.DB_DIRECTORY, exist_ok=True)
is_initialized = utils_vectordb.initialize_database_collection()
if not is_initialized:
    print("Collections Not Initalized")
print(utils_vectordb.list_collections())

print("Creating Unique IDs for Paper Data...")
papers['paper_unique_id'] = papers['source_id'].astype(str) + "_" + papers['year'].astype(str)

print("Creating Unique IDs for Author Groups...")
diff_source_ids = authors['source_id'].diff().values
IDS = [0]
ID = 0
# No two duplicate sets of source_ids appear together
# Based on the difference of source_id we can determine 
# when a set of authors begins and ends.
for i in range(1, authors.shape[0]):
    diff = diff_source_ids[i]
    if diff != 0:
        ID += 1
    IDS.append(ID)
authors['author_unique_id'] = IDS

print("Combining Author and Institution Names into a single entry...")
authors_singleton = []

for uid, author_data in authors.groupby('author_unique_id'):
    author_data['full_name'] = author_data['first_name'] + " " + author_data['last_name']
    source_id = author_data['source_id'].iloc[0]
    authors_singleton.append({
        'author_unique_id': uid,
        'source_id': source_id,
        'authors': author_data['full_name'].tolist(),
        'institutions': [x for x in author_data['institution'].tolist() if type(x) == str] # Simple hack to remove NaN values
    })
authors_singleton = pd.DataFrame(authors_singleton)

print("Assigning Primary Key to Authors and Papers data...")
# Create two mappings.
# First is whether a paper's Unique ID has been assigned or not.
# Second is which author Unique ID has been assigned to which paper unique ID.
paper_uid_assigned = {x: False for x in papers['paper_unique_id'].values}
authors_uid_values = {x: None for x in authors_singleton['author_unique_id'].unique()}

# Group author's data on unique_ids
for i, r in authors_singleton.iterrows():
    source_id = r['source_id']
    author_uid = r['author_unique_id']
    papers_data = papers[papers['source_id'] == source_id].sort_values(by='year', ascending=True)
    # This is a set of all available paper unique IDs sorted on their order of appearance
    available_paper_uids = papers_data['paper_unique_id'].unique()
    # For all available paper unique ids,
    for paper_uid in available_paper_uids:
        # Check if that paper unique id has already being assigned to a group of author or not.
        if not paper_uid_assigned[paper_uid]:
            # If not assign it to the author group,
            # and mark the paper unique id as assigned.
            paper_uid_assigned[paper_uid] = True
            authors_uid_values[author_uid] = paper_uid
            break


authors_singleton['paper_unique_id'] = authors_singleton['author_unique_id'].apply(lambda x: authors_uid_values[x])   

print("Merging authors data with papers...")
papers = papers.merge(authors_singleton, how='left', on='paper_unique_id')
papers['nan_title'] = papers['title'].isna()
papers['nan_abstract'] = papers['abstract'].isna()
# Drop data where both title and abstract is nan
papers = papers[~(papers['nan_title'] & papers['nan_abstract'])]

print("Sampling at random and populating the database...")
sample_set = papers.sample(frac=0.3)

print("Registering Samples...")
for i, r in tqdm.tqdm(sample_set.iterrows()):
    try:

        title = utils_vectorizer.preprocess_input(r['title'])
        abstract = utils_vectorizer.preprocess_input(r['abstract'])

        # Do not consider empty strings
        if (title == "") or (abstract == ""):
            continue

        title_embedding = utils_vectorizer.vectorize_query(title)
        abstract_embedding = utils_vectorizer.vectorize_query(abstract)

        metadata = {
            'authors': ",".join(r['authors']),
            'institutions': ",".join(r['institutions']),
            'publishing_year': r['year']
        }

        utils_vectordb.add_to_collection(config.TITLE_COLLECTION,
                                         r['paper_unique_id'],
                                         r['title'],
                                         title_embedding,
                                         metadata)

        utils_vectordb.add_to_collection(config.ABSTRACT_COLLECTION,
                                         r['paper_unique_id'],
                                         r['abstract'],
                                         abstract_embedding,
                                         metadata)

        is_registered = utils_vectorizer.register_paper_data({
            'id': r['paper_unique_id'],
            'authors': r['authors'],
            'institutions': r['institutions'],
            'publishing_year': r['year'],
            'title': r['title'],
            'abstract': r['abstract']
        })
    except Exception as e:
        # print(e)
        continue

print("Done!")  