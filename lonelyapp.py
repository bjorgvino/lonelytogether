import json, requests, uuid, os
from instagram import client, subscriptions
from StringIO import StringIO
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import func
from lonelydatabase import Base, PhotoboothEntry, InstagramEntry, FeedEntry, row2dict
from contextlib import contextmanager

# Define module variables
api = None
reactor = None
debugMode = False
randomFunc = None
DBSession = None
CONFIG = {
  "client_id": "",
  "client_secret": "",
  "redirect_uri": ""
}

# Make sure all image directories exist
publicImageDir = os.path.join('uploads', 'instagram_images')
imageDir = os.path.join(os.path.dirname(__file__), 'public', publicImageDir)
imageDirOriginals = os.path.join(imageDir, 'originals')

try: 
  os.makedirs(imageDirOriginals)
except OSError:
  if not os.path.isdir(imageDirOriginals):
    raise

@contextmanager
def session_scope():
  """Provide a transactional scope around a series of operations."""
  session = DBSession()
  try:
    yield session
    session.commit()
  except:
    session.rollback()
    raise
  finally:
    session.close()

def init(debug):
  global debugMode
  global randomFunc
  debugMode = debug
  if debugMode:
    connectionstring = 'sqlite:///lonelytogether.db'
    randomFunc = func.random
  else:
    CONFIG = get_config('config/api.json')
    DB = get_config('config/db.json')
    connectionstring = 'mysql+pymysql://{0}:{1}@{2}/{3}'.format(DB['username'], DB['password'], DB['host'], DB['db'])
    randomFunc = func.rand
  engine = create_engine(connectionstring)
  Base.metadata.bind = engine
  global DBSession
  DBSession = sessionmaker(bind=engine)

def get_config(filename):
  with open(filename) as json_file:
    return json.load(json_file)

def get_reactor():
  print "Creating subscriptions reactor"
  global reactor
  if not reactor is None:
    print "Returned existing reactor object"
    return reactor
  print "Created new subscriptions reactor"
  return subscriptions.SubscriptionsReactor()

def get_api():
  print "Creating Instagram API"
  global api
  if not api is None:
    print "Returned existing api object"
    return api
  print "Created new api object"
  return client.InstagramAPI(**CONFIG)

def process_request(x_hub_signature, raw_response):
  try:
    #reactor = get_reactor()
    global reactor
    reactor.process(CONFIG['client_secret'], raw_response, x_hub_signature)
  except subscriptions.SubscriptionVerifyError:
    print "Signature mismatch"

def process_tag_update(result):
  # Fetch images with tag 
  payload = {'count': 1, 'client_id': CONFIG['client_id']}
  r = requests.get('https://api.instagram.com/v1/tags/' + result['object_id'] + '/media/recent', params=payload)
  if r.status_code == 200:
    data = r.json()
    try:
      for entry in data['data']:
        if entry['type'] == 'image':
          try:
            # Collect data
            entry_id = entry['id']
            username = entry['user']['username']
            image_url = entry['images']['standard_resolution']['url']
            imageFilename = str(uuid.uuid4()) + '.jpg'
            
            # Fetch image and save to disk
            r = requests.get(image_url)
            i = Image.open(StringIO(r.content))
            i.save(os.path.join(imageDirOriginals, imageFilename))

            # Fetch random entry from database
            randomEntry = get_random_instagram_entry()

            if randomEntry is None:
              # Save info in database and return
              print "Saving image info for first instagram image"
              save_instagram_entry(username, imageFilename, image_url, entry_id)
              print "Saved first tag update to database"
            else:
              # Save info in database and carry on
              print "Saving image info before pairing"
              current_id = save_instagram_entry(username, imageFilename, image_url, entry_id, randomEntry['id'])
              if current_id > 0:
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
                save_lonely_feed_entry(username, randomEntry['username'], imageFilename, 'instagram', current_id)
                print "Saved tag update to database"
              else:
                print "Duplicate entry, not saved to database"
          except Exception, e:
            print "Error processing tag update"
            print str(e)
    except Exception, e:
      print "Error processing tag update"
      print str(e)
  else:
    print "Error when getting data from API"

def get_random_photobooth_entry():
  with session_scope() as session:
    try:
      dbEntry = session.query(PhotoboothEntry).order_by(randomFunc()).limit(1).first()
      entry = row2dict(dbEntry)
      return entry
    except Exception, e:
      print "Error getting random photobooth entry"
      print str(e)
      return None

def get_random_instagram_entry():
  try:
    conn = get_database_connection()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("""SELECT r1.id, r1.username, r1.image_filename FROM posts AS r1 JOIN (SELECT (RAND() * (SELECT MAX(id) FROM posts)) AS id) AS r2 WHERE r1.id >= r2.id ORDER BY r1.id ASC LIMIT 1;""")
    data = cur.fetchone()
    cur.close()
  except Exception, e:
    print "Error getting random instagram entry"
    print str(e)
    data = None
  finally:
    if conn is not None and conn.open:
      conn.close()
  return data

def save_photobooth_entry(username, imageFilename, randomEntryId=0):
  print "Saving photobooth entry"
  with session_scope() as session:
    try:
      entry = PhotoboothEntry(username=username, image_filename=imageFilename, paired_id=randomEntryId)
      session.add(entry)
      session.commit()
      print "Inserted ID=" + str(entry.id)
      return entry.id
    except Exception, e:
      print "Error saving photobooth entry"
      print str(e)
    return 0

def save_instagram_entry(username, imageFilename, imageUrl, postId, randomEntryId=0):
  print "Saving instagram entry"
  try:
    conn = get_database_connection()
    cur = conn.cursor()
    cur.execute("""INSERT INTO posts (username, image_filename, post_id, image_url, paired_id) VALUES (%s, %s, %s, %s, %s)""", (username, imageFilename, postId, imageUrl, randomEntryId))
    insert_id = cur.lastrowid
    cur.close()
    conn.commit()
    return insert_id
  except Exception, e:
    print "Error saving photobooth entry"
    print str(e)
  finally:
    if conn is not None and conn.open:
      conn.close()
  return 0

def save_lonely_feed_entry(username, username2, image_filename, source, source_id):
  print "Saving lonely feed entry"
  with session_scope() as session:
    try:
      entry = FeedEntry(left_username=username, right_username=username2, image_filename=image_filename, source=source, source_id=source_id)
      session.add(entry)
      session.commit()
      print "Inserted ID=" + str(entry.id)
      return entry.id
    except Exception, e:
      print "Error saving lonely feed entry"
      print str(e)
    return 0

def get_feed(count, lastId):
  with session_scope() as session:
    try:
      feed = session.query(FeedEntry).filter(FeedEntry.id > lastId).order_by(FeedEntry.id.desc()).limit(count).all()
      feedDict = []
      for feedEntry in feed:
        feedDict.append(row2dict(feedEntry))
      return json.dumps(feedDict, encoding="iso-8859-1")
    except Exception, e:
      print str(e)
      return str(e)

def get_entry(entryId):
  with session_scope() as session:
    try:
      dbEntry = session.query(FeedEntry).filter(FeedEntry.id == entryId).first()
      entry = row2dict(dbEntry)
      return entry
    except Exception, e:
      print str(e)
      return str(e)

api = get_api()
reactor = get_reactor()

print "Registering subscription callback"
reactor.register_callback(subscriptions.SubscriptionType.TAG, process_tag_update)
