import time

from cores.runtime_core_async import YoloCamera
from flask import Flask, Response, render_template 

VIDEO_SOURCE = 'source_video/people-640p.mp4'  # if video
# VIDEO_SOURCE = 0  # if webcam
camera = None

app = Flask(__name__)

def gen_frames():  # generate frame by frame from camera
    tic = time.time()
    
    while True:
        toc = time.time()
        print("M_Thread : ", '{:.2f}'.format(round((toc - tic) * 1000, 2)).rjust(10), "ms") ##

        frame = camera.get_frame()
        tic = time.time()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    camera = YoloCamera(VIDEO_SOURCE)
    camera.thread_start()
    app.run(host='0.0.0.0', port=5000, debug=False)
    camera.thread_stop()
