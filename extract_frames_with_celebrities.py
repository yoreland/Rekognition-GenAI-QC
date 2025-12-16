import boto3
import cv2
import numpy as np
from rekognition_video import RekognitionVideo
import os
import tempfile

def download_video_from_s3(bucket, key, local_path):
    s3 = boto3.client('s3')
    s3.download_file(bucket, key, local_path)

def get_celebrity_results(analyzer):
    results = []
    maxResults = 10
    paginationToken = ''
    finished = False

    while not finished:
        response = analyzer.rek.get_celebrity_recognition(
            JobId=analyzer.startJobId,
            MaxResults=maxResults,
            NextToken=paginationToken
        )

        for celebrityRecognition in response['Celebrities']:
            results.append({
                'name': celebrityRecognition['Celebrity']['Name'],
                'timestamp': celebrityRecognition['Timestamp'],
                'bbox': celebrityRecognition['Celebrity']['Face']['BoundingBox']
            })

        if 'NextToken' in response:
            paginationToken = response['NextToken']
        else:
            finished = True
    
    return results

def extract_frames_with_boxes():
    # Setup
    bucket = 'bedrock-video-generation-us-west-2-vst8u9'
    video = 'wjqxfhkrxovu/output.mp4'
    role_arn = 'arn:aws:iam::077090643075:role/RekognitionVideoRole'
    sns_topic_arn = 'arn:aws:sns:us-west-2:077090643075:RekognitionVideoTopic'
    sqs_queue_url = 'https://sqs.us-west-2.amazonaws.com/077090643075/RekognitionVideoQueue'
    
    analyzer = RekognitionVideo(bucket, video, role_arn, sns_topic_arn, sqs_queue_url)
    
    print("Starting celebrity detection...")
    analyzer.StartCelebrityDetection()
    
    if analyzer.GetSQSMessageSuccess():
        print("Getting celebrity results...")
        celebrity_results = get_celebrity_results(analyzer)
        
        # Download video
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_file:
            video_path = tmp_file.name
            
        print("Downloading video...")
        download_video_from_s3(bucket, video, video_path)
        
        # Extract frames
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Colors for different celebrities
        colors = [(255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,0,255), (0,255,255)]
        celebrity_colors = {}
        
        # Get unique timestamps for key frames
        timestamps = sorted(set([r['timestamp'] for r in celebrity_results]))[:5]
        
        for i, timestamp in enumerate(timestamps):
            frame_number = int(timestamp * fps / 1000)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = cap.read()
            
            if ret:
                h, w = frame.shape[:2]
                
                # Draw boxes for celebrities at this timestamp
                for result in celebrity_results:
                    if result['timestamp'] == timestamp:
                        name = result['name']
                        bbox = result['bbox']
                        
                        if name not in celebrity_colors:
                            celebrity_colors[name] = colors[len(celebrity_colors) % len(colors)]
                        
                        color = celebrity_colors[name]
                        
                        # Convert normalized coordinates to pixel coordinates
                        x = int(bbox['Left'] * w)
                        y = int(bbox['Top'] * h)
                        width = int(bbox['Width'] * w)
                        height = int(bbox['Height'] * h)
                        
                        # Draw rectangle and label
                        cv2.rectangle(frame, (x, y), (x + width, y + height), color, 2)
                        cv2.putText(frame, name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                # Save frame
                output_path = f'frame_{i+1}_t{timestamp}ms.jpg'
                cv2.imwrite(output_path, frame)
                print(f"Saved: {output_path}")
        
        cap.release()
        os.unlink(video_path)
        
        print(f"\nCelebrity color mapping:")
        for name, color in celebrity_colors.items():
            print(f"{name}: RGB{color}")

if __name__ == "__main__":
    extract_frames_with_boxes()
