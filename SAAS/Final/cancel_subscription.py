import boto3
import jenkins
import json


Domain_Name = "xyz"
instance_name= Domain_Name
record_name = Domain_Name + '.odoo.loyalerp.in'



def fetch_instances_public_ip(event, context):
    # Specify the tag key-value pair to identify the instance
    tag_key = 'Name'
    tag_value = instance_name

    # Create an EC2 client
    ec2 = boto3.client('ec2')

    # Get a list of instances with the specified tag
    response = ec2.describe_instances(Filters=[
        {'Name': f'tag:{tag_key}', 'Values': [tag_value]}
    ])

    instances = []
    
    # Extract instance IDs from the response
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances.append(instance['InstanceId'])

    # Start the EC2 instances with the specified tag
    if instances:
        start_response = ec2.start_instances(InstanceIds=instances)



        # Wait for instances to be in the 'running' state
        waiter = ec2.get_waiter('instance_running')
        waiter.wait(InstanceIds=instances)

        # Get public IP addresses of the started instances
        public_ips = []
        for instance_id in instances:
            instance_info = ec2.describe_instances(InstanceIds=[instance_id])
            public_ip = instance_info['Reservations'][0]['Instances'][0].get('PublicIpAddress')
            if public_ip:
                public_ips.append(public_ip)
        
        # Print the response
        print(start_response)
        
        return public_ips

def delete_R53_record(event, context, record_value):

    hosted_zone_id = 'Z03385962MSG1UDU36OBK'

    # Create Route 53 client
    route53 = boto3.client('route53')
        
    # Create DNS record
    response = route53.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch={
            'Changes': [
                {
                    'Action': 'DELETE',   #TO DELETE THE RECORD SET
                    'ResourceRecordSet': {
                        'Name': record_name,
                        'Type': 'A',
                        'TTL': 300,
                        'ResourceRecords': [
                            {'Value': record_value}
                        ]
                    }
                }
            ]
        }
    )
    
    return {
        'statusCode': 200,
        'body': 'R53 record deleted successfully!'
    }


def terminate_instances(event, context):
    # Specify the tag key-value pair to identify the instance
    tag_key = 'Name'
    tag_value = instance_name

    # Create an EC2 client
    ec2 = boto3.client('ec2')

    # Get a list of instances with the specified tag
    response = ec2.describe_instances(Filters=[
        {'Name': f'tag:{tag_key}', 'Values': [tag_value]}
    ])

    instances = []
    
    # Extract instance IDs from the response
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances.append(instance['InstanceId'])

    # Stop the EC2 instances with the specified tag
    if instances:
        terminate_response = ec2.terminate_instances(InstanceIds=instances)
        
        # Print the response
        print(terminate_response)

        return {
        'statusCode': 200,
        'body': 'instance deleted successfully!'
    }

def delete_jenkins_job(event, context):


    username = "admin"
    password = "11484c137b9c977ecd73e01970c027a790"
    host = "http://jenkins.loyalerp.in/"
    job_name = Domain_Name

    server = jenkins.Jenkins(host, username=username, password=password) #automation_user_password

   
    server.delete_job(job_name)  
    
    return {
        'statusCode': 200,
        'body': 'jenkins deleted successfully!'
    }

def delete_repo(event, context):
    

    repo_name = Domain_Name

    client = boto3.client('codecommit')

    # delete the repo
    client.delete_repository(repositoryName=repo_name)
    
    return {
        'statusCode': 200,
        'body': 'repo deleted successfully!'
    }


def lambda_handler(event, context):

    start_ec2 = fetch_instances_public_ip(event, context)
    print (start_ec2)
    
    record_value = start_ec2[0]
    print (record_value)
    
    delete_R53 = delete_R53_record(event, context, record_value)
    print (delete_R53_record)
    
    terminate_ec2 = terminate_instances(event, context)
    print (terminate_ec2)


    delete_jenkins = delete_jenkins_job(event, context)
    print (delete_jenkins_job)

    delete_cc = delete_repo(event, context)
    print(delete_repo)

    print ("service belongs to " +Domain_Name+" is deleted Successfully !! ")



