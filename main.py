import os
from pathlib import Path
import pickle

pybliometrics_cfg = str(Path("./pybliometrics.cfg").resolve())
os.environ['PYB_CONFIG_FILE'] = pybliometrics_cfg
print(f"Using pybliometrics config file: {pybliometrics_cfg}")

import orcid
import scopus
import doi
import pretty
from importlib import reload

# %% Specify IDs
orcid_id = "0000-0002-7108-637X"
scopus_id = "7005289082"
record_name = "EnricoZio"

xlsx_loc = f"./{record_name}.xlsx"
md_loc = f"./{record_name}.md"
html_loc = f"./{record_name}.html"

# %% Retrieve ORCID data
print("Retrieving ORCID entries from API...")
orcid_record = orcid.query_api(orcid_id, save_to=f"./ORCID-{record_name}.json")
orcid_doi_list = orcid.extract_doi(orcid_record)

print(f"    Retrieved {len(orcid_doi_list)} DOIs from ORCID.")

# %% Retrieve Scopus data
print("Retrieving Scopus entries from API...")
record = scopus.query_api(scopus_id, save_to=f"./Scopus-{record_name}.json")
scopus_doi_list = scopus.extract_doi(record)

print(f"    Retrieved {len(scopus_doi_list)} DOIs from Scopus.")

# %% Combine the lists
reload(doi)
doi_list = doi.merge_doi_lists(orcid_doi_list, scopus_doi_list)

# %% Fetch metadata for each DOI
print("Fetching metadata for each DOI...")
database = doi.process_doi_list(doi_list, database_loc=xlsx_loc)

print("     Finished fetching reference data!")

# Save the data to an xlsx file
database.to_excel(xlsx_loc)
print(f"    Saved to {xlsx_loc}")

# %% Convert into a markdown string
print("Converting data to markdown string...")
mds = pretty.df_to_markdown(database, save_to=md_loc)
print(f"    Saved to {md_loc}")

# %% Convert markdown to HTML
print("Converting markdown to HTML...")
html = pretty.markdown_to_html(mds, save_to=html_loc)
print(f"     Saved to {html_loc}")

# %% Print the database summary
print("Database types summary:")
print(database.groupby("type").size())

# %% Get journals
print("Getting journals...")
journal_types = ("journal-article",
                 "proceedings-article",
                 "posted-content",
                 "book-chapter")
journals = database[database["type"].isin(journal_types)]

# Save to a file
journals.to_excel(f"{record_name}-journals.xlsx")

# HTML
journals_mds = pretty.df_to_markdown(journals, save_to=f"{record_name}-journals.md")
pretty.markdown_to_html(journals_mds, save_to=f"{record_name}-journals.html")

print("     Finished getting journals!")

# %% Get books
print("Getting books...")

book_types = ("book",)
books = database[database["type"].isin(book_types)]

# Save to a file
books.to_excel(f"{record_name}-books.xlsx")

# HTML
books_mds = pretty.df_to_markdown(books, save_to=f"{record_name}-books.md")
pretty.markdown_to_html(books_mds, save_to=f"{record_name}-books.html")

print("     Finished getting books!")



