import requests
import json

url = "https://jobsearch.api.jobtechdev.se/search?q=devops&country=i46j_HmG_v64"
headers = {"Accept": "application/json",
           "User-Agent": "Mozilla/5.0"} # Some websites may require you to set a User-Agent header

job_listings = []

# Iterate over the results with an increment of 100 until you have 500 job listings
for offset in range(0, 500, 100):
    params = {"offset": offset, "limit": 100}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        # The request was successful
        data = response.json()
        # adding in total to get total.value from the data set so I can see the total postings found in url for later comparison with what we pulled in job_listings so we don't drop anything
        total = data.get("total", 0)
        #this tells it to add to job_listings from data found the hits dictionary
        job_listings += data.get("hits", [])
    else:
        # The request was unsuccessful
        print("Error: Status code", response.status_code)
        break


# Extract only certain headers from the job listings
headers_to_keep = ["id", "headline", "workplace_address.municipality", "description.text", "application_deadline"]

#Straight forward searching and retrieving only the specified headers
#extracted_data = [{key: job.get(key) for key in headers_to_keep} for job in job_listings]

#for fields within nested dictionaries, we need to split the two and check that they work... or something like that, I forget in this moment.
extracted_data = [{key: job.get(key) if "." not in key else job.get(key.split(".")[0], {}).get(key.split(".")[1]) for key in headers_to_keep} for job in job_listings]

# Save the extracted data to a JSON file called "extracted_data_total_hits.json"(see filename in parenthesis after with open). 
# encoding="utf-8" & ensure_ascii=False  makes sure the Swedish letters stay intact
with open("extracted_data_loop.json", "w", encoding="utf-8") as f:
    json.dump(extracted_data, f, ensure_ascii=False)

print("Total job listings from url:", total)
num_jobs = len(job_listings)
print(f"{num_jobs} jobs found in extracted_data_loop")