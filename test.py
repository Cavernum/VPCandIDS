ec2_client = self.get_ec2_client(aws_credentials)
ec2_client.describe_instances(Filters=[{
                'Name': 'private-ip-address',
                'Values': [
                    '10.273.117.10',
                ]
            }
            ])

 def get_ec2_client(self, aws_credentials):
        client = boto3.client('ec2', aws_access_key_id=aws_credentials["aws_access_key_id"],
                              aws_secret_access_key=aws_credentials["aws_secret_access_id"])
        return client
