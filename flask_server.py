import lonelyapp, base64, re, uuid, os, json
from flask import Flask, request, redirect, url_for, Response, render_template
from PIL import Image
from io import BytesIO

if __name__ == '__main__':
  app = Flask(__name__, static_url_path='', static_folder='public')
else:
  app = Flask(__name__)

dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
publicImageDir = os.path.join('uploads', 'photobooth_images')
imageDir = os.path.join(os.path.dirname(__file__), 'public', publicImageDir)
imageDirOriginals = os.path.join(imageDir, 'originals')

try: 
  os.makedirs(imageDirOriginals)
except OSError:
  if not os.path.isdir(imageDirOriginals):
    raise

@app.route('/')
def root():
  # Check if this method is used on production...we probably don't want that? Or do we? Then we could use render_template('index.html') instead
  return app.send_static_file('index.html')


@app.route('/photobooth/')
def photobooth():
  # Check if this method is used on production...we probably don't want that? Or do we? Then we could use render_template('index.html') instead
  return app.send_static_file('photobooth/index.html')


@app.route('/api/')
def home():
  if request.args.get('ping', None) == '':
    return "Pong!\n"  
  return "Let\'s be lonely together!\n"


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


@app.route('/api/getfeed', methods=['GET'])
def get_feed():
  count = request.args.get('count', 20)
  lastId = request.args.get('lastId', 0)
  return Response(response=lonelyapp.get_feed(count, lastId), status=200, mimetype="application/json")


@app.route('/api/entry/<int:entryId>', methods=['GET'])
def get_entry(entryId):
  entry = lonelyapp.get_entry(entryId)
  return Response(response=json.dumps(entry, encoding="iso-8859-1"), status=200, mimetype="application/json")


@app.route('/entry/<int:entryId>', methods=['GET'])
def get_entry_templated(entryId):
  entry = lonelyapp.get_entry(entryId)
  return render_template('entry.html', entry=entry)


@app.route('/api/upload', methods=['POST', 'OPTIONS'])
def photobooth_upload_handler():
  # Get post data: Username and image data
  dataUrl = request.form['dataUrl']
  username = request.form['username']
  imageB64Data = dataUrlPattern.match(dataUrl).group(2)
  if imageB64Data is not None and len(imageB64Data) > 0:
    # Decode image and save to disk with a unique filename
    imageData = base64.b64decode(imageB64Data)
    imageFilename = str(uuid.uuid4()) + '.jpg'
    i = Image.open(BytesIO(imageData))
    i.save(os.path.join(imageDirOriginals, imageFilename))

    # Fetch random entry from database
    randomEntry = lonelyapp.get_random_photobooth_entry()

    if randomEntry is None:
      # Save info in database and return
      print "Saving image info for first image"
      lonelyapp.save_photobooth_entry(username, imageFilename)
      return "First image", 500
    else:
      # Save info in database and carry on
      print "Saving image info before pairing"
      current_id = lonelyapp.save_photobooth_entry(username, imageFilename, randomEntry['id'])

      # Cropping original image
      width, height = i.size
      left = width/4
      top = 0
      right = 3 * left
      bottom = height
      cropped = i.crop((left, top, right, bottom))

      # Cropping paired image
      i2 = Image.open(os.path.join(imageDirOriginals, randomEntry['image_filename']))
      cropped2 = i2.crop((left, top, right, bottom))

      # Combine images and save the resulting image to disk
      combined = Image.new('RGB', (640, 480))
      combined.paste(cropped, (0, 0))
      combined.paste(cropped2, (320, 0))
      combined.save(os.path.join(imageDir, imageFilename))

      # Save paired info database
      lonelyapp.save_lonely_feed_entry(username, randomEntry['username'], imageFilename, 'photobooth', current_id)

      # Return combined image
      return os.path.join('/', publicImageDir, imageFilename)
  else:
    return "Error", 500

if __name__ == '__main__':
    lonelyapp.init(debug=True)
    app.run(debug=True)
    #app.run(host='0.0.0.0') # For testing against instagram api
