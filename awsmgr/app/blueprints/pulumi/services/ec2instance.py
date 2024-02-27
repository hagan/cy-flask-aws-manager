import pulumi
from pulumi_aws import ec2


def pulumi_ec2_instance():
     # Create an EC2 linux instance
    instance = ec2.Instance(
        'awsmgr-instance',
        instance_type='t2.micro',
        ami='ami-052c9ea013e6e3567',
        tags={'Name': 'AWSMGRInstance'}
    )
