import boto3
import json
import time

def setup_resources():
    # Get account ID and region
    sts = boto3.client('sts')
    account_id = sts.get_caller_identity()['Account']
    region = boto3.Session().region_name or 'us-east-1'
    
    # Create clients
    s3 = boto3.client('s3')
    sns = boto3.client('sns')
    sqs = boto3.client('sqs')
    iam = boto3.client('iam')
    
    bucket_name = f'rekognition-video-{account_id}'
    topic_name = 'RekognitionVideoTopic'
    queue_name = 'RekognitionVideoQueue'
    role_name = 'RekognitionVideoRole'
    
    print(f"Setting up resources in region: {region}")
    
    # 1. Create S3 bucket
    try:
        if region == 'us-east-1':
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        print(f"Created S3 bucket: {bucket_name}")
    except Exception as e:
        print(f"S3 bucket creation: {e}")
    
    # 2. Create SNS topic
    topic_response = sns.create_topic(Name=topic_name)
    topic_arn = topic_response['TopicArn']
    print(f"Created SNS topic: {topic_arn}")
    
    # 3. Create SQS queue
    queue_response = sqs.create_queue(QueueName=queue_name)
    queue_url = queue_response['QueueUrl']
    queue_arn = f"arn:aws:sqs:{region}:{account_id}:{queue_name}"
    print(f"Created SQS queue: {queue_url}")
    
    # 4. Subscribe SQS to SNS
    sns.subscribe(
        TopicArn=topic_arn,
        Protocol='sqs',
        Endpoint=queue_arn
    )
    
    # 5. Set SQS queue policy to allow SNS
    queue_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": "*",
            "Action": "sqs:SendMessage",
            "Resource": queue_arn,
            "Condition": {
                "ArnEquals": {
                    "aws:SourceArn": topic_arn
                }
            }
        }]
    }
    
    sqs.set_queue_attributes(
        QueueUrl=queue_url,
        Attributes={'Policy': json.dumps(queue_policy)}
    )
    print("Set SQS queue policy")
    
    # 6. Create IAM role for Rekognition
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "rekognition.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }
    
    try:
        iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy)
        )
        
        # Attach policy to allow SNS publish
        role_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Action": "sns:Publish",
                "Resource": topic_arn
            }]
        }
        
        iam.put_role_policy(
            RoleName=role_name,
            PolicyName='RekognitionSNSPolicy',
            PolicyDocument=json.dumps(role_policy)
        )
        
        role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"
        print(f"Created IAM role: {role_arn}")
        
    except Exception as e:
        print(f"IAM role creation: {e}")
        role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"
    
    # Wait for role propagation
    time.sleep(10)
    
    return {
        'bucket': bucket_name,
        'topic_arn': topic_arn,
        'queue_url': queue_url,
        'role_arn': role_arn,
        'region': region,
        'account_id': account_id
    }

if __name__ == "__main__":
    resources = setup_resources()
    print("\nResource setup complete!")
    print(f"Bucket: {resources['bucket']}")
    print(f"Topic ARN: {resources['topic_arn']}")
    print(f"Queue URL: {resources['queue_url']}")
    print(f"Role ARN: {resources['role_arn']}")
