import boto3


def find_instance_id_by_name(resource_name):
    ec2 = boto3.client('ec2')
    response = ec2.describe_instances(
        Filters=[
            {
                'Name': 'tag:Name',
                'Values': [resource_name]
            }
        ]
    )
    for reservation in response['Reservations']:
        for instance in reservation['Instance']:
            return instance['InstanceId']
    return None


def boto3_start_ec2(ec2_resource_name, printf=print):
    printf(f"boto3_start_ec2({ec2_resource_name})")
    ec2 = boto3.resource('ec2')

    instance_id = find_instance_id_by_name(ec2_resource_name)
    if instance_id:
        instance = ec2.Instance(instance_id)
        printf("Starting instance: {instance_id}")
        response = instance.start()
        printf(response)
    else:
        printf(f"ERROR: Could not find {ec2_resource_name}")


def boto3_stop_ec2(ec2_resource_name, printf=print):
    printf(f"boto3_stop_ec2({ec2_resource_name})")
    ec2 = boto3.resource('ec2')
    instance_id = find_instance_id_by_name(ec2_resource_name)
    if instance_id:
        instance = ec2.Instance(instance_id)
        printf("Stopping instance: {instance_id}")
        response = instance.stop()
        printf(response)
    else:
        printf(f"ERROR: Could not find {ec2_resource_name}")