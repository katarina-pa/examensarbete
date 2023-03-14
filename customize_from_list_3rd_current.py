import requests
import json

# This is the current API joblistings url with a built in search for devops and Sweden
url = "https://jobsearch.api.jobtechdev.se/search?q=devops&country=i46j_HmG_v64"
# According to chatGPT the user agent ifnormation is added because some websites may require you to set a User-Agent header
headers = {"Accept": "application/json", "User-Agent": "Mozilla/5.0"} 

# read in the list of desired fields from a file and clean up one line space
with open("desired_fields.txt", "r") as f:
  desired_fields = [line.strip() for line in f]

# empty dictionaries and list for later usage in the loop
job_listings_extracted = []
missing_fields = {}

#chatGPT 2nd suggested function to be able to concatenate a list if more than one element present, this allows us to be able to retrieve data
#even when in a 3rd nested layer.
def get_value_by_nested_key(nested_dict, keys):
    current = nested_dict
    for key in keys:
        if isinstance(current, list):
            # If the current value is a list, concatenate all the values for the given key from each item in the list
            values = [item.get(key, {}) for item in current]
            # Join the values together as a string separated by ","
            current = ', '.join(str(value) for value in values if value)
        else:
            # If the current value is a dictionary, get the value associated with the given key
            current = current.get(key, {})
    return current if current != {} else None

# Iterate over the results with an increment of 100 until you have 500 job listings, can be changed to increase the offset for a bigger 
# data retrieval
for offset in range(0, 500, 100):
    params = {"offset": offset, "limit": 100}
    response = requests.get(url, headers=headers, params=params)
    # The request was successful
    if response.status_code == 200:
      # Add all json response from website into variable called data
      data = response.json()
      # adding in total total.value from the data set so can see the total postings found in url for later comparison 
      # with what we pulled in job_listings so we don't drop anything
      total = data.get("total", 0)
      # get all the job listings in hits directory
      job_listings = data.get("hits", [])
      
      #the start of looping through the data and picking out the desired fields
      for job in job_listings:
          #originally had "extracted_fields = {}" placed outside the loop, which did not create a new empty dictionary for each job, so
          #chat GPT suggested I move it within this specific job_listings group but before the field so that a new one is
          #ready for each job (to fix duplicate first row)
          extracted_fields = {}
          # extract the desired fields from each job listing, from the list called upon earlier
          for field in desired_fields:
            # traverse the nested dictionaries (and lists) to extract the desired field
            current = job
            for key in field.split("."):
              keys = field.split(".")
              value = get_value_by_nested_key(job, keys)
              extracted_fields[field] = value
          # The below needs to be commented out if the below missing fields secion is commented back in or there will be duplicate appending.    
          job_listings_extracted.append(extracted_fields)

          # The below should be checking for joblisting with missing fields  (in case there are any, for trouble shooting purposes). If none missing,
          # then it just appends the info to the job_listings_extracted.
          '''
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
          '''
    else:
    # The request was unsuccessful
      print("Error: Status code", response.status_code)
      break
    
# Here we create the job_listings_desired.json file with the information retrieved from the api
# encoding="utf-8" and ensure_ascii=False together make sure that Swedish letters (å,ä,ö) are kept intact even when dumped in json file.
with open("job_listings_desired.json", "w", encoding="utf-8") as f:
  json.dump(job_listings_extracted, f, ensure_ascii=False, indent=4)

# Print of number of api's own accounting of job listings; for data quality comparion and purposes
print("Total job listings from url:", total)
# print of number of retrieved job postings with desired fields, to compare with total above
num_jobs_extract = len(job_listings_extracted)
print(f"{num_jobs_extract} jobs found in extracted_fields")

# print out the IDs of the job listings missing each desired field (if missing_fields is empty it will only print an empty dictionary)
# only for troubleshooting purposes if there are less extracted fields than total.
'''
print(missing_fields)
for field in missing_fields:
    print(f"{len(missing_fields[field])} job listings are missing the field {field}:")
    print(missing_fields[field])
'''