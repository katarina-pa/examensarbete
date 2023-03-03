# Important to have run the customize_from_list.py so that the right job_listings_desired.json file is used.
import sqlite3
import json

# read in the list of desired fields from a file and clean up one line space
with open("desired_fields.txt", "r", encoding="utf-8") as f:
  desired_fields = [line.strip() for line in f]

# read in the extracted job listings from a JSON file
with open("job_listings_desired.json", "r", encoding="utf-8") as f:
  job_listings_extracted = json.load(f)

# get the data types of the fields from the first job listing
field_data_types = {field: type(job_listings_extracted[0].get(field)) for field in desired_fields}

# connect to the database
conn = sqlite3.connect('job_listings.db')
c = conn.cursor()

# check if the table already exists
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='current_job_listings'")
table_exists = c.fetchone()

# create a new table for the job listings with dynamic columns based on fields in the JSON file
# added `` here too in case it would throw an error because of dot character
if not table_exists:
  #columns = [f"`{field}` TEXT" for field in desired_fields]
  
  # create the column definitions with the correct data types
  columns = []
  for field in desired_fields:
    data_type = field_data_types[field]
    if data_type is bool:
      column_def = f"`{field}` BOOLEAN"
    elif data_type is int:
      column_def = f"`{field}` INTEGER"
    else:
      column_def = f"`{field}` TEXT"
    columns.append(column_def)
'''
else:
  # get the existing columns from the table
  c.execute("PRAGMA table_info(current_job_listings)")
  existing_columns = [row[1] for row in c.fetchall()]

  # only include the additional columns in the create table query
  columns = []
  for field in desired_fields:
    if field not in existing_columns:
      columns.append(f"{field} TEXT")
  # add back the id column
  #columns = ["id INTEGER PRIMARY KEY"] + columns
'''    
create_table_query = "CREATE TABLE current_job_listings ({})".format(", ".join(columns))
c.execute(create_table_query)

# insert the extracted job listings into the table, so that it does not add the same values over and over on each row, causing duplicates
for job in job_listings_extracted:
    # added f"`{field}`" for field in desired_fields]
    values = [job.get(f"`{field}`", "") for field in desired_fields]
    #query = "INSERT INTO current_job_listings ({}) VALUES ({})".format(", ".join(desired_fields), ", ".join(["?" for _ in range(len(desired_fields))]))
    # added the `` for field due to dot character in the field names in json data
    # I added extra [f"`{field}`" for field in desired_fields] for the 2nd desired fields in the len()
    query = "INSERT INTO current_job_listings ({}) VALUES ({})".format(", ".join([f"`{field}`" for field in desired_fields]), ", ".join(["?" for _ in range(len(desired_fields))]))
    print(values)
    c.execute(query, tuple(values))


# commit changes and close the database connection
conn.commit()
conn.close()
