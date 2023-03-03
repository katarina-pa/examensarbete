# examensarbete

Trying to find a way to get headers and data from https://jobsearch.api.jobtechdev.se into a SQLite DB that would allow us to better query and analyze data trends.

The furthest I have come with the data extraction is with customize_from_list.py which utilizes desired_fields.txt for reference on fields we may be interested in. (This way we can edit the txt file fairly easily instead of searching through the python code.) customize_from_list.py produces a json file called "job_listings_desired.json".

create_sql.py is my thus far feeble attempt to both create a db and insert values dynamically based upon the data found in the created json file mentioned above ("job_listings_desired.json"). It creates a database called job_listings and a table within it called current_job_listings, and seemingly with the correct datatypes. However, the insertion of the values have not been successful, as it just shows up as empty strings (despite not being empty at all.)

I have added many of my different work pieces to the .gitignore so as to not clutter our repo & have only included those that may be of worth for us to look at.