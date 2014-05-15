import lonelyapp
from flask import Flask, request

app = Flask(__name__)

@app.route('/api')
def home():
  if request.args.get('ping', None) == '':
    return "Pong!\n"  
  return "Let\'s be lonely together!\n"

@app.route('/api/callback', methods=['GET'])
def instagram_subscription():
  if request.args.get('hub.mode', '') == 'subscribe':
    return request.args.get('hub.challenge')
  return "Error\n"

@app.route('/api/callback', methods=['POST'])
def instagram_tag_update_handler():
  x_hub_signature = request.headers.get('X-Hub-Signature', '')
  raw_response = request.data
  # TODO: Make the following run in the background
  lonelyapp.process_request(x_hub_signature, raw_response)
  return "Done\n"

if __name__ == '__main__':
    app.run(debug=True)