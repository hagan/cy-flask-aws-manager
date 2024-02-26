import json
import os

import pulumi
from pulumi import Output, export, ResourceOptions
from pulumi import automation as auto
import pulumi_aws as aws

import sys

from awsmgr.app.utils import with_appcontext

# config = pulumi.Config()
# env = pulumi.get_stack()
# vpc_name = config.require("cyverse-ec2-example-vpc")
# zone_number = config.require_int("zone_number")
# vpc_cidr = config.require("vpc_cidr")


@with_appcontext
def pulumi_s3_bucket(app):
    """

    """
     # Create an AWS S3 bucket
    bucket = aws.s3.Bucket('myBucket')

    # Export the bucket's name
    pulumi.export('bucket_name', bucket.id)

