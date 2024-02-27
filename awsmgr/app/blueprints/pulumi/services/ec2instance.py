import pulumi
from pulumi_aws import ec2


def pulumi_ec2_instance_func(resource_name, instance_type, ami, tags={}):
     # Create an EC2 linux instance
    instance = ec2.Instance(
        resource_name,
        instance_type=instance_type,
        ami=ami,
        tags=tags
    )
