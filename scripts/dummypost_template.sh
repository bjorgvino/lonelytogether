#!/bin/bash
SIGNATURE=2c86357c6edd4ab4b473aafd56a34e24efd256a3
SUBSCRIPTION_ID=000000

curl -H "Content-Type: application/json" \
     -H "X-Hub-Signature: $SIGNATURE" \
     -d '[{"changed_aspect": "media", "object": "tag", "object_id": "lonelytogether", "time": 1399803381, "subscription_id": $SUBSCRIPTION_ID, "data": {}}]' http://localhost:5000/api/callback
     
