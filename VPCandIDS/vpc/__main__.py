from . import boto3
from . import subnets
from . import gateways
from . import routes
from . import acls
from . import security_groups


#from botocore.exceptions import ClientError
#log = logging.getLogger(__name__)
 
ec2 = boto3.client('ec2')
#Création du VPC
vpc = subnets.create_custom_vpc('10.0.0.0/16','Name', 'myVPC')
print("VCP créé")
print(vpc, "\n")
vpc_id = vpc["Vpc"]["VpcId"] 
print("VPC ID")
print(vpc_id, "\n")



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
internet_gateway = gateways.create_internet_gateway(vpc_id, "Name", "Internet-GW")
print("Create and attach Internet Gateway")
print(internet_gateway, "\n")


#Get subnet ID for NAT Gateway
subnet_id_ng = publicSubnet["Subnet"]["SubnetId"]
print("Get Subnet ID for NAT Gateway")
print(subnet_id_ng, "\n")

#Create NAT Gateway
nat_gateway = gateways.create_nat_gateway(subnet_id_ng, "Name", "EIP", "Name", "Nat-GW")
print("Create NAT Gateway")
print(nat_gateway, "\n")

#Get Internet Gateway ID
internet_gateway_id = internet_gateway["InternetGateway"]["InternetGatewayId"]
print("Get Internet Gateway ID")
print(internet_gateway_id,"\n")

#Create Route table and Route to Internet Gateway
public_routage_gt = routes.create_public_route(vpc_id, "0.0.0.0/0", internet_gateway_id, "Name", "Public-Route")
print("Create Route Table for Internet Gateway")
print(nat_gateway, "\n")

#Get NAT Gateway ID
nat_gateway_id = nat_gateway['NatGateway']['NatGatewayId']
print("Get NAT Gateway ID")
print(nat_gateway_id, "\n")

print("NAT setting up......")

ng_available = False

#Check if Nat Gateway is Active then create route
while ng_available == False:
    #Get NAT Gateway State
    get_nat_gw= ec2.describe_nat_gateways(
        Filter=[
            {
                'Name': 'nat-gateway-id',
                'Values': [
                    nat_gateway_id,
                ],
            },
        ],
    )

    nat_gatway_info = get_nat_gw['NatGateways'][0]
    ng_state = nat_gatway_info['State']

    if ng_state == "available":
        print("NAT Gateway est up !" "\n")

        #Create Private Route Table and Route to NAT Gateway
        response_private_rt = routes.create_private_route(vpc_id, "0.0.0.0/0","Name", "Private-Route")
        print("Create Route Table for NAT Gateway ")
        print(nat_gateway, "\n")

        ng_available = True




#Table de routage de l'IP publique
public_route_id = public_routage_gt["RouteTable"]["RouteTableId"]
print("Get public route table")
print(public_route_id, "\n")

#Association du subnet public avec la table de routage publique
association_public_subnet_routage = routes.association_tableRoutage_subnet(public_route_id, public_subnet_id)
print("Association du subnet public à la table de routage publique")
print(association_public_subnet_routage, "\n")

#Table de routage du subnet privé
private_routage = routes.create_private_route(vpc_id, "0.0.0.0/0", "Name", "Private-Route")
print("Table de routage subnet privé")
print(private_routage, "\n")

#Table de routage subnet privé
private_route_id = private_routage["RouteTable"]["RouteTableId"]
print("Get Public Route Table ID")
print(private_route_id, "\n")

#Association du subnet privé avec la table de routage privée
association_private_subnet_routage = routes.association_tableRoutage_subnet(private_route_id, private_subnet_id)
print("Associate Private Subnet 1 to Private Route table Response")
print(association_private_subnet_routage, "\n")

#NACLS
nacl = acls.create_and_configure_nacl(vpc_id, public_subnet_id, private_subnet_id,'us-east-1')
print(nacl)

#Groupes de sécurité
web_sg_id, db_sg_id = security_groups.create_security_groups(vpc_id)
print(f"Security Group for Web Server: {web_sg_id}")
print(f"Security Group for DB Server: {db_sg_id}")

print("All done")








