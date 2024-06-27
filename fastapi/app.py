import subprocess
import numpy as np
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import threading

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
<head>
    <title>Real-time Audio Stream</title>
    <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
    <h1>Real-time Audio Stream</h1>
    <div id="graph"></div>
    <script type="text/javascript">
        var ws = new WebSocket("ws://localhost:8000/ws");

        var trace = {
            x: [],
            y: [],
            mode: 'lines',
            type: 'scatter'
        };
        var data = [trace];
        var layout = {
            title: 'Real-time Audio Stream',
            xaxis: {title: 'Time'},
            yaxis: {title: 'Amplitude'}
        };
        Plotly.newPlot('graph', data, layout);

        var startTime = new Date().getTime();
        ws.onmessage = function(event) {
            var data = JSON.parse(event.data);
            var currentTime = new Date().getTime() - startTime;
            currentTime = Math.floor(currentTime / 1000); // Convert to seconds
            var update = {
                x: [[currentTime]],
                y: [data]
            };
            Plotly.extendTraces('graph', update, [0]);
        };
    </script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    rtsp_url = "rtsp://user:4321q0220@192.168.10.121:554" # rtsp_url = "rtsp://username:password@ip_address:port/path"
    ffmpeg_command = [
        'ffmpeg',
        '-i', rtsp_url,
        '-vn',
        '-f', 's16le',
        '-ac', '1',
        '-ar', '44100',
        '-'
    ]
    # ffmpeg_command = [
    # 'ffmpeg',
    # '-i', rtsp_url,  # 입력 스트림
    # '-acodec', 'aac',  # 오디오 코덱을 AAC로 변경
    # '-ar', "44100",  # 샘플레이트를 변수에서 설정된 값으로 변경
    # '-ab', '64k',  # 비트레이트를 64kbps로 설정
    # '-vn',  # 비디오 스트림 제거
    # '-rtsp_transport', 'tcp',  # RTSP 스트림을 TCP를 통해 전송
    # 'output_audio.aac'  # 출력 파일명과 포맷
    # ]
    process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, bufsize=10**8)
    while True:
        raw_audio = process.stdout.read(44100 * 2)
        if not raw_audio:
            break
        audio_data = np.frombuffer(raw_audio, np.int16).tolist()
        await websocket.send_json(audio_data)
    await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
