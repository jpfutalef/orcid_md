# ORCID record

Customized automatic creation of publication record using ORCID data.

# Instructions

1. Clone this repository
2. Navigate to this folder in the terminal
3. You can install the necessary packages by running:
```bash
pip install -r requirements.txt
```
4. Specify the ORCIDID variable in the `orcid_record.py` file.
5. Run the script:
```bash
python orcid_record.py
```

# Output
The scripts does the following:
1. Queries the ORCID API to get the publications of the user specified in the `orcid_record.py` file.
2. The above returns DOI and title of the publications, stored in the `ORCID-[ORCIDID].json` file.
3. The script then queries the CrossRef API to get the data of each publication.
4. The detailed data is stored in the `Record-[ORCIDID].xlsx` file.

