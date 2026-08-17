import os
import json
import base64
import asyncio
import httpx
import audioop
import time
import redis
from pydub import AudioSegment
import io
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException, Response
from fastapi.responses import PlainTextResponse

from libs.telephony_adapters.twilio_adapter import TwilioAdapter
from libs.stt_adapters.gemini_adapter import GeminiSTTAdapter
from libs.tts_adapters.gemini_adapter import GeminiTTSAdapter
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Voice Runtime API")

redis_client = redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379/0"))
twilio_adapter = TwilioAdapter()
stt_adapter = GeminiSTTAdapter()
tts_adapter = GeminiTTSAdapter()

CONVERSATION_ENGINE_URL = os.environ.get("CONVERSATION_ENGINE_URL", "http://127.0.0.1:8000/internal/conversation/turn")

def is_rate_limited(ip: str) -> bool:
    """Basic Rate Limiting: max 5 calls per minute per IP"""
    key = f"rate_limit:webhook:{ip}"
    current = redis_client.incr(key)
    if current == 1:
        redis_client.expire(key, 60)
    return current > 5

@app.post("/internal/telephony/webhook")
async def twilio_webhook(request: Request):
    client_ip = request.client.host
    if is_rate_limited(client_ip):
        raise HTTPException(status_code=429, detail="Too Many Requests")
        
    # form_data = await request.form()
    # signature = request.headers.get("X-Twilio-Signature", "")
    # url = str(request.url)
    
    # # Enforce signature validation in production/testing if token exists
    # if twilio_adapter.auth_token:
    #     if not twilio_adapter.validate_webhook_signature(signature, url, dict(form_data)):
    #         raise HTTPException(status_code=401, detail="Invalid Twilio signature")
    form_data = await request.form()
    signature = request.headers.get("X-Twilio-Signature", "")

    # print("=== ALL REQUEST HEADERS ===")
    # for key, value in request.headers.items():
    #     print(f"{key}: {value}")
    # print("===========================")

    # Twilio signs the PUBLIC HTTPS URL.
    # ngrok terminates HTTPS and forwards to local Uvicorn over HTTP,
    # so request.url may incorrectly contain http://.
    host = request.headers.get("x-forwarded-host") or request.headers.get("host", "")
    proto = request.headers.get("x-forwarded-proto", "")

    if not proto:
        proto = "https" if "ngrok" in host else request.url.scheme

    url = f"{proto}://{host}{request.url.path}"

    if request.url.query:
        url += f"?{request.url.query}"

    # print("=== TWILIO WEBHOOK DEBUG ===")
    # print("URL:", url)
    # print("Signature:", signature)
    # print("Auth token loaded:", bool(twilio_adapter.auth_token))
    # print("Auth token length:", len(twilio_adapter.auth_token))
    # print("Form params:", dict(form_data))
    # print("============================")

    # Enforce signature validation when an auth token exists
    # if twilio_adapter.auth_token:
    #     if not twilio_adapter.validate_webhook_signature(
    #         signature,
    #         url,
    #         dict(form_data),
    #     ):
    #         raise HTTPException(
    #             status_code=401,
    #             detail="Invalid Twilio signature",
    #         )
            
    # For local ngrok dev, the WebSocket URL needs to use wss://
    host = request.headers.get("host", "")
    scheme = "wss" if "ngrok" in host or "https" in str(request.url) else "ws"
    stream_url = f"{scheme}://{host}/internal/telephony/stream"
    
    # twiml_response = twilio_adapter.generate_connect_response(stream_url)
    # return Response(content=twiml_response, media_type="application/xml")
    twiml = """<?xml version="1.0" encoding="UTF-8"?>
    <Response>
    <Connect>
        <Stream
            url="wss://marina-poncho-avenging.ngrok-free.dev/internal/telephony/stream"
            statusCallback="https://marina-poncho-avenging.ngrok-free.dev/internal/telephony/stream-status"
            statusCallbackMethod="POST">

            <Parameter
                name="test"
                value="voice-receptionist"/>

        </Stream>
    </Connect>
    </Response>"""

    print("=== RETURNING STREAM TWIML ===")
    print(twiml)

    return Response(
        content=twiml,
        media_type="application/xml",
    )

async def convert_tts_to_mulaw(audio_bytes: bytes) -> bytes:
    """Convert Gemini TTS output to 8000Hz mono mu-law for Twilio"""
    # Gemini returns WAV typically
    try:
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))
        audio_segment = audio_segment.set_frame_rate(8000).set_channels(1).set_sample_width(2)
        pcm_data = audio_segment.raw_data
        mulaw_data = audioop.lin2ulaw(pcm_data, 2)
        return mulaw_data
    except Exception as e:
        print(f"Audio conversion error: {e}")
        return b""

async def write_mulaw_to_wav(mulaw_bytes: bytes) -> bytes:
    """Wrap Twilio's raw mu-law in a valid WAV container for Gemini STT"""
    pcm_data = audioop.ulaw2lin(mulaw_bytes, 2)
    wav_io = io.BytesIO()
    import wave
    with wave.open(wav_io, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(8000)
        wav_file.writeframes(pcm_data)
    return wav_io.getvalue()

@app.websocket("/internal/telephony/stream")
async def twilio_stream(websocket: WebSocket):
    await websocket.accept()
    
    stream_sid = None
    call_sid = None
    org_id = "test-org"  # In a real app, resolved from the dialed phone number
    token = "test-token"
    
    audio_buffer = bytearray()
    silence_frames = 0
    is_speaking = False
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["event"] == "start":
                stream_sid = message["start"]["streamSid"]
                call_sid = message["start"]["callSid"]
                print(f"Started stream for Call: {call_sid}")
                
            elif message["event"] == "media":
                payload = message["media"]["payload"]
                audio_chunk = base64.b64decode(payload)
                
                # Simple VAD (Amplitude-based)
                pcm_chunk = audioop.ulaw2lin(audio_chunk, 2)
                max_amp = audioop.max(pcm_chunk, 2)
                
                if max_amp > 1000: # Threshold for speech
                    is_speaking = True
                    silence_frames = 0
                    audio_buffer.extend(audio_chunk)
                elif is_speaking:
                    silence_frames += 1
                    audio_buffer.extend(audio_chunk)
                    
                    # 50 frames of silence (approx 1 second at 50 packets/sec typical) -> end of utterance
                    if silence_frames > 50:
                        is_speaking = False
                        
                        if len(audio_buffer) > 8000: # At least 1 sec of audio
                            # Process turn
                            wav_data = await write_mulaw_to_wav(bytes(audio_buffer))
                            
                            # Transcribe (Buffered STT approach)
                            try:
                                text = await stt_adapter.transcribe(wav_data, mime_type="audio/wav")
                            except Exception as e:
                                print(f"STT Error: {e}")
                                text = ""
                                
                            audio_buffer.clear()
                            
                            if text:
                                print(f"Caller said: {text}")
                                # Call Conversation Engine
                                async with httpx.AsyncClient() as client:
                                    try:
                                        resp = await client.post(CONVERSATION_ENGINE_URL, json={
                                            "call_id": call_sid,
                                            "organization_id": org_id,
                                            "token": token,
                                            "user_text": text
                                        })
                                        resp.raise_for_status()
                                        turn_resp = resp.json()
                                        
                                        reply_text = turn_resp.get("text")
                                        if reply_text:
                                            # Synthesize TTS
                                            tts_bytes = await tts_adapter.synthesize(reply_text)
                                            mulaw_out = await convert_tts_to_mulaw(tts_bytes)
                                            
                                            # Stream back in chunks
                                            chunk_size = 320 # 20ms chunks
                                            for i in range(0, len(mulaw_out), chunk_size):
                                                chunk = mulaw_out[i:i+chunk_size]
                                                out_payload = base64.b64encode(chunk).decode("utf-8")
                                                await websocket.send_text(json.dumps({
                                                    "event": "media",
                                                    "streamSid": stream_sid,
                                                    "media": {"payload": out_payload}
                                                }))
                                                await asyncio.sleep(0.02) # throttle to real-time
                                                
                                        if turn_resp.get("action") == "end_call":
                                            # Not implemented: hangup via REST API
                                            pass
                                            
                                    except Exception as e:
                                        print(f"Engine/TTS Error: {e}")
                                        # Graceful fallback per PRD
                                        fallback_text = "I'm having trouble accessing that information. Transferring you."
                                        tts_bytes = await tts_adapter.synthesize(fallback_text)
                                        mulaw_out = await convert_tts_to_mulaw(tts_bytes)
                                        out_payload = base64.b64encode(mulaw_out).decode("utf-8")
                                        await websocket.send_text(json.dumps({
                                            "event": "media",
                                            "streamSid": stream_sid,
                                            "media": {"payload": out_payload}
                                        }))
                                        
                        audio_buffer.clear()
                
            elif message["event"] == "stop":
                print(f"Stream stopped for Call: {call_sid}")
                break
                
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for Call: {call_sid}")
    except Exception as e:
        print(f"WebSocket stream error: {e}")