import os
import gradio as gr
import cv2
import time
from speech_to_text import record_audio, transcribe_with_groq
from ai_agent import ask_agent
from text_to_speech import text_to_speech_with_gtts

# API Key
GROQ_API_KEY = "REMOVED_SECRETuHxFC"
audio_filepath = "audio_question.mp3"

# ----------- Chat Logic -----------
def process_audio_and_chat(chat_history):
    try:
        # Record user audio
        record_audio(file_path=audio_filepath)
        user_input = transcribe_with_groq(audio_filepath)

        if not user_input.strip():
            return chat_history

        if "goodbye" in user_input.lower():
            chat_history.append([user_input, "Goodbye! 👋"])
            return chat_history

        # Get AI response
        response = ask_agent(user_query=user_input)

        # Generate unique filename for TTS
        timestamp = int(time.time() * 1000)
        output_file = f"final_{timestamp}.mp3"

        # Convert AI response to speech
        text_to_speech_with_gtts(input_text=response, output_filepath=output_file)

        # Update chat history
        chat_history.append([user_input, response])
        return chat_history

    except Exception as e:
        print(f"Error in recording: {e}")
        chat_history.append(["(system)", f"⚠️ Error: {str(e)}"])
        return chat_history

# ----------- Webcam Logic -----------
camera = None
is_running = False
last_frame = None

def initialize_camera():
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)
        if camera.isOpened():
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            camera.set(cv2.CAP_PROP_FPS, 30)
            camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return camera is not None and camera.isOpened()

def start_webcam():
    global is_running, last_frame
    is_running = True
    if not initialize_camera():
        return None
    ret, frame = camera.read()
    if ret and frame is not None:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        last_frame = frame
        return frame
    return last_frame

def stop_webcam():
    global is_running, camera
    is_running = False
    if camera is not None:
        camera.release()
        camera = None
    return None

def get_webcam_frame():
    global camera, is_running, last_frame
    if not is_running or camera is None:
        return last_frame
    if camera.get(cv2.CAP_PROP_BUFFERSIZE) > 1:
        for _ in range(int(camera.get(cv2.CAP_PROP_BUFFERSIZE)) - 1):
            camera.read()
    ret, frame = camera.read()
    if ret and frame is not None:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        last_frame = frame
        return frame
    return last_frame

# ----------- UI -----------
with gr.Blocks() as demo:
    gr.Markdown("<h1 style='color: orange; text-align: center; font-size: 3em;'> 👧🏼 Dora – Your Personal AI Assistant</h1>")

    with gr.Row():
        # Left column - Webcam
        with gr.Column(scale=1):
            gr.Markdown("## Webcam Feed")
            with gr.Row():
                start_btn = gr.Button("Start Camera", variant="primary")
                stop_btn = gr.Button("Stop Camera", variant="secondary")
            webcam_output = gr.Image(
                label="Live Feed",
                streaming=True,
                show_label=False,
                width=640,
                height=480
            )
            webcam_timer = gr.Timer(0.033)  # ~30 FPS

        # Right column - Chat
        with gr.Column(scale=1):
            gr.Markdown("## Chat Interface")
            chatbot = gr.Chatbot(label="Conversation", height=400, show_label=False)
            gr.Markdown("*🎤 Press the mic button to record your question*")

            with gr.Row():
                mic_btn = gr.Button("🎤 Record & Send", variant="primary")
                clear_btn = gr.Button("Clear Chat", variant="secondary")

    # Webcam events
    start_btn.click(fn=start_webcam, outputs=webcam_output)
    stop_btn.click(fn=stop_webcam, outputs=webcam_output)
    webcam_timer.tick(fn=get_webcam_frame, outputs=webcam_output, show_progress=False)

    # Chat events
    mic_btn.click(fn=process_audio_and_chat, inputs=chatbot, outputs=chatbot)
    clear_btn.click(fn=lambda: [], outputs=chatbot)

# ----------- Launch -----------
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        debug=True
    )
