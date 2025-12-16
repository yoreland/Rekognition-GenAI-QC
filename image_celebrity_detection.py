import boto3
import cv2

def detect_celebrities_in_image(image_path):
    # 读取图片
    with open(image_path, 'rb') as image_file:
        image_bytes = image_file.read()
    
    # 调用 Rekognition
    rekognition = boto3.client('rekognition')
    response = rekognition.recognize_celebrities(Image={'Bytes': image_bytes})
    
    # 读取图片用于绘制
    image = cv2.imread(image_path)
    h, w = image.shape[:2]
    
    # 颜色列表
    colors = [(255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,0,255), (0,255,255)]
    
    print(f"Found {len(response['CelebrityFaces'])} celebrities:")
    
    # 为每个名人画框
    for i, celebrity in enumerate(response['CelebrityFaces']):
        name = celebrity['Name']
        confidence = celebrity['MatchConfidence']
        bbox = celebrity['Face']['BoundingBox']
        
        print(f"- {name} (confidence: {confidence:.1f}%)")
        
        # 坐标转换
        x = int(bbox['Left'] * w)
        y = int(bbox['Top'] * h)
        width = int(bbox['Width'] * w)
        height = int(bbox['Height'] * h)
        
        # 画框和标签
        color = colors[i % len(colors)]
        cv2.rectangle(image, (x, y), (x + width, y + height), color, 3)
        cv2.putText(image, f"{name} ({confidence:.1f}%)", 
                   (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    # 保存结果
    output_path = f"celebrity_detected_{image_path.split('/')[-1]}"
    cv2.imwrite(output_path, image)
    print(f"Saved result to: {output_path}")
    
    return response

if __name__ == "__main__":
    detect_celebrities_in_image("jeff_portrait.jpg")
