import os
import numpy as np
from PIL import Image
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image as tf_image

load_dotenv()
app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
UPLOAD_FOLDER = 'static/uploads/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

MODEL_ROTI_PATH = 'models/model-roti.h5'
model_roti = load_model(MODEL_ROTI_PATH, compile=False)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'status': {
            'code': 200,
            'message': 'Roti Roti, Roti Coklat, Roti Keju, Fried Chicken, Fried Chicken, Rotiiiiiiii'
        }
    }), 200

@app.route('/predict', methods=['POST'])
def predictRoti():
    if 'image' not in request.files:
        return jsonify({
            'status': {
                'code': 400,
                'message': 'No image file provided.'
            }
        }), 400
    
    reqImage = request.files['image']
    if reqImage and allowed_file(reqImage.filename):
        filename = secure_filename(reqImage.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        reqImage.save(filepath)
        
        img = Image.open(filepath).convert("RGB")
        img = img.resize((150, 150))
        x = tf_image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = x / 255.0
        
        detect_roti = model_roti.predict(x)[0][0]
        
        if detect_roti > 0.5:
            classType = 'Roti Tidak Berjamur'
            percentage = int(detect_roti * 100)
        else:
            classType = 'Roti Berjamur'
            percentage = 100 - int(detect_roti * 100)
        
        return jsonify({
            'status': {
                'code': 200,
                'message': 'Success predicting',
                'data': {
                    'classType': classType,
                    'percentage': percentage
                }
            }
        }), 200
    else:
        return jsonify({
            'status': {
                'code': 400,
                'message': 'Invalid file format. Please upload a JPG, JPEG, or PNG image.'
            }
        }), 400

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 8080)), host='0.0.0.0', debug=True)
