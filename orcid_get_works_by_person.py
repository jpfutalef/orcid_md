
#%% Query ORCID for works authored by a person
# This notebook queries the [ORCID Public API](https://pub.orcid.org/v3.0/) to retrieve works listed in a person's 
# ORCID record. It takes an ORCID URL or iD as input to retrieve the ORCID record of a person and the works listed on it. 
# From the resulting list of works we output all DOIs.

# Prerequisites:
#!pip install python-benedict
import requests                        # dependency to make HTTP calls
from benedict import benedict          # dependency for dealing with json
import os
import json

print(f"Working directory: {os.getcwd()}")

#%% Query ORCID for works authored by a person
ORCID_RECORD_API = "https://pub.orcid.org/v3.0/"    # URL for ORCID API
target_orcid = "0000-0002-7108-637X"    # Zio's ORCID

# A function to query the ORCID API for a person's record
def query_orcid_for_record(orcid_id):
    response = requests.get(url=requests.utils.requote_uri(ORCID_RECORD_API + orcid_id),
                          headers={'Accept': 'application/json'})
    response.raise_for_status()
    result = response.json()
    return result

#%% Query the works
orcid_record = query_orcid_for_record(target_orcid)

# Save the ORCID record to a file
with open(f"./orcid_{target_orcid}.json", "w") as file:
    json.dump(orcid_record, file, indent='\t')

#%%
print(orcid_record["person"]["name"]["given-names"]["value"])

#%% Print a summary of the ORCID record
def print_record_summary(orcid_record):
    orcid_dict=benedict.from_json(orcid_record)
    print(f"ORCID iD: {orcid_dict.get('orcid-identifier.path')}")
    print(f"Name: {orcid_dict.get('person.name[0].given-names.value')} {orcid_dict.get('person.name[0].family-name.value')}")
    print(f"Biography: {orcid_dict.get('person.biography.content')}")


print_record_summary(orcid_record)


# In[18]:


import json
with open(f"./orcid_zio.json", "w") as file:
    json.dump(orcid_record, file)


# From the complete ORCID metadata we extract the works section and print out title and DOI of each first `work-summary` (the first item in a personal information section has the highest [display index](https://info.orcid.org/documentation/integration-guide/orcid-record/#Display_index)).
# 
# *Note: works that do not have a DOI assigned, will not be printed.*

# In[11]:


# extract works section from ORCID profile
def extract_works_section(orcid_record):
    orcid_dict=benedict.from_json(orcid_record)
    works=orcid_dict.get('activities-summary.works.group') or []
    return works

# for each work in the work section: extract title and DOI
def extract_doi(work):
    work_dict=benedict.from_json(work)
    title=work_dict.get('work-summary[0].title.title.value')
    dois= [doi['external-id-value'] for doi in work_dict.get('work-summary[0].external-ids.external-id', []) if doi['external-id-type']=="doi"]
    # if there is a DOI assigned to the work, the list of dois is not empty and we can extract the first one
    doi=dois[0] if dois else None
    return doi, title


# ---- example execution
works=extract_works_section(orcid_record)
for work in works:
    doi,title = extract_doi(work)
    if doi:
        print(f"{doi}, {title}")


# In[ ]:




