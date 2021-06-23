#!/usr/bin/env python

import os
import configparser
import json
import sys
import csv
import requests
import time
from os import path

# Authorization to call the Conformity API - set CC_API_KEY as env variable
apiKey = os.environ["CC_API_KEY"]

# Read config file and make case-sensitive
configFileName = "request_config.ini"
config = configparser.ConfigParser()
config.optionxform=str
config.read(path.join(path.dirname(sys.argv[0]), configFileName))

# Load and prepare API parameters
parameters = config["parameters"]
region = parameters.get("conformityHostedRegion")
accountIds = parameters.get("accountIds")
pageSize = int(parameters.get("page[size]"))
if type(parameters.get("page[Number]")) == type(0): 
	pageNumber = parameters.get("page[Number]")
else :
	pageNumber = 0
parameter_string = "?accountIds={}&page[size]={}&page[Number]={}".format(accountIds, pageSize, pageNumber)

# Load and prepare checks API filters
filters = config["filters"]
filter_string = ''
for option in filters: 
	if filters.get(option) != '' : 
		filter_string += "&filter[{}]={}".format(option, filters.get(option))

note_filters = config["notes"]
notesBoolean = note_filters.get("notes")
notesLength = note_filters.get("notesLength")
note_string = "?filter[notes]={}&filter[notesLength]={}".format(notesBoolean, notesLength)

# Building the initial Checks API query URL
checks_url = "https://{}-api.cloudconformity.com/v1/checks".format(region)
all_checks_url = "{}{}{}".format(checks_url, parameter_string, filter_string)
headers = {
	'Authorization' : 'ApiKey {}'.format(apiKey),
	'Content-Type' : 'application/vnd.api+json'
}

# launch the request session
session = requests.session()

# function to list all checks definied by the filters
def get_account_checks():
    combined = []
    if type(parameters.get("page[Number]")) == type(0) : 
    	pageNumber = parameters.get("page[Number]")
    else :
    	pageNumber = 0
    counter = 0
    max_results = 1
    while counter <= max_results:
        page = session.get(all_checks_url, headers=headers).json()
        max_results = page["meta"]["total"]
        counter += pageSize
        pageNumber += 1
        data = page["data"]
        combined += data
    return {"data": combined, "meta": page["meta"]}

# Launch the initial list-checks API call
print("Retrieving all relevant checks definied by {}...".format(configFileName))
pages_combined = get_account_checks()
print("Done\n")
returned_checks = pages_combined["data"]

# Establish a list for the final report data
report_data = []

# Using checks data, loop through each check to retrieve further details including the supression notes
print("Initiating process to retrieve each check's details...")
check_count = 0
for check in returned_checks:
	checkId = check["id"]
	specific_check_url = "{}/{}{}".format(checks_url, checkId, note_string)

	# Retrive the data for the specific check
	retrieve = session.get(specific_check_url, headers=headers)
	print("API response:" + str(retrieve.status_code) + " for check: " + checkId)
	
	# Build the data dictionary for the report output for each check
	response_data = retrieve.json()
	epoch_suppression_date = int(response_data["data"]["attributes"]["notes"][0]["created-date"])
	local_converted_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch_suppression_date/1000))
	reportDictionary = {
		"checkId" : response_data["data"]["id"],
		"ruleId" : response_data["data"]["relationships"]["rule"]["data"]["id"],
		"riskLevel" : response_data["data"]["attributes"]["pretty-risk-level"],
		"message" : response_data["data"]["attributes"]["message"],
		"resource" : response_data["data"]["attributes"]["resource"],
		"suppressed" : response_data["data"]["attributes"]["suppressed"],
		"suppressionNote" : response_data["data"]["attributes"]["notes"][0]["note"],
		"suppressionDate" : local_converted_date,
		"supressionCreatedBy" : response_data["data"]["attributes"]["notes"][0]["createdBy"],
		"conformityAccountId" : response_data["data"]["relationships"]["account"]["data"]["id"],
		"cloudProvider" : response_data["data"]["attributes"]["provider"],
		"resourceLink" : response_data["data"]["attributes"]["link"],
		"resolutionPage" : response_data["data"]["attributes"]["resolution-page-url"]
	}
	
	# Append check data to the combined report_data list object
	report_data.append(reportDictionary)
	check_count += 1

# Confirming report output
totalChecks = len(report_data)
print("\nReport data compiled for a total of {} checks".format(totalChecks))

# Prepare report filepath and timestamp
timestamp = time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime())
filepath = path.join(path.dirname(sys.argv[0]),"suppression_report_{}.csv".format(timestamp))

# Convert report_data to a csv output
keys = report_data[0].keys()
with open(filepath, "w", newline="")  as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(report_data)

print("\nData saved as: suppression_report_{}.csv\nDone".format(timestamp))    
