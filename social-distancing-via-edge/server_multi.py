from cores.core_async import YoloCamera
from flask import Flask, Response, render_template 

VIDEO_SOURCE = 'source_video/people-640p.mp4'  # if video
# VIDEO_SOURCE = 0  # if webcam
# camera = None

app = Flask(__name__)

def gen_frames(camera):  # generate frame by frame from camera
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

@app.route('/video_feed/<int:id>')
def video_feed(id):
    camera = YoloCamera('source_video/people-640p-' + str(id) + '.mp4')
    camera.thread_start()
    return Response(gen_frames(camera), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index_map_multi.html')

if __name__ == '__main__':
    # camera = YoloCamera(VIDEO_SOURCE)
    # camera.thread_start()
    app.run(host='0.0.0.0', port=5000, debug=False)
    # camera.thread_stop()
