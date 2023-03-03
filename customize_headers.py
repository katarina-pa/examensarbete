import requests
import json

url = "https://jobsearch.api.jobtechdev.se/search?q=devops&offset=101&limit=100&country=i46j_HmG_v64"
headers = {"Accept": "application/json",
           "User-Agent": "Mozilla/5.0"}  # Some websites may require you to set a User-Agent header

response = requests.get(url, headers=headers)

if response.status_code == 200:
    # The request was successful
    data = response.json()

    # Extract only certain headers from the response
    headers_to_keep = ["id", "headline", "application_deadline"]
    extracted_data = [{key: job.get(key) for key in headers_to_keep}
                      for job in data.get("hits", [])]

    ## Print the extracted data
    #print(extracted_data)
    # Save the extracted data to a JSON file
    with open("extracted_data.json", "w") as f:
      json.dump(extracted_data, f)
else:
    # The request was unsuccessful
    print("Error: Status code", response.status_code)
