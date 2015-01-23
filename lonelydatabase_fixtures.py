from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from lonelydatabase import Base, FeedEntry

connectionstring = 'sqlite:///lonelytogether.db'
engine = create_engine(connectionstring)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

entry = FeedEntry(left_username="left1", right_username="right1", image_filename="image1.jpg", source="test", source_id="1")
session.add(entry)
session.commit()