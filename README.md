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
    
### Implementation notes
Users can alter the report dictionary within the script's final for loop to change the contents of the final report.

For reference, below is an example response from the 'Get Check Details' command which forms the basis of the final report.  

    {
        "data": {
            "type": "checks",
            "id": "ccc:e1234fad-1234-1234-1234-1234f2589a17:S3-026:S3:global:example-public-bucket-1234",
            "attributes": {
                "region": "global",
                "status": "FAILURE",
                "risk-level": "VERY_HIGH",
                "pretty-risk-level": "Very High",
                "message": "S3 Bucket example-public-bucket-1234 does not have S3 Block Public Access feature enabled.",
                "resource": "example-public-bucket-1234",
                "descriptorType": "s3-bucket",
                "link-title": "example-public-bucket-1234",
                "resourceName": "S3 Bucket",
                "last-modified-date": 1624309659393,
                "created-date": 1623906719224,
                "categories": [
                    "security"
                ],
                "suppressed": true,
                "failure-discovery-date": 1623906719224,
                "ccrn": "ccrn:aws:e1234fad-1234-1234-1234-1234f2589a17:S3:ap-southeast-2:example-public-bucket-1234",
                "extradata": [
                    {
                        "name": "LocationConstraint",
                        "label": "LocationConstraint",
                        "type": "META",
                        "value": "ap-southeast-2"
                    }
                ],
                "tags": [
                    "S3Bucket::Tag"
                ],
                "cost": 0,
                "waste": 0,
                "suppressed-until": null,
                "notes": [
                    {
                        "createdBy": "XYZQWERTY123",
                        "created-date": 1624309662534,
                        "note": "Ticket-123 - Plan of action Suppression Example"
                    }
                ],
                "excluded": false,
                "rule-title": "Enable S3 Block Public Access for S3 Buckets",
                "link": "https://s3.console.aws.amazon.com/s3/buckets/example-public-bucket-1234/?region=ap-southeast-2&tab=overview",
                "provider": "aws",
                "resolution-page-url": "https://www.cloudconformity.com/knowledge-base/aws/S3/bucket-public-access-block.html#XYZIUYTRE123"
            },
            "relationships": {
                "rule": {
                    "data": {
                        "type": "rules",
                        "id": "S3-026"
                    }
                },
                "account": {
                    "data": {
                        "type": "accounts",
                        "id": "e1234fad-1234-1234-1234-1234f2589a17"
                    }
                }
            }
        }
    }
    
### Contribution
Feedback on this soltuion is always welcome!
