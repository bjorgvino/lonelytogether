import web
import time
import requests
import MySQLdb
import json
from instagram import client, subscriptions

print "Setting up routes"
urls = (
  '/', 'index',
  '/callback', 'instagram_handler'
)

api = None
reactor = None
conn = None

def get_config(filename):
  with open(filename) as json_file:
    return json.load(json_file)

def get_database_connection():
  print "Connecting to database"
  if conn != None and conn.open:
    #print "Returned existing connection object"
    return conn
  #print "Opening new connection"
  return MySQLdb.connect(host=DATABASE_CONFIG['host'], user=DATABASE_CONFIG['username'], passwd=DATABASE_CONFIG['password'], db=DATABASE_CONFIG['db'])

def get_reactor():
  print "Creating subscriptions reactor"
  if reactor != None:
    #print "Returned existing reactor object"
    return reactor
  #print "Created new subscriptions reactor"
  return subscriptions.SubscriptionsReactor()

def get_api():
  print "Creating Instagram API"
  if api != None:
    print "Returned existing api object"
    return api
  print "Created new api object"
  return client.InstagramAPI(**CONFIG)

def process_tag_update(result):
  conn = get_database_connection()

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

class index:
  def GET(self):
    return "Hello, world!"

class instagram_handler:
  def GET(self):
    hub_data = web.input()
    if hub_data['hub.mode'] == 'subscribe':
      return hub_data['hub.challenge']
    return "Error"

  def POST(self):
    x_hub_signature = web.ctx.env.get('HTTP_X_HUB_SIGNATURE')
    raw_response = web.data()
    try:
      reactor = get_reactor()
      reactor.process(CONFIG['client_secret'], raw_response, x_hub_signature)
    except subscriptions.SubscriptionVerifyError:
      print "Signature mismatch"

print "Reading configuration files"
CONFIG = get_config('config/api.json')
APP_CONFIG = get_config('config/app.json')
DATABASE_CONFIG = get_config('config/db.json')

if __name__ == "__main__":
  #print "Subscribe to tag"
  #api.create_subscription(object='tag', object_id=APP_CONFIG['tag'], aspect='media', callback_url=APP_CONFIG['callback'])

  conn = get_database_connection()
  #api = get_api()
  reactor = get_reactor()

  print "Registering subscription callback"
  reactor.register_callback(subscriptions.SubscriptionType.TAG, process_tag_update)

  print "Starting application"
  app = web.application(urls, globals())
  app.run()
