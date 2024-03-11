import pandas as pd
import requests
from pathlib import Path
from rich import progress
import json

#%% ORCID data
orcid_id = "0000-0002-7108-637X"
ORCID_RECORD_API = "https://pub.orcid.org/v3.0/"

json_loc = f"./ORCID-{orcid_id}.json"
xlsx_loc = f"./ORCID-{orcid_id}.xlsx"
md_loc = f"./ORCID-{orcid_id}.md"
#%% Retrieve ORCID data
print("Retrieving ORCID entries from API...")

response = requests.get(
    url=requests.utils.requote_uri(ORCID_RECORD_API + orcid_id),
    headers={"Accept": "application/json"},
)
response.raise_for_status()
orcid_record = response.json()

# Save the record to a file
with open(json_loc, "w") as f:
    json.dump(orcid_record, f)

# Message
person_name_dict = orcid_record["person"]["name"]
given_name = person_name_dict["given-names"]["value"]
family_name = person_name_dict["family-name"]["value"]
print(f"     Retrieved ORCID record for {given_name} {family_name}...")
print(f"     Found {len(orcid_record['activities-summary']['works']['group'])} works")
print(f"     Saved to {json_loc}")

#%% A function to fetch metadata for a given DOI
def fetchmeta(doi, fmt="reference", **kwargs):
    """Fetch metadata for a given DOI.

    Parameters
    ----------
    doi : str
    fmt : str, optional
        Desired metadata format. Can be 'dict' or 'bibtex'.
        Default is 'dict'.
    **kwargs :
        Additional keyword arguments are passed to `json.loads()` if `fmt`
        is 'dict' and you're a big JSON nerd.

    Returns
    -------
    out : str or dict or None
        `None` is returned if the server gives unhappy response. Usually
        this means the DOI is bad.

    Examples
    --------
    >>> fetchmeta('10.1016/j.dendro.2018.02.005')
    >>> fetchmeta('10.1016/j.dendro.2018.02.005', 'bibtex')

    References
    ----------
    https://www.doi.org/hb.html
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

#%% Check if the xls file exists
print("Checking if the xlsx file exists...")

if Path(xlsx_loc).exists():
    print(f"    FOUND! {xlsx_loc} will be used to check if DOI is already in the list.")
    df = pd.read_excel(xlsx_loc)
    data = df.to_dict(orient="index")

else:
    print(f"    NOT FOUND. New file will be created at {xlsx_loc}")
    data = {}

#%% Obtain each work's metadata using the DOI
print("Fetching reference data...")
for iwork in progress.track(
    orcid_record["activities-summary"]["works"]["group"], "Fetching reference data..."
):
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

    # If the DOI is already in the list, skip
    if doi in data:
        continue

    # Extract the data
    try:
        meta = fetchmeta(doi, fmt="dict")
        doi_url = meta["URL"]
        title = meta["title"]
        references_count = meta["references-count"]
        year = meta["issued"]["date-parts"][0][0]
        url = meta["URL"]

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
            "reference": reference
        }

    except KeyError as e:
        print(f"Failed to process DOI: {doi}")

        work_data = {}

    # Add to the data
    data[doi] = work_data

print("Finished fetching reference data...")

#%% Convert the data into a DataFrame
print("Converting data to a DataFrame...")
df = pd.DataFrame(data).T

# Save the data to an xlsx file
df.to_excel(xlsx_loc, index=False)
print(f"    Saved to {xlsx_loc}")

#%% Convert into a markdown string
print("Converting data to markdown string...")
md = []
for year, items in df.groupby("year", sort=False):
    md.append(f"## {year}")
    for _, item in items.iterrows():
        md.append(item["reference"])
        md.append("")
    md.append("")
mds = "\n".join(md)

# Write to a markdown file
with open(md_loc, "w", encoding='utf-8') as f:
    f.write(mds)
print(f"    Saved to {md_loc}")

print("Finished!")