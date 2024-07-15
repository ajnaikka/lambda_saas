import boto3

def lambda_handler(event, context):
    source_repo = 'saas'
    target_repo = 'domain'
    branch_name = 'domain'  # Optional

    client = boto3.client('codecommit')

    # Clone the source repo locally
    a = client.get_repository(repositoryName=source_repo)  # Triggers local clone
    client.create_repository(repositoryName=target_repo)
    #client.delete_repository(repositoryName=target_repo)  # to delte a repository


    # Push changes to the target repo
    client.put_file(
        repositoryName=target_repo,
        branchName=branch_name,
        filePath='/',
        fileContent= a,
        fileMode='NORMAL'
    )

    return {
        'statusCode': 200,
        'body': 'Code cloned and pushed successfully!'
    }
