import boto3
import json
import time

class RekognitionVideo:
    def __init__(self, bucket, video, role_arn, sns_topic_arn, sqs_queue_url):
        self.bucket = bucket
        self.video = video
        self.roleArn = role_arn
        self.snsTopicArn = sns_topic_arn
        self.sqsQueueUrl = sqs_queue_url
        self.rek = boto3.client('rekognition')
        self.sqs = boto3.client('sqs')
        self.startJobId = None

    def StartCelebrityDetection(self):
        response = self.rek.start_celebrity_recognition(
            Video={'S3Object': {'Bucket': self.bucket, 'Name': self.video}},
            NotificationChannel={'RoleArn': self.roleArn, 'SNSTopicArn': self.snsTopicArn}
        )
        self.startJobId = response['JobId']
        print('Start Job Id: ' + self.startJobId)

    def GetSQSMessageSuccess(self):
        jobFound = False
        succeeded = False
        
        while not jobFound:
            sqsResponse = self.sqs.receive_message(QueueUrl=self.sqsQueueUrl, MessageAttributeNames=['ALL'])
            
            if 'Messages' not in sqsResponse:
                print("No messages in queue, waiting...")
                time.sleep(5)
                continue
                
            for message in sqsResponse['Messages']:
                notification = json.loads(message['Body'])
                rekMessage = json.loads(notification['Message'])
                
                if rekMessage['JobId'] == self.startJobId:
                    jobFound = True
                    if rekMessage['Status'] == 'SUCCEEDED':
                        succeeded = True
                    
                    self.sqs.delete_message(QueueUrl=self.sqsQueueUrl, 
                                          ReceiptHandle=message['ReceiptHandle'])
                    break
        
        return succeeded

    def GetCelebrityDetectionResults(self):
        maxResults = 10
        paginationToken = ''
        finished = False

        while not finished:
            response = self.rek.get_celebrity_recognition(
                JobId=self.startJobId,
                MaxResults=maxResults,
                NextToken=paginationToken
            )

            print(response['VideoMetadata']['Codec'])
            print(str(response['VideoMetadata']['DurationMillis']))
            print(response['VideoMetadata']['Format'])
            print(response['VideoMetadata']['FrameRate'])

            for celebrityRecognition in response['Celebrities']:
                print('Celebrity: ' + str(celebrityRecognition['Celebrity']['Name']))
                print('Timestamp: ' + str(celebrityRecognition['Timestamp']))
                print()

            if 'NextToken' in response:
                paginationToken = response['NextToken']
            else:
                finished = True
