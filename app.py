from flask import Flask, render_template, Response, request
from flask_cors import CORS
import json
from PIL import Image
import base64
import io
import cv2
import numpy as np
import simplejpeg

#socket import
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
CORS(app)
font = cv2.FONT_HERSHEY_SIMPLEX
coord = (50, 50)
fontScale = 1
color = (255, 0, 0)
thickness = 2

# 1. socket - get frame
socketIo = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
@socketIo.on("frame")  
def handleMessage(data):
    result_str = data
    if(not result_str):
        print("no result")
    else:
        # 2. convert base64 to OpenCV frame
        b = bytes(result_str, 'utf-8')
        image = b[b.find(b'/9'):]
        
        # opt1: use pilImg
        # pilImg = Image.open(io.BytesIO(base64.b64decode(image)))
        # frame = cv2.cvtColor(np.array(pilImg), cv2.COLOR_BGR2RGB)
        
        # opt2: convert directly
        im_bytes = base64.b64decode(image)
        im_arr = np.frombuffer(im_bytes, dtype=np.uint8)
        frame = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)

		# 3. write on frame
        frame = cv2.putText(frame, 'OpenCV', coord, font,
							fontScale, color, thickness, cv2.LINE_AA)
        
        # 4. convert opencv frame to jpeg 
        # opt1: use imencode
        # retval, buffer = cv2.imencode('.jpg', frame)
        
        # opt2: use simplejpeg
        buffer = simplejpeg.encode_jpeg(frame, colorspace='BGR')
        
        # 5. convert jpeg to base64
        base64Bytes = base64.b64encode(buffer)
        json_string = json.dumps({'image': base64Bytes.decode("utf-8")})
    
        # 6. send frame back
        emit("frame", json_string, broadcast=True)

        
# 2. http
# @app.route('/api', methods=['POST', 'GET'])
# def api():
#     # 1. get the post request's json
# 	data = request.get_json()
 
# 	# 2. convert to base to PILimage then OpenCV frame
# 	result_str = data['data']
# 	b = bytes(result_str, 'utf-8')
# 	image = b[b.find(b'/9'):]
# 	pilImg = Image.open(io.BytesIO(base64.b64decode(image)))
# 	frame = cv2.cvtColor(np.array(pilImg), cv2.COLOR_BGR2RGB)	
 
# 	# 3. write on frame
# 	font = cv2.FONT_HERSHEY_SIMPLEX
# 	coord = (50, 50)
# 	fontScale = 1
# 	color = (255, 0, 0)
# 	thickness = 2
# 	frame = cv2.putText(frame, 'OpenCV', coord, font,
#                      fontScale, color, thickness, cv2.LINE_AA)

#     # 4. convert opencv frame to base64 string
# 	retval, buffer = cv2.imencode('.jpg', frame)
# 	base64String = base64.b64encode(buffer)
 
# 	# 5. send base64 back to react
# 	return base64String


if __name__ == '__main__':
	app.run(host='0.0.0.0')
	socketIo.run(app, debug=True)



