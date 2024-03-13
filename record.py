import orcid
import scopus
import doi
import pretty

# %% Specify IDs
orcid_id = "0000-0002-7108-637X"
scopus_id = "7103080737"
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
scopus_record = scopus.query_api(scopus_id, save_to=f"./Scopus-{record_name}.json")
scopus_doi_list = scopus.extract_doi(scopus_record)

print(f"    Retrieved {len(scopus_doi_list)} DOIs from Scopus.")

# %% Combine the lists
doi_list = list(set(orcid_doi_list + scopus_doi_list))

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
print(f"    Saved to {html_loc}")

print("Finished!")
