import requests
import json

API_URL = "https://pub.orcid.org/v3.0/"


def query_api(target_id, save_to="./orcid_record.json"):
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
    for iwork in record["activities-summary"]["works"]["group"]:
        # The summary of the work
        isummary = iwork["work-summary"][0]

        # Extract the DOI
        doi = None
        for ii in isummary["external-ids"]["external-id"]:
            if ii["external-id-type"] == "doi":
                doi = ii["external-id-value"]
                break

        # If the DOI is not found, skip
        if doi is None:
            continue

        doi_list.append(doi)

    return doi_list
