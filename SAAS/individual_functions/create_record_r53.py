import boto3


Domain_Name = "domain"
record_name = Domain_Name + ".odoo.loyalerp.in"
public_ip_address = "13.232.65.174"
record_value = public_ip_address

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

    return response

def lambda_handler(event, context):
    # Replace these values with your actual ones
    hosted_zone_id = 'Z03385962MSG1UDU36OBK'
    # record_name = 'your_domain_name.com'
    
    # Get the public IP address of the EC2 instance
    instance_ip = public_ip_address

    # Create DNS record in Route 53
    response = create_dns_record(hosted_zone_id, record_name, record_value)

    # Log the response from Route 53
    print(response)

    return {
        'statusCode': 200,
        'body': 'DNS record created successfully!'
    }



