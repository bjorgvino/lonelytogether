import MySQLdb, json, requests
from instagram import client, subscriptions

api = None
reactor = None
conn = None

def get_config(filename):
  with open(filename) as json_file:
    return json.load(json_file)

def get_database_connection():
  print "Connecting to database"
  global conn
  if not conn is None and conn.open:
    print "Returned existing connection object"
    return conn
  print "Opening new connection"
  return MySQLdb.connect(host=DATABASE_CONFIG['host'], user=DATABASE_CONFIG['username'], passwd=DATABASE_CONFIG['password'], db=DATABASE_CONFIG['db'])

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
  #conn = get_database_connection()
  global conn

  # Fetch images with tag 
  payload = {'count': 5, 'client_id': CONFIG['client_id']}
  r = requests.get('https://api.instagram.com/v1/tags/' + result['object_id'] + '/media/recent', params=payload)
  if r.status_code == 200:
    data = r.json()

    for entry in data['data']:
      if entry['type'] == 'image':
        try:
          cur = conn.cursor()
          image_url = entry['images']['standard_resolution']['url']
          entry_id = entry['id']
          username = entry['user']['username']
          cur.execute("""INSERT INTO posts (id, username, image_url) VALUES (%s, %s, %s)""", (entry_id, username, image_url))
          cur.close()
          conn.commit()
          print "Saved tag update to database"
        except Exception, e:
          print "Error processing tag update"
          print str(e)
          conn.rollback()
  else:
    print "Error when getting data from API"

  # Get current max id
  # c.execute("""SELECT max_tag_id FROM posts ORDER BY created_at DESC LIMIT 0, 1""")
  # max_tag_id = c.fetchone()
  # print max_tag_id

def get_random_photobooth_entry():
  global conn

  cur = conn.cursor(MySQLdb.cursors.DictCursor)
  cur.execute("""SELECT r1.id, r1.username, r1.image_filename FROM photobooth_posts AS r1 JOIN (SELECT (RAND() * (SELECT MAX(id) FROM photobooth_posts)) AS id) AS r2 WHERE r1.id >= r2.id ORDER BY r1.id ASC LIMIT 1;""")
  data = cur.fetchone()
  cur.close()
  return data

def save_photobooth_entry(username, imageFilename, randomEntryId=0):
  global conn

  print "Saving photobooth entry"
  try:
    cur = conn.cursor()
    cur.execute("""INSERT INTO photobooth_posts (username, image_filename, paired_id) VALUES (%s, %s, %s)""", (username, imageFilename, randomEntryId))
    insert_id = cur.lastrowid
    cur.close()
    conn.commit()
    return insert_id
  except Exception, e:
      print "Error saving photobooth entry"
      print str(e)
  return 0

def save_lonely_feed_entry(username, username2, image_filename, source, source_id):
  global conn

  print "Saving lonely feed entry"
  try:
    cur = conn.cursor()
    cur.execute("""INSERT INTO lonely_feed (left_username, right_username, image_filename, source, source_id) VALUES (%s, %s, %s, %s, %s)""", (username, username2, image_filename, source, source_id))
    insert_id = cur.lastrowid
    cur.close()
    conn.commit()
    return insert_id
  except Exception, e:
      print "Error saving lonely feed entry"
      print str(e)
  return 0

def get_feed(count, lastId):
  global conn
  try:
    print lastId
    par = (int(lastId), int(count))
    cur = conn.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT id, left_username, right_username, image_filename FROM lonely_feed WHERE id > %s ORDER BY id DESC LIMIT %s", par)
    data = cur.fetchall()
    cur.close()
    return json.dumps(data)
  except Exception, e:
    return str(e)

print "Reading configuration files"
CONFIG = get_config('config/api.json')
APP_CONFIG = get_config('config/app.json')
DATABASE_CONFIG = get_config('config/db.json')

api = get_api()
reactor = get_reactor()
conn = get_database_connection()

print "Registering subscription callback"
reactor.register_callback(subscriptions.SubscriptionType.TAG, process_tag_update)