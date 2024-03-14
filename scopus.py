import requests
import json
import pybliometrics.scopus as scopus


def query_api(target_id, save_to="./scopus_record.json"):
    # Get response
    author = scopus.AuthorRetrieval(target_id)
    record = author.get_documents()

    # Save the record to a file
    with open(save_to, "w") as f:
        json.dump(record, f)

    return record


def extract_doi(record):
    return [doc.doi for doc in record]
