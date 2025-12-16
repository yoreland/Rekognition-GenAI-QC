from rekognition_video import RekognitionVideo

def main():
    # Actual resource values from setup
    bucket = 'bedrock-video-generation-us-west-2-vst8u9'
    video = 'wjqxfhkrxovu/output.mp4'
    role_arn = 'arn:aws:iam::077090643075:role/RekognitionVideoRole'
    sns_topic_arn = 'arn:aws:sns:us-west-2:077090643075:RekognitionVideoTopic'
    sqs_queue_url = 'https://sqs.us-west-2.amazonaws.com/077090643075/RekognitionVideoQueue'
    
    analyzer = RekognitionVideo(bucket, video, role_arn, sns_topic_arn, sqs_queue_url)
    
    print("Starting celebrity detection...")
    analyzer.StartCelebrityDetection()
    
    print("Waiting for job completion...")
    if analyzer.GetSQSMessageSuccess():
        print("Job completed successfully, getting results...")
        analyzer.GetCelebrityDetectionResults()
    else:
        print("Celebrity detection job failed")

if __name__ == "__main__":
    main()
