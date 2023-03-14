# This query was created and tweaked to fix an user error that was made--when updating header names inside db (replaced . with _), the column description_text
# accidentally got "description.text" inserted as the value on all rows. Original JSON files contained the correct data, so re-inserted 
# with INSERT OR REPLACE in the python-sql query section. But had to replace the . for _ in two places in order to have the data corrected before insertion. 
# OBS! Important to have run the customize_from_list_3rd_historical.py AND change JSON file read so that the right job_listings_desired.json file is used.
# Must also change jtxt file and table name according to which historical table is being inserted into.
import sqlite3
import json

# read in the list of desired fields from a file and clean up one line space and ordered columns, replaced . for _ for later insert into db
with open("desired_fields_historical_2019-2020.txt", "r", encoding="utf-8") as f:
  # desired_fields = [line.strip() for line in f]
  desired_fields = [line.strip().replace(".", "_") for line in f]
# read in the extracted job listings from a JSON file
# OBS! Must change the years in json file so that it reads the correct data pull
with open("job_listings_desired_2019-2020.json", "r", encoding="utf-8") as f:
  job_listings_extracted = json.load(f)

# connect to the database
conn = sqlite3.connect('job_listings.db')
c = conn.cursor()

# looping through the data in the json file
for job in job_listings_extracted:
    # Replace "." with "_" in field names to match updated db table names
    job = {key.replace(".", "_"): value for key, value in job.items()}
    # added f"`{field}`" for field in desired_fields]
    #chat GPT suggested the below to extract only the values from the listing and to convert any datatypes that are not str, bool, or int.
    values = [str(job.get(field, "")) if isinstance(job.get(field, ""), (str, bool)) else int(job.get(field)) if isinstance(job.get(field), int) else "" for field in job.keys() if field in desired_fields]
    # added the `` for field due to dot character in the field names in json data
    # the ignore fixed the unique constraint error that I got after introducing primary key so that I would not get duplicate fields. It basically skips any duplicate dataset once an id has already been found.
    # OBS! currently hardcoded table name so need to make sure to change it when need a different table name
    query = "INSERT OR REPLACE INTO historical_job_listings_2019_older ({}) VALUES ({})".format(','.join([f"`{field}`" for field in desired_fields]), ','.join(['?' for _ in range(len(desired_fields))])).replace("[]","").replace("{}","")
    # actual execution of the above query and values
    c.execute(query, tuple(values))


# commit changes and close the database connection
conn.commit()
conn.close()
