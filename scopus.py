import requests
import json

API_URL = "https://pub.orcid.org/v3.0/"


def query_api(target_id, save_to="./scopus_record.json"):
    # Get response
    response = requests.get(
        url=requests.utils.requote_uri(API_URL + target_id),
        headers={"Accept": "application/json"},
    )

    response.raise_for_status()
    record = response.json()

    # Save the record to a file
    with open(save_to, "w") as f:
        json.dump(record, f)

    return record


def extract_doi(record):
    doi_list = []
    return doi_list
