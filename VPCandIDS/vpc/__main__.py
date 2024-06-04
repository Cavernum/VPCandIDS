import boto3
from . import subnets
from . import gateways
from . import routes
import logging
from botocore.exceptions import ClientError
log = logging.getLogger(__name__)
 
"""
print("__main__.py!")


ec2 = boto3.resource('ec2')

try:
    ec2.create_vpc(CidrBlock='10.0.0.0/16', DryRun=True)
except ClientError as e:
    if "DryRunOperation" not in str(e):
        raise
    log.info("VPC creation dryrun succeeded. Now processing real task...")
#vpc = ec2.create_vpc(CidrBlock='10.0.0.0/16')
#vpc_id = vpc.id
vpc_id = 'vpc-0c1dee316e8c29bdd'


try:
    vpc.create_tags(Tags=[{"Key": "Name", "Value": "my_vpc"}], DryRun=True)
except ClientError as e:
    if "DryRunOperation" not in str(e):
        raise
    log.info("VPC creation dryrun succeeded. Now processing real task...")
#vpc.create_tags(Tags=[{"Key": "Name", "Value": "my_vpc"}])
"""

vpc = subnets.create_custom_vpc('10.0.0.0/16','Name', 'myVPC')
print("VCP créé")
print(vpc, "\n")
vpc_id = vpc["Vpc"]["VpcId"] 
input()

print("VPC ID")
print(vpc_id, "\n")
#vpc_id = 'vpc-0c1dee316e8c29bdd'



#Création du subnet public
publicSubnet = subnets.create_subnet_perso("us-east-1a", "10.0.1.0/24", vpc_id, "Name", "Pub-Sub")
print("Réussite création subnet public")
print(publicSubnet, "\n")
public_subnet_id = publicSubnet["Subnet"]["SubnetId"]

#Création du subnet privé
privateSubnet = subnets.create_subnet_perso("us-east-1a", "10.0.2.0/24", vpc_id, "Name", "Priv-Sub")
print("Réussite création subnet privé")
print(privateSubnet, "\n")
private_subnet_id = privateSubnet["Subnet"]["SubnetId"]



#Create and attach Internet Gateway
internet_gateway, gw_id = gateways.attach_gateway(vpc_id, "Name", "GW")
print("Create and attach Internet Gateway Response")
print(internet_gateway, "\n")


#Get subnet ID for NAT Gateway
subnet_id_ng = publicSubnet["Subnet"]["SubnetId"]
print("Get Subnet ID for NAT Gateway")
print(subnet_id_ng, "\n")

#Create NAT Gateway
nat_gateway = gateways.create_gateway_perso(subnet_id_ng, "Name", "EIP", "Name", "Nat-GW")
log.info("Create NAT Gateway")
log.debug(nat_gateway)

#Get Internet Gateway ID
internet_gateway_id = internet_gateway["InternetGateway"]
log.info("Get Internet Gateway ID")
log.debug(internet_gateway_id)

#Create Route table and Route to Internet Gateway
public_routage_gt = routes.create_public_route(vpc_id, "0.0.0.0/0", internet_gateway_id, "Name", "Pub-RT")
print("Create Route Table for Internet Gateway Response")
print(public_routage_gt, "\n")

#Get NAT Gateway ID
nat_gateway_id = nat_gateway["NatGateway"]["NatGatewayId"]
print("Get NAT Gateway ID")
print(nat_gateway_id, "\n")

###TODO check NAT activation status






