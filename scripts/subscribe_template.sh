#!/bin/bash
# Example: ./subscribe add lonelytogether
CLIENT_ID=
CLIENT_SECRET=
CALLBACK=""
ACTION="$1"
TAG="$2"

if [ "$ACTION" = "add" ]; then
  echo "Adding subscription for tag: #$TAG"
  curl -F "client_id=$CLIENT_ID" \
       -F "client_secret=$CLIENT_SECRET" \
       -F "object=tag" \
       -F "aspect=media" \
       -F "object_id=$TAG" \
       -F "callback_url=$CALLBACK" \
       https://api.instagram.com/v1/subscriptions/
elif [ "$ACTION" = "remove" ]; then
  echo "Removing all subscriptions"
  curl -X DELETE "https://api.instagram.com/v1/subscriptions?client_secret=$CLIENT_SECRET&object=tag&client_id=$CLIENT_ID"
else
  echo "Listing all subscriptions:"
  curl "https://api.instagram.com/v1/subscriptions?client_secret=$CLIENT_SECRET&client_id=$CLIENT_ID"
fi
echo ""