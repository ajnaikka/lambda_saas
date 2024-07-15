import jenkins
import json
import os
import boto3
import requests


def lambda_handler(event, context):

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

    username = os.environ['username']
    password = os.environ['password']
    host = os.environ['host']
    job_name = os.environ['job_name']

    server = jenkins.Jenkins(host, username=username, password=password) #automation_user_password

    user = server.get_whoami()
    version = server.get_version()
    print('Hello %s from Jenkins %s' % (user['fullName'], version))


    commit = event['Records'][0]['codecommit']['references'][0]['commit']
    repo_name = event['Records'][0]['codecommit']['references'][0]['repositoryName']
    user_name = event['Records'][0]['codecommit']['references'][0]['userName']
    branch = event['Records'][0]['codecommit']['references'][0]['ref']
    commit_message = event['Records'][0]['codecommit']['references'][0]['commitMessage']
    params = {'commit_id': commit,
              'repo_name': repo_name,
              'email': user_name,
              'branch': branch,
              'commit_message': commit_message
              }

    # Run a build 
    server.build_job(job_name, parameters=params)

    # Get build number
    last_build_number = server.get_job_info(job_name)['lastCompletedBuild']['number']
    Current_build_number = int(last_build_number) + 1
    print("Build Number", Current_build_number )

    # Get build info
    build_info = server.get_build_info(job_name, last_build_number)
    print("build info", build_info) 


    print("Event Payload:")
    print(json.dumps(event))


    
    

