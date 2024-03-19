import os

import pulumi
import pulumi_archive as archive
import pulumi_aws as aws

from awsmgr.app.blueprints.pulumi.services import get_pulumi_provider


def pulumi_lambda_instance_func(acdc, resource_name, tags={}, printf=print):
     # Create an EC2 linux instance
    provider = get_pulumi_provider(acdc)
    os.environ.pop('AWS_ACCESS_KEY_ID')
    os.environ.pop('AWS_SECRET_ACCESS_KEY')
    os.environ.pop('AWS_SESSION_TOKEN')

    printf("pulumi_lambda_instance_func called")

    assume_role = aws.iam.get_policy_document(
        statements=[
            aws.iam.GetPolicyDocumentStatementArgs(
                effect="Allow",
                principals=[
                    aws.iam.GetPolicyDocumentStatementPrincipalArgs(
                        type="Service",
                        identifiers=["lambda.amazonaws.com"],
                    )
                ],
                actions=["sts:AssumeRole"],
            )
        ]
    )
    iam_for_lambda = aws.iam.Role(
        "iam_for_lambda",
        name="iam_for_lambda",
        assume_role_policy=assume_role.json,
    )
    # lambda_ = archive.get_file(type="zip",
    #     source_file="lambda.js",
    #     output_path="lambda_function_payload.zip")
    # test_lambda = aws.lambda_.Function("test_lambda",
    #     code=pulumi.FileArchive("lambda_function_payload.zip"),
    #     name="lambda_function_name",
    #     role=iam_for_lambda.arn,
    #     handler="index.test",
    #     source_code_hash=lambda_.output_base64sha256,
    #     runtime="nodejs18.x",
    #     environment=aws.lambda_.FunctionEnvironmentArgs(
    #         variables={
    #             "foo": "bar",
    #         },
    #     ))