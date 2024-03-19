import json
import os
import sys

import pulumi
from pulumi import Output, export, ResourceOptions
from pulumi import automation as auto
import pulumi_aws as aws

from awsmgr.app.blueprints.boto.services.dataclass import AWSMgrConfigDataClass
from awsmgr.app.blueprints.pulumi.services import get_pulumi_provider

# from awsmgr.app.utils import with_appcontext

# config = pulumi.Config()
# env = pulumi.get_stack()
# vpc_name = config.require("cyverse-ec2-example-vpc")
# zone_number = config.require_int("zone_number")
# vpc_cidr = config.require("vpc_cidr")


# @with_appcontext app
def pulumi_s3_bucket_func(acdc: AWSMgrConfigDataClass, bucket_name: str, printf=print):
    provider = get_pulumi_provider(acdc)
    ## oddly even providing a provider it uses environment 1st
    os.environ.pop('AWS_ACCESS_KEY_ID')
    os.environ.pop('AWS_SECRET_ACCESS_KEY')
    os.environ.pop('AWS_SESSION_TOKEN')

    if bucket_name:
        printf("pulumi_s3_bucket_func called")
        bucket = aws.s3.Bucket(
            bucket_name,
            opts=pulumi.ResourceOptions(provider=provider),
        )
        # Export the bucket's name
        pulumi.export('bucket_name', bucket.id)
