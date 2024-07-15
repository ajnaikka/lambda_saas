import boto3
import base64

def lambda_handler(event, context):
    source_repo = 'saas'
    target_repo = 'domain'
    branch_name = 'domain'  # Optional

    client = boto3.client('codecommit')

    # Clone the source repo locally
    source_repo_metadata = client.get_repository(repositoryName=source_repo)
    clone_url = source_repo_metadata['repositoryMetadata']['cloneUrlHttp']

    # Create the target repo
    client.create_repository(repositoryName=target_repo)

    # Push changes to the target repo
    file_content = f'your content here'  # write ur content here


    client.put_file(
        repositoryName=target_repo,
        branchName=branch_name,
        filePath='/src',  # You need to specify a file path
        fileContent=file_content,
        fileMode='NORMAL'
    )

    return {
        'statusCode': 200,
        'body': 'Code cloned and pushed successfully!'
    }
