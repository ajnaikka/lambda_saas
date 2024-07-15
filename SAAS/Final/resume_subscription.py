import boto3
import jenkins
import xml.etree.ElementTree as ET


Domain_Name = "lkj"
instance_name= Domain_Name
record_name = Domain_Name + '.odoo.loyalerp.in'

username = "admin"
password = "11484c137b9c977ecd73e01970c027a790"
host = "http://jenkins.loyalerp.in/"


def start_instances(event, context):
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
        
        
        
def update_r53_record(event, context, record_value):

    hosted_zone_id = 'Z03385962MSG1UDU36OBK'

    # Create Route 53 client
    route53 = boto3.client('route53')
    # Create DNS record
    response = route53.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch={
            'Changes': [
                {
                    'Action': 'UPSERT',
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
            'body': 'updated R53 record successfully!'
        }


def jenkins_job(username, password, host):

    job_name = Domain_Name
    server = jenkins.Jenkins(host, username=username, password=password)

    branch_specifier = "refs/heads/production"

    existing_config = server.get_job_config(job_name)
    tree = ET.fromstring(existing_config)

    name_element = tree.find(".//hudson.plugins.git.BranchSpec/name")
    if name_element is not None:
        name_element.text = branch_specifier

    updated_config = ET.tostring(tree, encoding='utf8', method='xml').decode()

    server.reconfig_job(job_name, updated_config)

    params = {
              'jenkins_job_name': Domain_Name,
              'branch': branch_specifier,
              'ANSIBLE_HOST': record_name,
              'sector': ""
              }

    server.build_job(job_name, parameters=params)


        
def lambda_handler(event, context):
    
    start_ec2 = start_instances(event, context)
    print (start_ec2)
    
    record_value = start_ec2[0]
    
    update_r53 = update_r53_record(event, context, record_value)
    print(update_r53_record)

    trigger = jenkins_job(username, password, host)
    print (trigger)
    