import pandas as pd
import requests
import json
from rich.progress import Progress


def merge_doi_lists(*args):
    """
    Merge multiple lists of DOIs into one list.
    :param args: doi_list1, doi_list2, ...
    """
    out = []
    for arg in args:
        out.extend(arg)
    return out


def process_doi_list(doi_list, database_loc="./publication_record.xlsx"):
    """
    Reads each DOI in the list, gets the metadata, and adds it to the database.
    There's the possibility to pass a database to check if the DOI is already in the database.
    :param doi_list: list of DOIs
    :param database: DataFrame with the database
    """
    try:
        database = pd.read_excel(database_loc, index_col=0)
        data = database.to_dict(orient="index")
        print(f"    FOUND! {database_loc} will be used to check if DOI is already in the list.")

    except FileNotFoundError:
        print(f"    NOT FOUND. New file will be created at {database_loc}")
        data = {}

    with Progress() as progress:
        bar = progress.add_task("Fetching DOI data...",
                                total=len(doi_list))
        for doi in doi_list:
            # Update the progress bar. Ensure fixed width for the description
            description = f"    Processing DOI: {doi}".ljust(50)
            progress.update(bar, advance=1, description=description)

            # If the DOI is already in the list, skip
            if doi in data:
                continue

            # Fetch the metadata
            doi_metadata = get_doi_json(doi)
            data[doi] = process_doi_metadata(doi, doi_metadata)

    return pd.DataFrame.from_dict(data).T.sort_values("year", ascending=False)


# A function to fetch metadata for a given DOI
def get_doi_json(doi, fmt="dict", **kwargs):
    """
    Fetch metadata for a given DOI.
    :param doi: str DOI
    :param fmt: str, optional
        Desired metadata format. Can be 'dict' or 'bibtex'.
        Default is 'dict'.
    :param kwargs: Additional keyword arguments are passed to `json.loads()
    """
    # Parse args and setup the server response we want.
    accept_type = "application/"
    if fmt == "dict":
        accept_type += "citeproc+json"
    elif fmt == "bibtex":
        accept_type += "x-bibtex"
    elif fmt == "reference":
        accept_type = "text/x-bibliography; style=apa"
    else:
        raise ValueError(f"Unrecognized `fmt`: {fmt}")

    # Request data from server.
    url = "https://dx.doi.org/" + str(doi)
    header = {"accept": accept_type}
    r = requests.get(url, headers=header)

    # Format metadata if server response is good.
    out = None
    if r.status_code == 200:
        if fmt == "dict":
            out = json.loads(r.text, **kwargs)
        else:
            out = r.text
    return out


def process_doi_metadata(doi, meta):
    """
    Reads the metadata from the doi json
    :param doi: str DOI
    :param meta: json with the metadata
    :return: dictionary with the metadata
    """
    # Extract the data
    try:
        title = meta["title"]
        references_count = meta["references-count"]
        year = meta["issued"]["date-parts"][0][0]
        url = meta["URL"]
        doc_type = meta["type"]

        # Create authors list with links to their ORCIDs
        authors = meta["author"]
        autht = []
        for author in authors:
            name = f"{author['family']}, {author['given'][0]}."
            if "holdgraf" in author["family"].lower():
                name = f"**{name}**"
            if "ORCID" in author:
                autht.append(f"[{name}]({author['ORCID']})")
            else:
                autht.append(name)
        autht = "; ".join(autht)

        journal = meta["publisher"]

        url_doi = url.split("//", 1)[-1]
        reference = f"{autht} ({year}). **{title}**. {journal}. [{url_doi}]({url})"

        # Setup this entry
        work_data = {
            "title": title,
            "authors": autht,
            "year": year,
            "journal": journal,
            "citation_count": references_count,
            "url_doi": url_doi,
            "url": url,
            "reference": reference,
            "type": doc_type,
        }

    except KeyError as e:
        print(f"Failed to process DOI: {doi}")
        work_data = {}

    return work_data
