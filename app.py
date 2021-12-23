#!/usr/bin/env python
from importlib import import_module
import os
from flask import Flask, render_template, Response, request, redirect,\
    url_for, make_response, jsonify
from werkzeug.utils import secure_filename
import cv2
import time
from datetime import timedelta

# import camera driver
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera import Camera

# from camera_opencv import Camera

# Raspberry Pi camera module (requires picamera package)
# from camera_pi import Camera

app = Flask(__name__)
# 设置静态文件缓存过期时间
app.send_file_max_age_default = timedelta(seconds=1)

# 设置允许的文件格式
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'JPG', 'PNG', 'bmp'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/', methods=['POST', 'GET'])
def index():
    """Video streaming home page."""
    if request.method == 'POST':
        f = request.files['file']

        if not (f and allowed_file(f.filename)):
            return jsonify({"error": 1001,
                            "msg": "请检查图片类型，仅限于'png', 'jpg', 'JPG', 'PNG', 'bmp'"})
        basepath = os.path.dirname(__file__)  # 当前文件所在路径

        # 注意：没有的文件夹一定要先创建，不然会提示没有该路径
        upload_path = os.path.join(basepath, 'static/images', secure_filename(f.filename))

        f.save(upload_path)
        # 使用Opencv转换一下图片格式和名称
        img = cv2.imread(upload_path)
        cv2.imwrite(os.path.join(basepath, 'static/images', 'test.jpg'), img)
        return render_template('index_ok.html', val1=time.time())
    return render_template('index.html')


def gen(camera):
    """Video streaming generator function."""
    yield b'--frame\r\n'
    while True:
        frame = camera.get_frame()
        yield b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n--frame\r\n'


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='127.0.0.1', threaded=True, debug=True)
