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
config = configparser.ConfigParser()
config.optionxform=str
config.read("request_config.ini")

# Load and prepare parameters
parameters = config["parameters"]
region = parameters.get("conformityHostedRegion")
accountIds = parameters.get("accountIds")
pageSize = int(parameters.get("page[size]"))
if type(parameters.get("page[Number]")) == type(0): 
	pageNumber = parameters.get("page[Number]")
else :
	pageNumber = 0
parameter_string = "?accountIds={}&page[size]={}&page[Number]={}".format(accountIds, pageSize, pageNumber)

# Load and prepare filters
filters = config["filters"]
filter_string = ''
for option in filters: 
	if filters.get(option) != '' : 
		filter_string += "&filter[{}]={}".format(option, filters.get(option))

note_filters = config["notes"]
notesBoolean = note_filters.get("notes")
notesLength = note_filters.get("notesLength")
note_string = "?filter[notes]={}&filter[notesLength]={}".format(notesBoolean, notesLength)

# Building the API query URL
checks_url = "https://{}-api.cloudconformity.com/v1/checks".format(region)
all_checks_url = "{}{}{}".format(checks_url, parameter_string, filter_string)
headers = {
	'Authorization' : 'ApiKey {}'.format(apiKey),
	'Content-Type' : 'application/vnd.api+json'
}

# launch the request session
session = requests.session()

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

# Establish a list for the final report data
report_data = []

# Query each check to extract suppression data
print("Retrieving all relevant checks based on config file...")
pages_combined = get_account_checks()
print("DONE")
returned_checks = pages_combined["data"]

print("Initiating process to retrieve each check's details...")
check_count = 0
for check in returned_checks:

	checkId = check["id"]
	specific_check_url = "{}/{}{}".format(checks_url, checkId, note_string)

	# Retrive the data for the specific check
	retrieve = session.get(specific_check_url, headers=headers)
	print("API response:" + str(retrieve.status_code) + " for check: " + checkId)
	
	# Build the data dictionary for the report output
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
	
	# Append check data to report data
	report_data.append(reportDictionary)
	check_count += 1

# Confirming report output
totalChecks = len(report_data)
print("Report data compiled for a total of {} checks".format(check_count))

timestamp = time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime())
keys = report_data[0].keys()
with open("suppression_report_{}.csv".format(timestamp), "w", newline="")  as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(report_data)
