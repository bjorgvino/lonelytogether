import lonelyapp
import base64
import re
import uuid
import os
from flask import Flask, request, redirect, url_for

app = Flask(__name__)
dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
imageDir = os.path.join(os.path.dirname(__file__), 'public', 'uploads')

@app.route('/api/')
def home():
  if request.args.get('ping', None) == '':
    return "Pong!\n"  
  return "Let\'s be lonely together! Auto deploy enabled...\n"

@app.route('/api/callback', methods=['GET'])
def instagram_subscription():
  if request.args.get('hub.mode', '') == 'subscribe':
    return request.args.get('hub.challenge')
  return redirect(url_for('home'))

@app.route('/api/callback', methods=['POST'])
def instagram_tag_update_handler():
  x_hub_signature = request.headers.get('X-Hub-Signature', '')
  raw_response = request.data
  # TODO: Make the following run in the background
  lonelyapp.process_request(x_hub_signature, raw_response)
  return "Done\n"

@app.route('/api/upload', methods=['POST'])
def photobooth_upload_handler():
  # TODO: 
  # - Get post data: Username and image data
  dataUrl = request.form['dataUrl']
  username = request.form['username']
  imageB64Data = self.dataUrlPattern.match(imgdata).group(2)
  if imageB64Data is not None and len(imageB64Data) > 0:
    # - Decode image and save to disk with a unique filename
    imageData = base64.b64decode(imgb64)
    imageFilename = uuid.uuid4() + '.png'
    fh = open(os.path.join(imageDir, imageFilename, 'wb'))
    fh.write(imgData.decode('base64'))
    fh.close()
    # - Check for previous image in database, read the image and merge
    # - Save an entry in database 
    return "Done\n"
  else:
    return "error", 500

if __name__ == '__main__':
    app.run(debug=True)