# Conformity-Suppression-Report
Builds a CSV report to extract suppression data for individual checks

## Solution Use Case
Conformity users may choose to use the Conformity check 'suppression' feature to record audit notes or pre-remediation notes.  
For example, this could be a note recording the ID of a Jira ticket stored in a separate remediation project.  
This script allows users to extract the check data including the suppression note and publish them to a csv report.

Check suppression help guide: https://www.cloudconformity.com/help/rules/model-check/suppress-check.html 

## Usage
The script uses python 3 and requires a Conformity API key set as environment variable. 
Ensure the user for the API has mininum read-only access to all accounts listed.  
Create Conformity API Key https://www.cloudconformity.com/help/public-api/api-keys.html  

    $ export CC_API_KEY="XXXXXXYYYYYZZZ678768768687IIUUYYTTRREEWWQQ"
    
The filter options for the checks API are found here: https://cloudone.trendmicro.com/docs/conformity/api-reference/tag/Checks  
The user must define parameters and the chosen filters in the 'request-config.ini' file.  
Conformity AccountIds can be retrieved from accounts API https://cloudone.trendmicro.com/docs/conformity/api-reference/tag/Accounts  
For example, this can be done with a solution such as this: https://github.com/KW-Cloud-Tech/ConformityAccountMapping  
Once the config file is configured, the script can be run locally and will produce a timestamped csv file in the same folder

    $ python generate-report.py 
    
### Contribution
Feedback on this soltuion is always welcome!
