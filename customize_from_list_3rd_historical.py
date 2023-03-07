import requests
import json

# This is the historical API joblistings url with a built in free text search for devops within Sweden between historical dates
# OBS! you must change the dates within the URL as of now since I just need it to work, optimization will come later.
url = "https://historical.api.jobtechdev.se/search?q=devops&country=i46j_HmG_v64&historical-from=2016-09-21&historical-to=2017-03-07"
# According to chatGPT the user agent ifnormation is added because some websites may require you to set a User-Agent header
headers = {"Accept": "application/json", "User-Agent": "Mozilla/5.0"} 

# read in the list of desired fields from a file and clean up one line space
# had to create historical list since headers were different from current. Had to create a 3rd one ending _2019-2020 for 
# that time period since it was missing even more.
# OBS! Make sure correct txt file is referenced!
with open("desired_fields_historical_2019-2020.txt", "r") as f:
  desired_fields = [line.strip() for line in f]

# empty dictionaries and list for later usage in the loop
job_listings_extracted = []
missing_fields = {}

'''
# suggested function by chatGPT to reiterate and be able to go to 3rd nesting level to retrieve value-- this one works as is
def get_value_by_nested_key(nested_dict, keys):
    """
    Traverses a nested dictionary and returns the value for a given set of keys.

    Parameters:
    - nested_dict (dict): The nested dictionary to traverse.
    - keys (list): The keys to look up in the dictionary. Each key represents a level of nesting.

    Returns:
    - The value associated with the given set of keys, or None if the keys were not found in the dictionary.
    """
    historical = nested_dict
    for key in keys:
        if isinstance(historical, list):
            # If the historical value is a list, create a new list containing the values for the given key from each item in the list
            historical = [item.get(key, {}) for item in historical]
        else:
            # If the historical value is a dictionary, get the value associated with the given key
            historical = historical.get(key, {})
        # If the historical value is a list with only one element, return that element instead of the whole list
        if isinstance(historical, list) and len(historical) == 1:
            historical = historical[0]
    return historical if historical != {} else None
'''


#2nd suggested function to be able to concatenate a list if more than one element present, will use this one 
# just in case there are any as it seems to work but I have not found a data example to verify it yet but it returns 
# the same as the first suggested function.
def get_value_by_nested_key(nested_dict, keys):
    historical = nested_dict
    for key in keys:
        if isinstance(historical, list):
            # If the historical value is a list, concatenate all the values for the given key from each item in the list
            values = [item.get(key, {}) for item in historical]
            # Join the values together as a string separated by ","
            historical = ', '.join(str(value) for value in values if value)
        else:
            # The below was giving me   AttributeError: 'NoneType' object has no attribute 'get' because of headers not existing
            # If the historical value is a dictionary, get the value associated with the given key
            historical = historical.get(key, {})
    return historical if historical != {} else None

# Iterate over the results with an increment of 100 until you have 1000 job listings, can be changed to increase the offset for a bigger 
# data retrieval. Historical allows an offset of 0-2000
for offset in range(0, 1000, 100):
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
            historical = job
            # somehow, the below is not working with the function, it returns ALL fields, so I will go backwards to see if I can
            # find out the compatibility issue. May be the headers list & indeed, there was no .label for must- & nice to have education.
            
            for key in field.split("."):
              keys = field.split(".")
              value = get_value_by_nested_key(job, keys)
              extracted_fields[field] = value
              '''
              #used the below to back track from the function step to trouble-shoot without function
            for key in field.split("."):
              if isinstance(historical, list):
                historical = [item.get(key, {}) for item in historical]
              else:
                historical = historical.get(key, {})
              extracted_fields[field] = historical '''
          job_listings_extracted.append(extracted_fields)

          # The below should be checking for joblisting with missing fields  (in case there are any, for trouble shooting purposes). If none missing,
          # then it just appends the info to the job_listings_extracted. It will not gather correctly without this piece however since
          # I do not remember how I have tied them together and now I cannot untangle them.
          
          missing_fields_found = False
          for field in desired_fields:
            if field not in extracted_fields:
              job_id = job["_id"]
              if field not in missing_fields:
                missing_fields[field] = []
              missing_fields[field].append(job_id)
              missing_fields_found = True
          if not missing_fields_found:
            pass
    else:
    # The request was unsuccessful
      print("Error: Status code", response.status_code)
      break
    
# Here we create the job_listings_desired.json file with the information retrieved from the api
# encoding="utf-8" and ensure_ascii=False together make sure that Swedish letters (å,ä,ö) are kept intact even when dumped in json file.
# OBS! make sure the .json file name matches the years being pulled
with open("job_listings_desired_2016-2017.json", "w", encoding="utf-8") as f:
  json.dump(job_listings_extracted, f, ensure_ascii=False, indent=4)

# Print of number of api's own accounting of job listings; for data quality comparion and purposes
print("Total job listings from url:", total)
# print of number of retrieved job postings with desired fields, to compare with total above
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