import boto3

ec2 = boto3.client('ec2')

def create_gateway_perso(subnet_id, tags_key_ip, tags_value_ip, tags_key_nat, tags_value_nat):
    eip_allocation = ec2.allocate_address(
        Domain='vpc',
        TagSpecifications=[
            {
                'ResourceType': 'elastic-ip',
                'Tags': [
                    {
                        'Key': tags_key_ip,
                        'Value': tags_value_ip
                    },
                ]
            },
        ]
    )

    eip_id = eip_allocation["AllocationId"]
    
    natGateway = ec2.create_nat_gateway(
        AllocationId=eip_id,
        SubnetId= subnet_id,
        TagSpecifications=[
            {
                'ResourceType': 'natgateway',
                'Tags': [
                    {
                        'Key': tags_key_nat,
                        'Value': tags_value_nat
                    },
                ]
            },
        ],
    )
    return natGateway

def attach_gateway(vpc_id, tags_key, tags_value):
    ig = ec2.create_internet_gateway(   #création du Internet Gateway
        TagSpecifications=[
            {
                'ResourceType': 'internet-gateway',
                'Tags': [
                    {
                        'Key': tags_key,
                        'Value': tags_value
                    },
                ]
            },
        ],
    )

    ig_id = ig["InternetGateway"]["InternetGatewayId"]
    response = ec2.attach_internet_gateway(
        InternetGatewayId= ig_id,
        VpcId=vpc_id,
    )
    print("Attach Internet Gateway to VPC Response")
    print(response, "\n")
    print(ig_id)

    return response, ig_id