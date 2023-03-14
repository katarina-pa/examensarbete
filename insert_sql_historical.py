# OBS! Important to have run the customize_from_list_3rd_historical.py or customize_from_list_3rd_historical_2019_older.py first, and then ALSO change JSON file read so that the right job_listings_desired[YYYY-YYYY].json file is used.
# Must also change txt file and table name according to which historical table is being inserted into.
import sqlite3
import json

# read in the list of desired fields from a file and clean up one line space and ordered columns
with open("desired_fields_historical_2019-2020.txt", "r", encoding="utf-8") as f:
  #desired_fields = [line.strip() for line in f]
  #correct the non-SQLite compatible naming convention with a _ instead of .
  desired_fields = [line.strip().replace(".", "_") for line in f]

# read in the extracted job listings from a JSON file
# OBS! Must change the years in json file so that it reads the correct data pull
with open("job_listings_desired_2016-2017.json", "r", encoding="utf-8") as f:
  job_listings_extracted = json.load(f)

# don't believe I need the below for insertion only so commented out
# get the data types of the fields from the extracted job listing in json file to format db columns later
#field_data_types = {field: type(job.get(field)) for job in job_listings_extracted for field in job if field in desired_fields}

# connect to the database
conn = sqlite3.connect('job_listings.db')
c = conn.cursor()

# looping through the data in the json file
for job in job_listings_extracted:
    # Replace "." with "_" in field names to match updated db table names
    job = {key.replace(".", "_"): value for key, value in job.items()}
    #chat GPT suggested the below to extract only the values from the listing and to convert any datatypes that are not str, bool, or int.
    values = [str(job.get(field, "")) if isinstance(job.get(field, ""), (str, bool)) else int(job.get(field)) if isinstance(job.get(field), int) else "" for field in job.keys() if field in desired_fields]
    # added the `` for field due to dot character in the field names in json data
    # the ignore fixed the unique constraint error that I got after introducing primary key so that I would not get duplicate fields. It basically skips any duplicate dataset once an id has already been found.
    # OBS! currently hardcoded table name so need to make sure to change it when need a different table name
    query = "INSERT OR IGNORE INTO historical_job_listings_2019_older ({}) VALUES ({})".format(','.join([f"`{field}`" for field in desired_fields]), ','.join(['?' for _ in range(len(desired_fields))])).replace("[]","").replace("{}","")
    # actual execution of the above query and values
    c.execute(query, tuple(values))


# commit changes and close the database connection
conn.commit()
conn.close()
