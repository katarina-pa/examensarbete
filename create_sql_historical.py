# OBS! Important to have run the customize_from_list_3rd_historical.py AND change JSON file read so that the right job_listings_desired.json file is used.
import sqlite3
import json

table_name = "historical_job_listings"

# read in the list of desired fields from a file and clean up one line space and ordered columns
with open("desired_fields_historical.txt", "r", encoding="utf-8") as f:
  #desired_fields = [line.strip() for line in f]
  #correct the non-SQLite compatible naming convention with a _ instead of .
  desired_fields = [line.strip().replace(".", "_") for line in f]

# read in the extracted job listings from a JSON file
# OBS! Must change the years in json file so that it reads the correct data pull
with open("job_listings_desired_2021-2022.json", "r", encoding="utf-8") as f:
  job_listings_extracted = json.load(f)

# get the data types of the fields from the extracted job listing in json file to format db columns later
field_data_types = {field: type(job.get(field)) for job in job_listings_extracted for field in job if field in desired_fields}

# connect to the database
conn = sqlite3.connect('job_listings.db')
c = conn.cursor()

# check if the table already exists
# OBS! currently hardcoded table name under name= so need to make sure to change it when need a different table name
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='historical_job_listings'")
table_exists = c.fetchone()
if table_exists:
  print("Requested table name already exists")
else:
# define the db column datatypes from what is in the json file as well as redefine id column and others with the data types that we want to see in the db
  columns = []
  for field in desired_fields:
    data_type = field_data_types[field]
    if data_type is bool:
      column_def = f"`{field}` BOOLEAN"
    #not sure if we want something like this or not for the other id fields (taxonomy id)
    #elif field.str.contains ("*id"):
    #  column_def = "`id` INTEGER"
    #in historical, the ID is actually a string, so will comment out. I will still try to make it a PRIMARY KEY, if possible
    elif field == "id":
      column_def = "`id` TEXT PRIMARY KEY"  
    elif data_type is int:
      column_def = f"`{field}` INTEGER"
    else:
      column_def = f"`{field}` TEXT"
    columns.append(column_def)
  #add them back as for use later on when comparing to job dictionary, so that the list and the columns in db match
  field_data_types[field] = data_type

  # create a new table for the job listings with dynamic columns and datatypes as defined in code above
  # using variable name table_name which can be changed at the top, however there are two other places that are still hardcoded
  create_table_query = "CREATE TABLE {} ({})".format(table_name,",".join(columns))
  # actual execution of the SQL query to create a table
  c.execute(create_table_query)

# looping through the data in the json file
for job in job_listings_extracted:
    # Replace "." with "_" in field names to match updated db table names
    job = {key.replace(".", "_"): value for key, value in job.items()}
    #chat GPT suggested the below to extract only the values from the listing and to convert any datatypes that are not str, bool, or int.
    values = [str(job.get(field, "")) if isinstance(job.get(field, ""), (str, bool)) else int(job.get(field)) if isinstance(job.get(field), int) else "" for field in job.keys() if field in desired_fields]
    # added the `` for field due to dot character in the field names in json data
    # the ignore fixed the unique constraint error that I got after introducing primary key so that I would not get duplicate fields. It basically skips any duplicate dataset once an id has already been found.
    # OBS! currently hardcoded table name so need to make sure to change it when need a different table name
    query = "INSERT OR IGNORE INTO historical_job_listings ({}) VALUES ({})".format(','.join([f"`{field}`" for field in desired_fields]), ','.join(['?' for _ in range(len(desired_fields))])).replace("[]","").replace("{}","")
    # actual execution of the above query and values
    c.execute(query, tuple(values))


# commit changes and close the database connection
conn.commit()
conn.close()
