# This is the current API joblistings for devops and Sweden
import requests
import json

url = "https://jobsearch.api.jobtechdev.se/search?q=devops&country=i46j_HmG_v64"
headers = {"Accept": "application/json",
           "User-Agent": "Mozilla/5.0"} # Some websites may require you to set a User-Agent header

# read in the list of desired fields from a file and clean up one line space
with open("desired_fields.txt", "r") as f:
  desired_fields = [line.strip() for line in f]

# empty dictionaries and list for later usage in the loop
extracted_fields = {}
job_listings_extracted = []
missing_fields = {}


# Iterate over the results with an increment of 100 until you have 500 job listings, can be changed to increase the offset for a bigger 
# data retrieval
for offset in range(0, 500, 100):
    params = {"offset": offset, "limit": 100}
    response = requests.get(url, headers=headers, params=params)
    # The request was successful
    if response.status_code == 200:
      data = response.json()
      # adding in total total.value from the data set so can see the total postings found in url for later comparison 
      # with what we pulled in job_listings so we don't drop anything
      total = data.get("total", 0)
      # get all the job listings in hits directory
      job_listings = data.get("hits", [])
      
      for job in job_listings:
          # extract the desired fields from each job listing, from the list called upon earlier
          for field in desired_fields:
            # traverse the nested dictionaries (and lists) to extract the desired field
            current = job
            for key in field.split("."):
              if isinstance(current, list):
                current = [item.get(key, {}) for item in current]
              else:
                current = current.get(key, {})
            extracted_fields[field] = current

          # checking for joblisting with missing fields  (in case there are any, for trouble shooting purposes). If none missing,
          # then it appends the info to the job_listings_extracted. I do not remember how to do this without it, so will leave in place.
          missing_fields_found = False
          for field in desired_fields:
            if field not in extracted_fields:
              job_id = job["_id"]
              if field not in missing_fields:
                missing_fields[field] = []
              missing_fields[field].append(job_id)
              missing_fields_found = True
          if not missing_fields_found:
            job_listings_extracted.append(extracted_fields)
    else:
    # The request was unsuccessful
      print("Error: Status code", response.status_code)
      break
    
# encoding="utf-8" and ensure_ascii=False   together make sure that Swedish letters (å,ä,ö) are kept intact even when dumped in json file.
with open("job_listings_desired.json", "w", encoding="utf-8") as f:
  json.dump(job_listings_extracted, f, ensure_ascii=False, indent=4)

# So we can see a print of total for data quality purposes
print("Total job listings from url:", total)
# to see number of fields retrieved from desired_fields.txt, not needed once done
# num_jobs = len(desired_fields )
#print(f"{num_jobs} fields found in desired_fields ")
# to see number of job postings retrieved with desired fields, to compare with total
num_jobs_extract = len(job_listings_extracted)
print(f"{num_jobs_extract} jobs found in extracted_fields")

# print out the IDs of the job listings missing each desired field (if missing_fields is empty it will only print an empty dictionary)
# only for troubleshooting purposes if there are discrepancies between total and extracted. 
'''
print(missing_fields)
for field in missing_fields:
    print(f"{len(missing_fields[field])} job listings are missing the field {field}:")
    print(missing_fields[field])
'''