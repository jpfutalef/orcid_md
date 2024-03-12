import pandas as pd
import requests
from pathlib import Path
from rich.progress import Progress
import json
import markdown

# %% Specify IDs
orcid_id = "0000-0002-7108-637X"
scopus_id = "7103080737"

# %% Retrieve ORCID data
print("Retrieving ORCID entries from API...")

# %% Retrieve Scopus data
print("Retrieving Scopus entries from API...")

# %% Check if the xls file exists
print("Checking if the xlsx file exists...")

if Path(xlsx_loc).exists():
    print(f"    FOUND! {xlsx_loc} will be used to check if DOI is already in the list.")
    df = pd.read_excel(xlsx_loc, index_col=0)
    data = df.to_dict(orient="index")

else:
    print(f"    NOT FOUND. New file will be created at {xlsx_loc}")
    data = {}

# %% Obtain each work's metadata using the DOI
print("Fetching reference data...")

with Progress() as progress:
    bar = progress.add_task("Fetching DOI data...",
                            total=len(orcid_record["activities-summary"]["works"]["group"]))

    for iwork in orcid_record["activities-summary"]["works"]["group"]:
        # The summary of the work
        isummary = iwork["work-summary"][0]

        # Extract the DOI
        doi = None
        for ii in isummary["external-ids"]["external-id"]:
            if ii["external-id-type"] == "doi":
                doi = ii["external-id-value"]
                break

        # Update the progress bar. Ensure fixed width for the description
        description = f"    Processing DOI: {doi}".ljust(50)
        progress.update(bar, advance=1, description=description)

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

# %% Convert the data into a DataFrame
print("Converting data to a DataFrame...")
df = pd.DataFrame(data).T

# Save the data to an xlsx file
df.to_excel(xlsx_loc, index=False)
print(f"    Saved to {xlsx_loc}")

# %% Convert into a markdown string
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
# %% Convert markdown to HTML
print("Converting markdown to HTML...")

html = markdown.markdown(mds)
with open(html_loc, "w", encoding='utf-8') as f:
    f.write(html)

print("Finished!")
