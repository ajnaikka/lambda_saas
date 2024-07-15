import boto3


Domain_Name = "xyz"
instance_name= Domain_Name


def stop_instances(event, context):
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
        stop_response = ec2.stop_instances(InstanceIds=instances)
        
        # Print the response
        print(stop_response)

        return {
            'statusCode': 200,
            'body': f'EC2 instances with tag {tag_key}:{tag_value} stopping request sent successfully!'
        }
    else:
        return {
            'statusCode': 404,
            'body': f'No EC2 instances found with tag {tag_key}:{tag_value}.'
        }

def lambda_handler(event, context):

    response = stop_instances(event, context)
    print (response)