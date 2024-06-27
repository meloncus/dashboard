import subprocess
import numpy as np
import socketio
import threading

# RTSP 스트림 URL
rtsp_url = "rtsp://user:4321q0220@192.168.10.121:554"
sample_rate = 8000

# ffmpeg 명령어
ffmpeg_command = [
    'ffmpeg',
    '-i', rtsp_url,  # 입력 스트림
    '-acodec', 'aac',  # 오디오 코덱을 AAC로 변경
    '-ar', str(sample_rate),  # 샘플레이트를 변수에서 설정된 값으로 변경
    '-ab', '64k',  # 비트레이트를 64kbps로 설정
    '-vn',  # 비디오 스트림 제거
    '-rtsp_transport', 'tcp',  # RTSP 스트림을 TCP를 통해 전송
    'output_audio.aac'  # 출력 파일명과 포맷
]

# Socket.IO 클라이언트 설정
sio = socketio.Client()

@sio.event
def connect():
    print("!!Connection established!!")

@sio.event
def disconnect():
    print("!!Disconnected from server!!")

sio.connect('http://localhost:5000')


def capture_audio():
    print("Capturing audio...")
    process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=10**8)
    while True:
        print("Reading audio data...")
        bytes_per_sample = 2 * 2  # 16비트 스테레오의 경우
        raw_audio = process.stdout.read(int(sample_rate) * bytes_per_sample)
        print("Raw audio:", raw_audio)
        if not raw_audio:
            print("No audio data")
            break  # 프로세스가 종료되었거나 오류가 발생한 경우 루프 종료
        audio_data = np.frombuffer(raw_audio, np.int16)
        print("Audio data:", audio_data)
        sio.emit('audio_data', audio_data.tolist())
        print("Sent audio data:", audio_data)

        # Check if capture_audio is working properly
        print("capture_audio is working properly")

threading.Thread(target=capture_audio).start()