import boto3
import json

region_name = 'ap-south-1'
key = "551"
security_group_ids = "sg-0b4256d9673173ab5"

Domain_Name = "domain"
user_count = 1
Subscription_plan = "basic"

def lambda_handler(event, context):
    # Create an EC2 client
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
        SecurityGroupIds=security_group_ids,
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
    waiter = ec2.get_waiter('instance_running')
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

# Uncomment the following line if you want to return the serialized instance as the Lambda function result
# return serialized_instance
