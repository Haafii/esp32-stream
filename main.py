import asyncio
import threading

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse

app = FastAPI()

# Global variable to hold the latest frame (in memory)
latest_frame = None

# A lock to ensure thread-safe access to the frame
frame_lock = threading.Lock()


@app.post("/upload_frame")
async def upload_frame(file: UploadFile = File(...)):
    """
    Endpoint for the ESP32 to upload a single frame.
    Expects the frame as an image (e.g. JPEG).
    """
    global latest_frame
    # Read the uploaded file contents
    content = await file.read()
    # Update the global frame safely using the lock
    with frame_lock:
        latest_frame = content
    return {"status": "frame received"}


@app.get("/video_feed")
async def video_feed():
    """
    Endpoint that streams the video feed (MJPEG) to the client.
    It repeatedly sends the latest available frame.
    """
    async def frame_generator():
        global latest_frame
        while True:
            # Sleep briefly to avoid a tight loop
            await asyncio.sleep(0.05)
            with frame_lock:
                frame = latest_frame
            if frame:
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
                )
    return StreamingResponse(
        frame_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
