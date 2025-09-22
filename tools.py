import cv2
import base64

def capture_image(max_index=3) -> str:
    """
    Captures one frame from the first available webcam, saves it as 'sample.jpg',
    and returns it as a Base64-encoded string.
    """
    for idx in range(max_index + 1):
        cap = cv2.VideoCapture(idx)  # Works on both Mac & Windows
        if cap.isOpened():
            print(f"Webcam found at index {idx}")
            # Warm up the camera
            for _ in range(10):
                cap.read()
            ret, frame = cap.read()
            cap.release()
            if ret:
                cv2.imwrite("sample.jpg", frame)
                print("Image captured and saved as 'sample.jpg'")
                # Encode to Base64
                _, buf = cv2.imencode('.jpg', frame)
                return base64.b64encode(buf).decode('utf-8')
    raise RuntimeError("Could not open any webcam (tried indices 0-3)")

# Example usage
if __name__ == "__main__":
    img_b64 = capture_image()
    print(f"Base64 string length: {len(img_b64)}") 


from groq import Groq

def analyze_image_with_query(query: str) -> str:
    """
    Expects a string with 'query'.
    Captures the image and sends the query and the image to
    to Groq's vision chat API and returns the analysis.
    """
    img_b64 = capture_image()
    model="meta-llama/llama-4-maverick-17b-128e-instruct"
    
    if not query or not img_b64:
        return "Error: both 'query' and 'image' fields required."

    client=Groq(api_key="REMOVED_SECRETuHxFC")  
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text", 
                    "text": query
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{img_b64}",
                    },
                },
            ],
        }]
    chat_completion=client.chat.completions.create(
        messages=messages,
        model=model
    )

    return chat_completion.choices[0].message.content

#query = "How many people do you see?"
#print(analyze_image_with_query(query))
