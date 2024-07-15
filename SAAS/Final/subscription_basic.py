import boto3
import json
import jenkins
import xml.etree.ElementTree as ET


#input from user, thses valuse are fetched from frontend website through webhook
Domain_Name = "xyz"
record_name = Domain_Name + ".odoo.loyalerp.in"
user_count = 1
Subscription_plan = "basic"
sector = "sector"

# metadata for ec2 creation
region_name = 'ap-south-1'
key = "551"
security_group_ids = "sg-0b4256d9673173ab5" #constant odoo-sg created from console

#jenkins credentials hardcoded for testing purposes
username = "admin"
password = "11484c137b9c977ecd73e01970c027a790"
host = "http://jenkins.loyalerp.in/"

#repo details for jenkins scm polling
repo_url = "git@github.com:ajnaikka/saas_basic.git" #repo url for jenkins scm polling
branch_specifier= "refs/heads/main" #branch to build
script_path = "jenkins" #jenkins script path

# fucntion to provision ec2

def create_ec2(user_count, Domain_Name, key, security_group_ids):
    ec2 = boto3.client('ec2', region_name=region_name)
    
    # Determine instance type based on user_count
    if 1 <= user_count <= 3:
        instance_type = 't2.micro'
    elif 4 <= user_count <= 6:
        instance_type = 't2.medium'
    else:
        # You may want to handle other user_count ranges accordingly
        raise ValueError("Unsupported user_count.")
    
    ami_id = 'ami-03f4878755434977f' 
    
    # Create an EC2 instance
    instance = ec2.run_instances(
        ImageId=ami_id,
        InstanceType=instance_type,
        MinCount=1,
        MaxCount=1,
        KeyName=key,
        SecurityGroupIds=[security_group_ids],
        IamInstanceProfile={
            'Name': 'ec2-s3'
        },
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': Domain_Name  # Replace with your desired instance name
                    },
                    # Add more tags as needed
                ]
            },
        ]
    )
    
    # Wait until the instance is running
    instance_id = instance['Instances'][0]['InstanceId']
    waiter = ec2.get_waiter('instance_status_ok')   #instance_running
    waiter.wait(InstanceIds=[instance_id])


    
    # Fetch the public IP address
    instance_info = ec2.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]
    public_ip_address = instance_info.get('PublicIpAddress', 'N/A')
    print(public_ip_address)
    
    # Convert datetime objects to strings in the response
    if 'LaunchTime' in instance_info:
        instance_info['LaunchTime'] = instance_info['LaunchTime'].strftime('%Y-%m-%d %H:%M:%S')

    # Serialize the response
    serialized_instance = json.dumps(instance_info, default=str)

    # Return the serialized response
    print(json.dumps(serialized_instance))
    return public_ip_address
    
#function to create dnc record

def create_dns_record(hosted_zone_id, record_name, record_value):
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
        'body': 'DNS record created successfully!'
    }


#function to create and build jenkins job

def jenkins_job(username, password, host):


    job_name = Domain_Name
    server = jenkins.Jenkins(host, username=username, password=password) #automation_user_password

    xml_string = """
      <?xml version='1.1' encoding='UTF-8'?>
      <flow-definition plugin="workflow-job@2.43">
        <actions/>
        <description>My Jenkins Pipeline</description>
        <keepDependencies>false</keepDependencies>
        <properties>
          <hudson.model.ParametersDefinitionProperty>
            <parameterDefinitions>
              <hudson.model.StringParameterDefinition>
                <name>jenkins_job_name</name>
                <description>jenkins_job_name</description>
                <defaultValue>{jenkins_job_name}</defaultValue>
              </hudson.model.StringParameterDefinition>
              <hudson.model.StringParameterDefinition>
                <name>sector</name>
                <description>sector</description>
                <defaultValue>{sector}</defaultValue>
              </hudson.model.StringParameterDefinition>
              <hudson.model.StringParameterDefinition>
                <name>branch</name>
                <description>branch to build</description>
                <defaultValue>{branch_specifier}</defaultValue>
              </hudson.model.StringParameterDefinition>
              <hudson.model.StringParameterDefinition>
                <name>ANSIBLE_HOST</name>
                <description>url of deploy server</description>
                <defaultValue>{ANSIBLE_HOST}</defaultValue>
              </hudson.model.StringParameterDefinition>
            </parameterDefinitions>
          </hudson.model.ParametersDefinitionProperty>
        </properties>
        <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps@2.91">
          <scm class="hudson.plugins.git.GitSCM" plugin="git@4.2.2">
            <configVersion>2</configVersion>
            <userRemoteConfigs>
              <hudson.plugins.git.UserRemoteConfig>
                <url>{repo_url}</url>
              </hudson.plugins.git.UserRemoteConfig>
            </userRemoteConfigs>
            <branches>
              <hudson.plugins.git.BranchSpec>
                <name>{branch_specifier}</name>
              </hudson.plugins.git.BranchSpec>
            </branches>
            <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
            <submoduleCfg class="list"/>
            <extensions/>
          </scm>
          <scriptPath>{script_path}</scriptPath>
        </definition>
        <triggers/>
        <disabled>false</disabled>
      </flow-definition>
      """.format(repo_url=repo_url, branch_specifier=branch_specifier, script_path=script_path, jenkins_job_name=Domain_Name,branch=branch_specifier,ANSIBLE_HOST=record_name,sector=sector)

   # server.create_job(job_name,config)
    xml_string_stripped = xml_string.strip()
    tree = ET.fromstring(xml_string_stripped)
    config = ET.tostring(tree, encoding='utf8', method='xml').decode()
 
    params = {
              'jenkins_job_name': Domain_Name,
              'branch': branch_specifier,
              'ANSIBLE_HOST': record_name,
              'sector': sector
              }
    
    server.create_job(job_name, config)
    server.build_job(job_name, parameters=params)

    return {
        'statusCode': 200,
        'body': 'Jenkins job created and triggered successfully!'
    }


def create_repo(event, context):
    

    repo_name = Domain_Name

    client = boto3.client('codecommit')

    # Create the unique repo
    client.create_repository(repositoryName=repo_name)
    # Create repo trigger
    client.put_repository_triggers(
    repositoryName=repo_name,
            triggers=[
                {
                    'name': repo_name,
                    'destinationArn': 'arn:aws:lambda:ap-south-1:093407068366:function:jenkins_trigger', # replace with existing lambda function
                    'customData': 'string',
                    'branches': [
                        'production','staging',
                    ],
                    'events': [
                        'updateReference',
                    ]
                },
            ]
        )
            
    return {
        'statusCode': 200,
        'body': 'Repository created successfully!'
    }


# lambda_handler entry point

def lambda_handler(event, context):

    # Create an EC2 client
    ec2_response = create_ec2(user_count, Domain_Name, key, security_group_ids)
    print(ec2_response)
    record_value = ec2_response
    
    hosted_zone_id = 'Z03385962MSG1UDU36OBK' #created from console
    

    r53_responce = create_dns_record(hosted_zone_id, record_name, record_value)
    print(r53_responce)
    
    jenkins= jenkins_job(username, password, host)
    print(jenkins)

    cc = create_repo(event, context)
    print(cc)