jirapythonexcel is a utiity to easily and quickly download jira issues in an excel file

Before using this utility, ensure that the environ.properties file is populated with the required jira project details. It takes in the following four values and all are mandatory:
server - > add the jira server URL
username -> username with permissions to access the jira project
apitoken -> apitoken with permissions to access the jira project
projectkey -> project for which issues need to be fetched

You can easily fetch issues for the sprint or the release (fixversion) using the provided functions.
