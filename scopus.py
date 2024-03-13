import requests
import json
import pybliometrics.scopus as scopus


def query_api(target_id, save_to="./scopus_record.json"):
    # Get response
    author = scopus.AuthorRetrieval(target_id)
    record = author.get_documents()
    return record


def extract_doi(record):
    return record
