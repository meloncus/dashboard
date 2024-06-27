from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('audio_data')
def handle_audio_data(data):
    print("Received audio data:", data)
    # 클라이언트에 실시간으로 오디오 데이터 전송
    emit('audio_stream', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
