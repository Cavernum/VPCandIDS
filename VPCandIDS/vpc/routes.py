import boto3

ec2 = boto3.client('ec2')

def create_public_route(vpc_id, dest_cidr, int_gw_id, tags_key, tags_value):
    tableRoutage = ec2.create_route_table(
        VpcId=vpc_id,
        TagSpecifications=[
            {
                'ResourceType': 'route-table',
                'Tags': [
                    {
                        'Key': tags_key,
                        'Value': tags_value
                    },
                ]
            },
        ]
    )
    
    rt_id = tableRoutage["RouteTable"]["RouteTableId"]

    response_route = ec2.create_route(
        DestinationCidrBlock=dest_cidr,
        GatewayId=int_gw_id,
        RouteTableId=rt_id,
    )

    # print("Create Public Route to Internet Gateway Responce")
    # print(response_route, "\n")

    return tableRoutage



def create_private_route(vpc_id, dest_cidr, nat_gw_id, tags_key, tags_value):
    tableRoutage = ec2.create_route_table(
        VpcId=vpc_id,
        TagSpecifications=[
            {
                'ResourceType': 'route-table',
                'Tags': [
                    {
                        'Key': tags_key,
                        'Value': tags_value
                    },
                ]
            },
        ]
    )
    rt_id = tableRoutage["RouteTable"]["RouteTableId"]
    ec2.create_route(
        DestinationCidrBlock=dest_cidr,
        GatewayId=nat_gw_id,
        RouteTableId=rt_id,
    )
    return tableRoutage


def association_tableRoutage_subnet(rt_id, subnet_id):
    association = ec2.associate_route_table(
        RouteTableId=rt_id,
        SubnetId=subnet_id,
    )
    return association
