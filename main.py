# import asyncio
# import threading

# from fastapi import FastAPI, File, UploadFile
# from fastapi.responses import StreamingResponse

# app = FastAPI()

# # Global variable to hold the latest frame (in memory)
# latest_frame = None

# # A lock to ensure thread-safe access to the frame
# frame_lock = threading.Lock()


# @app.post("/upload_frame")
# async def upload_frame(file: UploadFile = File(...)):
#     """
#     Endpoint for the ESP32 to upload a single frame.
#     Expects the frame as an image (e.g. JPEG).
#     """
#     global latest_frame
#     # Read the uploaded file contents
#     content = await file.read()
#     # Update the global frame safely using the lock
#     with frame_lock:
#         latest_frame = content
#     return {"status": "frame received"}


# @app.get("/video_feed")
# async def video_feed():
#     """
#     Endpoint that streams the video feed (MJPEG) to the client.
#     It repeatedly sends the latest available frame.
#     """
#     async def frame_generator():
#         global latest_frame
#         while True:
#             # Sleep briefly to avoid a tight loop
#             await asyncio.sleep(0.05)
#             with frame_lock:
#                 frame = latest_frame
#             if frame:
#                 yield (
#                     b"--frame\r\n"
#                     b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
#                 )
#     return StreamingResponse(
#         frame_generator(),
#         media_type="multipart/x-mixed-replace; boundary=frame"
#     )




# from fastapi import FastAPI, WebSocket
# import base64

# app = FastAPI()

# latest_frame = None  # Store the latest frame

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     global latest_frame
#     await websocket.accept()
#     print("WebSocket connection established!")
#     try:
#         while True:
#             frame_data = await websocket.receive_text()  # Receive base64 frame
#             latest_frame = base64.b64decode(frame_data)  # Decode to bytes
#     except Exception as e:
#         print("WebSocket error:", e)
#     finally:
#         await websocket.close()

# @app.get("/latest_frame")
# async def get_latest_frame():
#     if latest_frame is None:
#         return {"error": "No frame received yet"}
    
#     return {"frame": base64.b64encode(latest_frame).decode('utf-8')}


from fastapi import FastAPI, WebSocket, Response
import base64

app = FastAPI()

latest_frame = None  # Store the latest frame

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """ Receives frames from ESP32 over WebSocket """
    global latest_frame
    await websocket.accept()
    print("WebSocket connection established!")

    try:
        while True:
            frame_data = await websocket.receive_text()  # Receive frame as Base64
            latest_frame = base64.b64decode(frame_data)  # Decode frame
    except Exception as e:
        print("WebSocket connection closed:", e)
    finally:
        await websocket.close()

@app.get("/latest_frame")
async def get_latest_frame():
    """ Returns the latest frame as an image response """
    if latest_frame is None:
        return {"error": "No frame received yet"}
    
    return Response(content=latest_frame, media_type="image/jpeg")
