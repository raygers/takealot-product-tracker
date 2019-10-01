# Takealot Product Price Tracker

## Description
---
An AWS cloud based serverless solution for tracking Takealot product prices.

The solution will create an API which you can use to create users and add a list of Takealot products to be tracked.

A task will run twice a day to update the tracked prices.

The solution will create the following resources on AWS:
1. API Gateway Enpdoint.
2. API Lambda function to process all API requests
3. Lambda function which will be triggered twice a day by a cloudwatch scheduled event.
4. DynamoDB Table.
5. API key stored in AWS Key Management Service

## Development Environment prerequisites
---
1. Python 3.7
2. Latest version of pip3
3. NodeJs 10.X.X
4. Serverless framework (installed by setup script)

## Setup
---
1. Clone this repo
2. Change the execute permissions of the setup_env.sh. Run chmod u+x {path-to-file}/setup_env.sh
3. Run {path-to-file}/setup_env.sh to setup the environment and install the necessary packages.

## Configuration
---
The aws configuration in the severless.yml has been configured to use an AWS configured profile. If you only have a default profile configured on your system, you can remove the " profile: private" config setting from provider section of serverles.yml file.

If you have more than one prfile configured, change the value of the profile setting to the name of the profile you wish to use. Remember to set the profile environment variable in your console session to use the desired profile. This can be done by running the following command:

```javascript
export AWS_PROFILE=private
```

## Deployment
---
- Run "sls deploy" from the command line. 

This will create the stack on AWS. Once the stack has been created, the generated API endpoints will be ouputted to the console. The API endpoints will now be available to consume by postman or by a web GUI.

## Run API locally
---
To test the API locally, you can run the flask application by running the following comand:
```javascript
sls wsgi serve
```
Once the app has launched, you can test the API at http://localhost:5000/

## Testing
Import and run the postman collection.
