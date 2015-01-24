from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import lonelydatabase as db
import sys

connectionstring = 'sqlite:///lonelytogether.db'
engine = create_engine(connectionstring)
db.Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

entry1 = db.FeedEntry(left_username="left1", right_username="right1", image_filename="image1.jpg", source="test", source_id="1")
entry2 = db.FeedEntry(left_username="left2", right_username="right2", image_filename="image2.jpg", source="test", source_id="1")
entry3 = db.FeedEntry(left_username="left3", right_username="right3", image_filename="image3.jpg", source="test", source_id="1")

count = None
if len(sys.argv) > 1:
  count = sys.argv[1]

if count is None:
  print 'Adding 3 entries to the database'
  session.add(entry1)
  session.add(entry2)
  session.add(entry3)
elif count == "1":
  print 'Adding entry 1 to the database'
  session.add(entry1)
elif count == "2":
  print 'Adding entry 2 to the database'
  session.add(entry2)
elif count == "3":
  print 'Adding entry 3 to the database'
  session.add(entry3)

session.commit()
