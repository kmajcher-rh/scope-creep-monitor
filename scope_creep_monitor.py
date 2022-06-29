# List of all fields in given jira instance (redhat one in this case) - for finding where is the information you want to use in script
# https://issues.redhat.com/rest/api/2/field

# how to check what is the format of results of your query - make it a json and limit results to one row, print() it and analyze
# https://stackoverflow.com/questions/56240480/custom-field-unable-to-read-value-class-jira-resources-propertyholder
#   jira.search_issues('project=FSD', maxResults=1,json_result=True)

# epic.fields.summary == EPIC NAME
# epic.key - jira item number (CNV-xxxxx)
# customfield_12310243  == Story Points!

from jira import JIRA
import json
import smtplib
from email.message import EmailMessage

scopeLock = {'CNV-14405': 29, 'CNV-5810': 24, 'CNV-15705': 36, 'CNV-11991': 19, 'CNV-13992': 21, 'CNV-15404': 52, 'CNV-17857': 25, 'CNV-15418': 30, 'CNV-15517': 68, 'CNV-12541': 26, 'CNV-17012': 
72, 'CNV-15174': 10, 'CNV-15656': 122, 'CNV-15826': 31, 'CNV-15811': 56}


def issues_in_epic(epic):
    items = jira.search_issues('issuekey in childIssuesOf("' + epic + '") AND component = "CNV Install, Upgrade and Operators" AND issuetype = Story AND status != Obsolete AND status != "Won\'t Fix / Obsolete"')
    return items

def all_epics_in_release():
    items=jira.search_issues('type = epic AND component = "CNV Install, Upgrade and Operators" AND (fixVersion = "CNV v4.12.0") AND status != Obsolete AND status != "Won\'t Fix / Obsolete" ORDER BY priority')
    return items

def show_story_with_SP(story):
    print("\t",story.key, story.fields.summary, "'", story.fields.customfield_12310243, "'")    
    pass

def epicSizeinSP(epic):
    spSum = 0.0
    stories = issues_in_epic(epic.key)
    for story in stories:
        strSP= str(story.fields.customfield_12310243)        
        if strSP != 'None':    #to catch unsized stories            
            spSum += float(strSP)
        else:  
            #print("Unsized story: ", story.key) # for now I don't care
            pass
    return int(spSum)


def send_email(sender, recipient, message):
    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = "ScopeCreepAutomation run"
    msg['From'] = sender
    msg['To'] = recipient

    # Send the message via our own SMTP server.
    s = smtplib.SMTP('smtp.corp.redhat.com')
    s.send_message(msg)
    s.quit()

if __name__ == '__main__':
    file=open('configuration.json', 'r')
    config =json.load(file)  

    jira = JIRA(
        server=config['server'],
        token_auth=config['token_auth']
    )

    release_baseline = []

    epics=all_epics_in_release()
   
    sumOfEpicSizesinSP = 0

    for epic in epics:
        epicSP=epicSizeinSP(epic)
        sumOfEpicSizesinSP+=epicSP
        #print(epic.key, " ",epic.fields.summary, "Size:\t", epicSP)   
        if epicSP > scopeLock[epic.key]:
            print("Scope change: ", epic.key, " ",epic.fields.summary,  " \tOrginal/current size: "  ,  str(scopeLock[epic.key])  + "/" + str(epicSP))
        # stories = issues_in_epic(epic.key)
        # for story in stories:
        #     show_story_with_SP(story)
    print("Sum of all processed epics is: ", sumOfEpicSizesinSP , " SP")
    send_email("kmajcher@redhat.com", "kmajcher@redhat.com", "test message")


    #smtp.corp.redhat.com 