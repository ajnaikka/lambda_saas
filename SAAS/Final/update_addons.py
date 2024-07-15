import jenkins
import json
import os
import boto3
import xml.etree.ElementTree as ET


sector = "sector"

def codecommit(event, context):

    commit_info = {}

    # Access repository and commit information if available
    if 'Records' in event and len(event['Records']) > 0:
        record = event['Records'][0]

        if 'eventSourceARN' in record:
            # Extract repository name from event source ARN
            arn_parts = record['eventSourceARN'].split(':')
            repository_name = arn_parts[-1]
            print("Repository Name:", repository_name)
            commit_info['repositoryName'] = repository_name

        if 'codecommit' in record and 'references' in record['codecommit']:
            references = record['codecommit']['references']
            for ref in references:
                if 'commit' in ref:
                    commit_id = ref['commit']
                    print("Commit ID:", commit_id)
                    commit_info['commitID'] = commit_id

        if 'userIdentityARN' in record:
            # Extract repository name from event source ARN
            arn_parts = record['userIdentityARN'].split(':')
            user_name = arn_parts[-1]
            print("User Name:", user_name)
            user = user_name.split('/')
            print("user:", user[-1])
            commit_info['userName'] = user[-1]


    codecommit_client = boto3.client('codecommit')
    response = codecommit_client.get_commit(repositoryName=repository_name, commitId=commit_id)
    commit_message = response['commit']['message']
    commit_info['commitMessage'] = commit_message

    # Append commit_info to references list
    #references.append(commit_info)
    references[0].update(commit_info)
    
    # Extract the HTTPS clone URL from the repository information
    repo_info = codecommit_client.get_repository(repositoryName=repository_name)
    repo_url = repo_info['repositoryMetadata']['cloneUrlSsh']


    # variables to be used in jenkins
    commit = event['Records'][0]['codecommit']['references'][0]['commit']
    repo_name = event['Records'][0]['codecommit']['references'][0]['repositoryName']
    user_name = event['Records'][0]['codecommit']['references'][0]['userName']
    branch = event['Records'][0]['codecommit']['references'][0]['ref']
    commit_message = event['Records'][0]['codecommit']['references'][0]['commitMessage']

    return  repo_name, branch, repo_url, commit, user_name, commit_message
    


def trigger_jenkins(repo_name, branch, new_repo_url,commit, user_name,commit_message):

    username = "admin"
    password = "11484c137b9c977ecd73e01970c027a790"
    host = "http://jenkins.loyalerp.in/"
    job_name = repo_name

    server = jenkins.Jenkins(host, username=username, password=password) #automation_user_password

    # Get the existing job configuration
    existing_config = server.get_job_config(job_name)
    
    new_script_path = "jenins#2"
    new_branch_specifier = branch
   

    # Parse the existing configuration XML
    tree = ET.fromstring(existing_config)

    # Update the branch specifier
    name_element = tree.find(".//hudson.plugins.git.BranchSpec/name")
    if name_element is not None:
        name_element.text = new_branch_specifier

    # Update the repository URL and script path
    for child in tree.iter():
        if child.tag == 'url':
            child.text = new_repo_url
        elif child.tag == 'scriptPath':
            child.text = new_script_path

    print(tree)
    # Convert the modified XML back to a string
    updated_config = ET.tostring(tree, encoding='utf8', method='xml').decode()
    print (updated_config)

    # Update the job with the modified configuration
    server.reconfig_job(job_name, updated_config)

    record_name = repo_name + ".odoo.loyalerp.in"
    sector = "null"

    params = {'commit_id': commit,
              'repo_name': repo_name,
              'email': user_name,
              'branch': branch,
              'commit_message': commit_message
              }
    params1 = {
              'jenkins_job_name': repo_name,
              'branch': new_branch_specifier,
              'ANSIBLE_HOST': record_name,
              'sector': sector
              }

    # Run a build 
    server.build_job(job_name, parameters=params1)


def lambda_handler(event,context):

    variables = codecommit(event, context)

    repo_name = variables[0]
    branch = variables[1]
    new_repo_url = variables[2]
    commit = variables[3]
    user_name = variables[4]
    commit_message =variables[5]

    trigger = trigger_jenkins(repo_name, branch, new_repo_url,commit, user_name,commit_message)

    


   

  

    
