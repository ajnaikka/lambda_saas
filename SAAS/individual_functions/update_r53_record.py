import boto3

# These variable are hard-coded for  testing.

hosted_zone_id = 'Z03385962MSG1UDU36OBK'
record_name = 'loayl.odoo.loyalerp.in'
record_value = '3.110.127.225'

def lambda_handler(event, context):
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

    # return response

def lambda_handler(event, context):
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