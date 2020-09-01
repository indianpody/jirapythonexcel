import pandas as pd
from jira import JIRA, JIRAError
import logging
import os
from pandas import ExcelWriter
from configparser import ConfigParser

# set root directory and configuration file paths
ROOT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE_PATH = os.path.join(ROOT_DIRECTORY, "environ.properties")

# initialize logger
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger(__name__)

# read the environ.properties file and store the configuration values in local variables
config = ConfigParser()
config.read(CONFIG_FILE_PATH)
server = config.get('jira', 'server')
username = config.get('jira', 'username')
apitoken = config.get('jira', 'apitoken')
projectkey = config.get('jira', 'projectkey')

def loginJira():
    """
    The loginJira function establishes connection with JIRA. It uses the jira details stored in environ.properties file
    :parameter - none
    :rtype: jira object which can be used for further interaction with jira.
    """
    try:
        options = {'server': server}
        jira = JIRA(options, basic_auth=(username, apitoken))
        log.info("Successfully logged in jira project: " + projectkey)
        return jira
    except JIRAError as e:
        log.error(e.status_code, e.text)
        return "Error"
    except Exception as e:
        log.error("Unhandled exception")
        log.error(e)
        return "Error"


def getJiraIssues(jql):
    """
    The getJiraIssues function fetches issue details from jira based on the JQL provided
    :parameter
    jql: takes the JQL string which will be used to fetch jira issues
    :rtype: jira object which can be used for further interaction with jira.
    """
    try:
        log.info("Creating empty dataframe to store the jira responses")
        issuedf = pd.DataFrame()
        jira = loginJira()
        if jira == "Error":
            log.error("Could not log into JIRA. Please investigate the loginJIRA() function")
        else:
            log.info("Logged in to the jira project using the information defined in the environ.properties file")
        issues = jira.search_issues(jql, startAt=0, maxResults=2000)
        log.info("Fetched jira issues as per the defined jql: " + jql)
        log.info("Start looping through the jira response to unpack it and append the dataframe with results")
        for issue in issues:

            # Parsing the jira sprint object to extract the sprint name
            if issue.fields.customfield_10020 is not None:
                issuesprintobject = str(issue.fields.customfield_10020)
                issuesprintarray = issuesprintobject.split(',')
                if len(issuesprintarray) > 1:
                    issuesprint = issuesprintarray[4].split('=')
                    issuesprint = issuesprint[1]
                else:
                    issuesprint = ""
            else:
                issuesprint = ""

            if issue.fields.fixVersions is not None:
                releasename = issue.fields.fixVersions
            else:
                releasename = ""
            # set value of parent key depending on whether the issue is a sub-task or a parent itself
            if issue.fields.issuetype.name == "Sub-task":
                parentkey = issue.fields.parent.key
            else:
                parentkey = issue.key
            # if issue.fields.customfield_10026 in issue:
            #     issuestorypoint = issue.fields.customfield_10026
            # else:
            #     issuestorypoint = 0

            # adding values to a dictionary
            issuelist = {
                'Project_Key': issue.fields.project.key,
                'Parent_Key': parentkey,
                'Issue_Key': issue.key,
                'Issue_Type': issue.fields.issuetype.name,
                'Issue_Summary': issue.fields.summary,
                'Components': issue.fields.components,
                'Priority': issue.fields.priority,
                'Assignee': issue.fields.assignee,
                'Story_Point': '0',
                'Original_Estimate': issue.fields.timeoriginalestimate,
                'Remaining_Estimate': issue.fields.timeestimate,
                'Time_Spent': issue.fields.timespent,
                'Issue_Sprint': issuesprint,
                'Issue_Labels': issue.fields.labels,
                'Fix_Version': releasename
            }
            log.info("Added details of jira issue to the dataframe with issue key: " + issuelist['Issue_Key'])
            issuedf = issuedf.append(issuelist, ignore_index=True)
        return issuedf
    except JIRAError as e:
        log.error(e.status_code, e.text)
        return "Error"
    except Exception as e:
        log.error("Unhandled exception")
        log.error(e)
        return "Error"


def writeToExcel(dataframe, filename, sheetname):
    """
    The writeToExcel function writes the dataframe into a specific worksheet of an excel file
    :parameter
    dataframe: takes the dataframe name that needs to be written
    filename: takes the excel file name with .xls extension to which dataframe content is written
    sheetname: takes the worksheet name of the file to which dataframe content is written
    :rtype: boolean values true or false.
    """
    try:
        writer = ExcelWriter(filename)
        dataframe.to_excel(writer, sheetname)
        writer.save()
        return True
    except Exception as e:
        log.error("Unhandled exception")
        log.error(e)
        return False


def getJiraIssuesInSprint(sprintid, subtasksflag):
    """
    The getJiraIssuesInSprint function is used to get all the issues in a jira sprint
    :parameter
    sprintnumber: takes the sprint id for which issues need to be fetched
    subtasksflag: takes true or false and is used to tell the function if sub-task details
    should be included in the result.
    """
    try:
        if subtasksflag:
            jql = 'project = ' + config['jira']['projectkey'] + ' AND sprint = ' + sprintid + ' AND type in (story,bug,task,sub-task)'
        else:
            jql = 'project = ' + config['jira']['projectkey'] + ' AND sprint = ' + sprintid + ' AND type in (story,bug,task)'
        log.info("JQL created for querying jira project: " + jql)
        sprintissuesdf = getJiraIssues(jql)
        if isinstance(sprintissuesdf, pd.DataFrame):
            writefilesuccessflag = writeToExcel(sprintissuesdf, 'Sprint_Issues.xlsx', 'sprint_Issues')
            if writefilesuccessflag:
                log.info("Successfully created the sprint issues excel file for sprint id: " + sprintid)
            else:
                log.error("File writing is un-successfull for sprint issues. Please investigate the writeToExcel() function.")
        else:
            log.error("Could not fetch sprint issues. Please investigate the getJiraIssues() function")
    except JIRAError as e:
        log.error(e.status_code, e.text)
        log.error("Could not fetch sprint issues. Please investigate the getJiraIssuesInSprint() function")
    except Exception as e:
        log.error("Unhandled exception")
        log.error(e)


def getJiraIssuesInRelease(releasename):
    """
    The getJiraIssuesInRelease function is used to get all the issues in a jira sprint
    :parameter
    releasename: takes the fix version name for which issues need to be fetched
    """
    try:
        jql = 'project = ' + config['jira'][
                'projectkey'] + ' AND fixVersion = ' + "'" + releasename + "'" + ' AND type in (story,bug,task)'
        log.info("JQL created for querying jira project: " + jql)
        releaseissuesdf = getJiraIssues(jql)
        if isinstance(releaseissuesdf, pd.DataFrame):
            writefilesuccessflag = writeToExcel(releaseissuesdf, 'Release_Issues.xlsx', 'release_Issues')
            if writefilesuccessflag:
                log.info("Successfully created the release issues excel file for fix version: " + releasename)
            else:
                log.error("File writing is un-successfull for release issues. Please investigate the writeToExcel() function.")
        else:
            log.error("Could not fetch release issues. Please investigate the getJiraIssues() function")
    except JIRAError as e:
        log.error(e.status_code, e.text)
        log.error("Could not fetch release issues. Please investigate the getJiraIssuesInRelease() function")
    except Exception as e:
        log.error("Unhandled exception")
        log.error(e)


def main():
    getJiraIssuesInSprint('1', True)
    getJiraIssuesInRelease('Release One')


if __name__ == "__main__":
    main()
