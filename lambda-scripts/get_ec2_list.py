import boto3

def lambda_handler(event, context):
    string = ""

    bucket_name = "ec2-owners-list"
    s3_path = "user_list.txt"
    
    
    regions= [
    'ap-northeast-1',
    'ap-northeast-2',
    'ap-south-1',
    'ap-southeast-1',
    'ap-southeast-2',
    'ca-central-1',
    'eu-central-1',
    'eu-north-1',
    'eu-west-1',
    'eu-west-2',
    'eu-west-3',
    'sa-east-1',
    'us-east-1',
    'us-east-2',
    'us-west-1',
    'us-west-2'
    ]

    temp_regions = ['eu-north-1']
    iam_users_with_all_ec2_details = {}
    for region in temp_regions:
        string += region + '\n'
        ec2= boto3.resource('ec2', region_name=region)
        for instance in ec2.instances.all():
            instance_details_dict={}
            if not instance.tags is None:
                for tag in instance.tags:
                    if tag['Key'] == 'Name':
                        instance_name = tag['Value']
                    elif tag['Key'] == 'Department':
                        instance_department = tag['Value']
                    elif tag['Key'] == 'Project':
                        instance_project = tag['Value']
                    elif tag['Key'] == 'Owner':
                        instance_owner = tag['Value']
                    else:
                        pass
            if instance.public_ip_address is None:
                instance_private_ip = instance.private_ip_address
            else:
                instance_public_ip = instance.public_ip_address
            instance_details_dict["name"] = instance_name
            instance_details_dict["instance_id"] = instance.id
            instance_details_dict["status"] = instance.state['Name']
            instance_details_dict["department"] = instance_department
            instance_details_dict["project"] = instance_project
            if instance_owner not in iam_users_with_all_ec2_details:
                iam_users_with_all_ec2_details[instance_owner] = [instance_details_dict]
            else:
                iam_users_with_all_ec2_details[instance_owner].append(instance_details_dict)

            print(instance_details_dict)
            string += instance.id + '\n'
        print(iam_users_with_all_ec2_details)

            





    #print(string)
    #encoded_string = string
    # .encode("utf-8")
    #s3 = boto3.resource("s3")
    #s3.Bucket(bucket_name).put_object(Key=s3_path, Body=encoded_string)


lambda_handler(0, 0)