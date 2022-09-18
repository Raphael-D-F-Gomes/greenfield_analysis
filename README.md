# Greenfield analysis report generator 

This repository contains a report generator that search for errors and inconsistencies in a excel file with greenfield analysis data.
Plus, the report generator also show errors and alerts found, insert and delete data in a database with information about customers and suppliers,
show main statistics about customers and suppliers and plot a location analysis. 


To execute this project, you must first create the database "greenfield_analysis_data.db" with "create_database.py". 
Then, the "server.py" must be executed. The home page has the way to insert the excel file with the greenfield data. 


## Types of errors

* Divergence in the status between Customers and Locations tables
* Divergence in the status between Suppliers and Locations tables
* Customer without location
* Supplier without location
* Negative value in a customer demand
* Negative value in a supply
* Table missing
* Column missing in a table
* Status with wrong type

## Types of alerts
* All status marked as "Exclude"
* Null value in a demand
* Null value in a supply
* Duplicated values in a table
* Extra columns in a table
* Extra tables in a excel file
* Latitude or Longitude in a wrong format
