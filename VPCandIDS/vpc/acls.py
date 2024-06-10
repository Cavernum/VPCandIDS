import boto3

def create_and_configure_nacl(ec2_client,vpc_id, public_subnet_id, private_subnet_id, region='votre-region'):
    
    nacl_response = ec2_client.create_network_acl(VpcId=vpc_id)
    nacl_id = nacl_response['NetworkAcl']['NetworkAclId']

    current_associations = ec2_client.describe_network_acls(
        Filters=[
            {'Name': 'association.subnet-id', 'Values': [public_subnet_id, private_subnet_id]}
        ]
    )
    
    for association in current_associations['NetworkAcls'][0]['Associations']:
        if association['SubnetId'] == public_subnet_id:
            ec2_client.replace_network_acl_association(
                AssociationId=association['NetworkAclAssociationId'],
                NetworkAclId=nacl_id
            )
    
    for association in current_associations['NetworkAcls'][0]['Associations']:
        if association['SubnetId'] == private_subnet_id:
            ec2_client.replace_network_acl_association(
                AssociationId=association['NetworkAclAssociationId'],
                NetworkAclId=nacl_id
            )
    """"
    nacl_response = ec2_client.create_network_acl(VpcId=vpc_id)
    nacl_id = nacl_response['NetworkAcl']['NetworkAclId']
    print(nacl_id)
    
    ec2_client.associate_network_acl(Association={
        'NetworkAclId': nacl_id,
        'SubnetId': public_subnet_id
    })
    # Associer la NACL au sous-réseau privé
    ec2_client.associate_network_acl(Association={
        'NetworkAclId': nacl_id,
        'SubnetId': private_subnet_id
    })
    #ec2_client.associate_network_acl(NetworkAclId=nacl_id, SubnetId=public_subnet_id)
    #ec2_client.associate_network_acl(NetworkAclId=nacl_id, SubnetId=private_subnet_id)
    """
    
# Créer les règles pour le sous-réseau public (Serveur Web)
    ec2_client.create_network_acl_entry(
        NetworkAclId=nacl_id,
        RuleNumber=100,
        Protocol='-1',  # All
        RuleAction='allow',
        Egress=False,
        CidrBlock='0.0.0.0/0',
        PortRange={'From': 0, 'To': 65535}
    )
    ec2_client.create_network_acl_entry(
        NetworkAclId=nacl_id,
        RuleNumber=100,
        Protocol='-1',  # All
        RuleAction='allow',
        Egress=True,
        CidrBlock='0.0.0.0/0',
        PortRange={'From': 0, 'To': 65535}
    )
    # ec2_client.create_network_acl_entry(
    #     NetworkAclId=nacl_id,
    #     RuleNumber=110,
    #     Protocol='4',
    #     RuleAction='allow',
    #     Egress=False,
    #     CidrBlock='0.0.0.0/0',
    #     PortRange={'From': 0, 'To': 65535}
    # )
    # ec2_client.create_network_acl_entry(
    #     NetworkAclId=nacl_id,
    #     RuleNumber=120,
    #     Protocol='4',
    #     RuleAction='allow',
    #     Egress=True,
    #     CidrBlock='10.0.2.0/24',
    #     PortRange={'From': 0, 'To': 65535}
    # )

# Créer les règles pour le sous-réseau privé (Serveur MariaDB)
    ec2_client.create_network_acl_entry(
        NetworkAclId=nacl_id,
        RuleNumber=200,
        Protocol='-1',
        RuleAction='allow',
        Egress=False,
        CidrBlock='10.0.0.0/16',
        PortRange={'From': 0, 'To': 65535}
    )
    ec2_client.create_network_acl_entry(
        NetworkAclId=nacl_id,
        RuleNumber=200,
        Protocol='-1',
        RuleAction='allow',
        Egress=True,
        CidrBlock='10.0.0.0/16',
        PortRange={'From': 0, 'To': 65535}
    )
    # ec2_client.create_network_acl_entry(
    #     NetworkAclId=nacl_id,
    #     RuleNumber=210,
    #     Protocol='4',
    #     RuleAction='allow',
    #     Egress=True,
    #     CidrBlock='10.0.1.0/24',
    #     PortRange={'From': 0, 'To': 65535}
    # )
    
    return nacl_id
