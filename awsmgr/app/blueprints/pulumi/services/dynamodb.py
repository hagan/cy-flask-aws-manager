import os
import pulumi
from pulumi_aws import dynamodb

from awsmgr.app.blueprints.pulumi.services import get_pulumi_provider

def pulumi_dynamodb_instance_func(acdc, resource_name, tags={}):
     # Create an EC2 linux instance
    provider = get_pulumi_provider(acdc)
    ## oddly even providing a provider it uses environment 1st
    os.environ.pop('AWS_ACCESS_KEY_ID')
    os.environ.pop('AWS_SECRET_ACCESS_KEY')
    os.environ.pop('AWS_SESSION_TOKEN')
    print(f"current AWS_ACCESS_KEY_ID: {acdc.aws_access_key_id}")
    instance = dynamodb.Table(
        resource_name,
        opts=pulumi.ResourceOptions(provider=provider),
        attributes=[
            dynamodb.TableAttributeArgs(
                name="id",
                type="S",
            ),
        ],
        hash_key="id",
        billing_mode="PAY_PER_REQUEST")
    return instance
