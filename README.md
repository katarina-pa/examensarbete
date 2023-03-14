# Examensarbete

## Our data collection methods

We decided to use https://jobsearch.api.jobtechdev.se and https://historical.api.jobtechdev.se/ to review both current and historical job listings from the Swedish Labor Departments own job posting site called Platsbanken. 

The API with current listings https://jobsearch.api.jobtechdev.se contained postings involving devops from 2022-09-21 through 2023-03-07, so we decided to compare the same dates from previous years in order to do a fair comparison. 

We used their own built-in filters to do a free-text query on the word "devops" in the ad title, occupation title or in the ad description itself, and also filtered on country to only show those jobs located in Sweden. This provided us with a total of 1541 ads in json format.

With the help of chatGPT, we wrote some python codes to extract only the fields that we wanted for our project and stored them in json files organized by dates pulled. 

With python, we created a SQLite database based upon the headers in the extracted data and then loaded the json files into a SQLite DB to more easily query and analyze data trends.

We then explored the data through querying in the DB as well as in Excel.

### Issues we came across and solutions
* The reason we based our dates for the historical to Sep 21 to March 7 was to match the dates in our data pull from the current API as of the day when we pulled them.

  We pulled all the matching data from the current API that was available at the time of the pull, we did not have any date filters as we wanted all that was a match on our search. 
  
  That means that this same data pull may have different results when pulled on another occasion, if not using date filters. This will happen for two reason:
  * New job listings are posted each day.
  * The 2022 data is currently being migrated over to historical APIs: 

  https://gitlab.com/arbetsformedlingen/job-ads/jobsearch-apis/-/issues/105

  

* The original data in the historical API has some discrepancies as explained in https://gitlab.com/arbetsformedlingen/job-ads/getting-started-code-examples/historical-ads-info#limitations

  We resolved this by choosing to focus more on trends than actual numbers, which suited the purposes of our project.

* Because the historical data had different header names than the current, we decided to create separate tables to account for and preserve the original header names and data as much as possible. We have a total of 3 tables in the one database for this reason. See below section "Nitty-gritty" for a complete list of files and description.

*   Because not all fields were populated throughout the year samples, we also took small samples to manually review the ad descriptions in order to find more information and discover what type of skills, tools and technologies were being requested or desired in a job applicant. We did this by copying over the data into Excel.

    This proved to be very labor and time-intensive so we were not able to cover all areas that we had wanted in the time allotted, but we hope to complete more as we continue to work on it.

* In addition, because the data was a one-time pull and we were pressed for time (and our programming skills are not yet as strong as we would have liked), we did not spend more time on how to make the codes more efficient. We fixed things as we encountered them and did not go back to redo it in a more efficient (and cleaner) manner.

    We know that the whole process can be optimized and will return to streamline and automate the retrieval process, but for the purposes of this project, we decided to stop once we got the desired data pull.

* The nested field names in the json data contain [.] (period). We did not realize until later while querying in the database that this name format was not compatible with SQLite as it could not recognize field/column names with a period in it. At first we fixed this at the database level, but then later on when we realized we had made an error with the data that required us to upload the data again, we also fixed the compatibility in the python codes.

## Nitty-gritty
### Current API data
All files pertaining to the current API and a description of their usage:
* **desired_fields.txt** This file contains the list of the fields that we wanted to extract.
* **customize_from_list_3rd_current.py** This file loops through the API using their own filters for devops and Sweden: 
  
    ```Python
    https://jobsearch.api.jobtechdev.se/search?q=devops&country=i46j_HmG_v64
    ```
    It then references "*desired_fields.txt*" to gather only the specified fields and their contents (even elements in a 3rd nesting json layer). It will then save all the gathered data into "*job_listings_desired.json*" (creating the file if it does not already exists.)
* **create_sql_current.py** This is the file we used to dynamically create "*job_listings.db*" and the "*current_job_listings*" table based upon the extracted data in "*job_listings_desired.json*". It also uploads the extracted data into the table after creating it.
* **job_listings_desired.json** This is the default file that gets created with the data from the API after we run the above python code.
* **job_listings_desired_2022-2023.json** This is the back-up file that contains the data that we uploaded into the current_job_listings table. We added the years at the end of the name to preserve the extracted data pull as it was when we uploaded it into the db.
* **job_listings.db** This is the database that we created and where we stored the data. Contains 3 tables: 
    * "current_job_listings" (from current API from Sep 21 2022-March 07 2023)
    * "historical_job_listings" (contains data from the historical API from Sep 21 2020-March 07 2022)
    * "historical_job_listings_2019_older" (data from historical AP from Sep 21 2016-March 07 2020).
* **insert_sql_current.py** This will loop through the json file "job_listings_desired" and replace any "." in header name with "_" before finally inserting data into the "current_job_listings" table in the "job_listings" database. This can be used to insert new data into the table, if needed.


#### **How to use and run these current files**
(This will be updated at a later time with cleaner code, especially the sql-python codes, until then please just follow as described below):

1. Check desired_fields.txt to make sure the wanted fields are correct. 
    
    If need to make changes, change them to what you want to extract from the API and save.
  
2. Run **customize_from_list_3rd_current.py**
    * OBS! The result of running this code will write over any data in "*job_listings_desired.json*" if the file already exists; if it does not exist it will create the file and store the retrieved data there. 

      It will also print to the terminal some numbers based upon the data pull: 
      * the total number of ads matching our search
      * the number of ads we have extracted
    * This is a simple test to see that we have extracted the expected data.
      * If the numbers **match**, you can proceed to number 3 in this section.
      * If the extracted numbers are double the amount of the total, you seem to have appended the data twice somewhere in the code.
        * If the extracted numbers are more than the total, but not an obvious duplicate of the data set, you will need to manually review the code and the data to determine why this is. 
      * If the extracted numbers are **less than** the total, you can go to the last loop and comment out the extracted data appendage and instead comment back in the entire missing fields section as well at print at the bottom of the code for further trouble-shooting:

        ``` Python   
          job_listings_extracted.append(extracted_fields)
        ```

        ```Python
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
        ```

        ``` Python
        '''
        print(missing_fields)
        for field in missing_fields:
            print(f"{len(missing_fields[field])} job listings are missing the field {field}:")
            print(missing_fields[field])
        '''
        ```
    * Do a quick skim through on your newly created json file "*job_listings_desired.json*" to make sure the data looks ok.

3. To dynamically create both a new SQLite database AND tables based upon your extracted data (this step will also insert your extracted data into the table after creation):      
      
    a. Open **create_sql_current.py**

    b. Change the following:

    * The database name (the code will only create a new database if it does not find one with the name you have entered.)
      ```Python
      conn = sqlite3.connect('job_listings.db')
      ```
    * The table name in 3 locations:
      ```Python
        table_name = "current_job_listings"
      ```
      ```Python
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='current_job_listings'")
      ```
      ```Python
      query = "INSERT OR IGNORE INTO current_job_listings 
      ```

    c. Make sure that the names of the text file and the json file you will use are listed correctly:`

      ```Python
       with open("desired_fields.txt", "r", encoding="utf-8") as f:
      ```

      ```Python
        with open("job_listings_desired.json", "r", encoding="utf-8") as f:
      ```
    d. Save with your changes and run it.

      * If the tablename already exists, it will stop running and tell you the table already exists. If that is the case, then just skip to step 4.

    e. Open your newly created database and check your table and its content.

    
4. To only insert data into an existing SQLite table:

    a. Open **insert_sql_current.py**

    b. Check the following file names (change if needed to match the files you want to use) :
  
    * The database name

        ```Python
          conn = sqlite3.connect('job_listings.db')
        ```

    * The table name (the query will ignore any records where there is already an existing ID in the table--this to avoid unnecessary duplicates):
        ```Python
        query = "INSERT OR IGNORE INTO current_job_listings 
        ```
    c. Save your changes (if any) and run it.

    d. Open your table and check that your data has been added.


### Historical API data
All files pertaining to the historical API and a description of their usage:
* **desired_fields_historical.txt** This file contains the list of the fields that we wanted to extract. It matches the headers for the time period between *Sep 21 2020 - March 07 2022*.
* **desired_fields_historical_2016-2020.txt** This file contains the list of the fields that we wanted to extract. It matches the headers for the older time periods that we pulled between *Sep 21 2016 - March 07 2020*.
* **customize_from_list_3rd_historical.py** This file loops through the historical API using their own filters for devops and Sweden and the date ranges we need (in the url example below it is 2016-2017): 
  
    https://historical.api.jobtechdev.se/search?q=devops&country=i46j_HmG_v64&historical-from=2016-09-21&historical-to=2017-03-07

    It then references "*desired_fields_2016-2020.txt*" to gather only the specified fields and their contents (even elements in a 3rd nesting json layer). It will then save all the gathered data into "*job_listings_desired_[YYYY-YYYY].json*" (creating the file if it does not already exists.)
* **job_listings_desired_[YYYY-YYYY].json** These are the files that contains the data that we uploaded into the historical tables. We added the years at the end of the name to distinguish between each time period pulled.    
* **create_sql_historical.py** This is the file we used to connect to "*job_listings.db*" (described in more detail above in current data file descriptions) and dynamically create the "*historical_listings*" table based upon the extracted data in "*job_listings_desired_2020-2021.json*" and "*job_listings_desired_2021-2022.json*". It also uploads the extracted data into the table after creating it. This is only for Sep 2020-March 2022 data.

* **create_sql_historical_2019_older.py** This is the file we used to connect to "*job_listings.db*" and dynamically create the "*historical_listings_2019_older*" table based upon the extracted data in the files
"*job_listings_desired_[YYYY-YYYY].json*" where the end of the name corresponds to the year-interval of the data pull. It also uploads the extracted data into the table after creating it. This is only for Sep 2016-March 2020.

* **insert_sql_historical.py** This will loop through "*job_listings_desired_[YYYY-YYYY].json*", replace any "." in header name with "_" before finally inserting data into one of the two historical table in the "job_listings" database. This can be used to insert new data into the tables, if needed.

#### **How to use and run these historical files**
(This section will be updated at a later time with cleaner code, especially the sql-python codes, until then please just follow as described below):

1. Check the contents of the below files that corresponds to the time period you want to pull to make sure the wanted fields are correct:
    
    * **desired_fields_historical.txt** *OR*   **desired_fields_historical_2016-2020.txt**
    
      (See file descriptions above to determine which one you want to use)  
    
    * If you need to make changes, change the appropriate file to match the fields you want to extract from the API and save.

2. To pull data from the historical API:
  
    a. Open **customize_from_list_3rd_historical.py**

    b. Find the url and change the years WITHIN THE URL to the data you want to pull:

      ```Python
      url = "https://historical.api.jobtechdev.se/search?q=devops&country=i46j_HmG_v64&historical-from=2016-09-21&historical-to=2017-03-07"
      ```
    
    b. Check (and change as needed) the following:
    
    * The text file referenced for *desired_fields* matches the one you want from step 1 above:
        ```Python
        with open("desired_fields_[INSERT_CORRECT_NAME].txt", "r") as f:
        ```
    * Change the name of the json file to correspond with the years that you are pulling. OBS! Keep in mind that this will be the output json file after you have run the python code. If the file name already exists, it will override any data currently in it with your current pool.
        ```Python
        with open("job_listings_desired_[INSERT_CORRECT_NAME].json", "w", encoding="utf-8") as f:
        ```
    c. Save and run.

    * Upon completion, in addition to producing the said json file, it will also print to the terminal some numbers based upon the data pull:
      * the total number of ads matching our search
      * the number of ads we have extracted
    * This is a simple test to see that we have extracted the expected data.
      * If the numbers **match**, you can proceed to number 3 in this section.
      * If the extracted numbers are double the amount of the total, you seem to have appended the data twice somewhere in the code.
        * If the extracted numbers are more than the total, but not an obvious duplicate of the data set, you will need to manually review the code and the data to determine why this is. 
      * If the extracted numbers are **less than** the total, you can go to the last loop and comment out the extracted data appendage and instead comment back in the entire missing fields section as well at print at the bottom of the code for further trouble-shooting:

        ``` Python   
          job_listings_extracted.append(extracted_fields)
        ```
        ```Python
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
        ```
        ``` Python
        '''
        print(missing_fields)
        for field in missing_fields:
            print(f"{len(missing_fields[field])} job listings are missing the field {field}:")
            print(missing_fields[field])
        '''
        ```
    * Do a quick skim through on your newly created json file "*job_listings_desired_[YYYY-YYYY].json*" to make sure the data looks ok.
3. To dynamically create both a new SQLite database AND tables based upon your extracted data (this will also insert your extracted data into the table after creation):      
      
    a. Depending on where your time spans pulled falls, one of the following python files (see file descriptions above to determine which one you want to use):

      * **create_sql_historical.py** *or* **create_sql_historical_2019_older.py**

    b. Change the following:

    * The database name (it will create a new database if it does not find one with the name you have entered.)
      ```Python
      conn = sqlite3.connect('[INSERT_YOUR_DATABASE_NAME].db')
      ```
    * The table name in 3 locations:
      ```Python
      table_name = "[YOUR TABLE NAME]"
      ```
      ```Python
      c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='[YOUR TABLE NAME]'")
      ```
      ```Python
      query = "INSERT OR IGNORE INTO [YOUR TABLE NAME] 
      ```
     * The text file (to match the one from step 2b):
      
        ```Python
        with open("desired_fields_[INSERT_CORRECT_NAME].txt", "r", encoding="utf-8") as f:
        ```

      * The json file (to match the one from step 2b above)

        ```Python
        with open("job_listings_[INSERT_CORRECT_NAME].json", "r", encoding="utf-8") as f:
        ```

    d. Save with your changes and run it.

      * If there is already a table with the name you listed, it will stop running and tell you the table already exists. If that is the case, then just skip to step 4 below.

    e. Open your newly created database and check your table(s) and their content.

4. To insert data into an existing SQLite historical table:

    a. Open **insert_sql_historical.py**

    b. Check the following file names (change if needed to match the files you want to use) :

    * The text file

      ```Python
      with open("desired_fields_[INSERT_CORRECT_NAME].txt", "r", encoding="utf-8") as f:
      ```

    * The json file

      ```Python
      with open("job_listings_desired_[INSERT_CORRECT_NAME].json", "r", encoding="utf-8") as f:
      ```

    * The database name

      ```Python
        conn = sqlite3.connect('job_listings.db')
      ```

    * The table name:
      ```Python
      query = "INSERT OR IGNORE INTO [INSERT_CORRECT_HISTORICAL_TABLE] 
      ```
    c. Save your changes (if any) and run it.

    d. Open your table and check that your data has been added.