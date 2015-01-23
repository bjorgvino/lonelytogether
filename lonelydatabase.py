import datetime
from sqlalchemy import Column, Index, BigInteger, String, TIMESTAMP
from sqlalchemy.dialects import mysql, sqlite
from sqlalchemy.sql.expression import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

BigIntegerType = BigInteger()
BigIntegerType = BigIntegerType.with_variant(mysql.BIGINT(), 'mysql')
BigIntegerType = BigIntegerType.with_variant(sqlite.INTEGER(), 'sqlite')

Base = declarative_base()
 
class PhotoboothEntry(Base):
  __tablename__ = 'photobooth_posts'
  __table_args__ = {'mysql_engine':'InnoDB'}
  id = Column(BigIntegerType, primary_key=True, autoincrement=True)
  username = Column(String(30), index=True, nullable=False)
  image_filename = Column(String(2000), nullable=False)
  paired_id = Column(BigInteger, nullable=False, server_default="0")
  created_at = Column(TIMESTAMP, server_default=func.now())


class InstagramEntry(Base):
  __tablename__ = 'instagram_posts'
  __table_args__ = {'mysql_engine':'InnoDB'}
  id = Column(BigIntegerType, primary_key=True, autoincrement=True)
  username = Column(String(30), index=True, nullable=False)
  image_filename = Column(String(2000), nullable=True)
  post_id = Column(String(64), unique=True, nullable=False)
  image_url = Column(String(2000), nullable=False)
  paired_id = Column(BigInteger, nullable=False, server_default="0")
  created_at = Column(TIMESTAMP, server_default=func.now())
 

class FeedEntry(Base):
  __tablename__ = 'lonely_feed'
  __table_args__ = {'mysql_engine':'InnoDB'}
  id = Column(BigIntegerType, primary_key=True, autoincrement=True)
  left_username = Column(String(30), nullable=False)
  right_username = Column(String(30), nullable=False)
  image_filename = Column(String(2000), nullable=False)
  source = Column(String(20), nullable=False)
  source_id = Column(String(64), nullable=False)
  #created_at = Column(TIMESTAMP, server_default=func.now())
  created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)

Index('left_right_source', FeedEntry.left_username, FeedEntry.right_username, FeedEntry.source_id)
engine = create_engine('sqlite:///lonelytogether.db')

Base.metadata.create_all(engine)
