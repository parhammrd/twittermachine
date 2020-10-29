#!./venv/bin/python
# -*- coding: utf-8 -*-

"""
	db back bone 
"""
import json
from order import wizard
from datetime import datetime

from sqlalchemy import create_engine, Float, Column, Integer, String, BigInteger, Text, Boolean, JSON, null, DateTime, ARRAY, ForeignKey, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

wiz = wizard()
nameewiz = wiz.revdir()

dbtquery = open(nameewiz, "r")
jobj = json.load(dbtquery)
dbtquery.close()

#%% sqlite class objects

Base = declarative_base()

class dbUser(Base): 
	__tablename__ = "dbUser"
	index = Column('index', Integer, autoincrement=True, primary_key = True)
	userid = Column('userid', BigInteger, unique = True, nullable = False)
	screenname = Column('screenname', String(15))

	created_at = Column('created_at', DateTime)
	favourites_count = Column('likes', Integer)
	followers_count = Column('followers', Integer)
	friends_count = Column('friends', Integer)
	statuses_count = Column('tweets', Integer)
	listed_count = Column('list', Integer)
	location = Column('location', String(80))
	time_zone = Column('timezone', String(50))
	description = Column('description', String(200))
	profile_image_url = Column('profile_image_url', String(200))
	botometer = Column('botscore', Float)

	userverified = Column('verified', Boolean)
	useractive = Column('active', Boolean) #$
	userprotec = Column('protected', Boolean)
	default_profile = Column('defualtprofile', Boolean)

	tweets = relationship("dbTweet", backref="dbUser")
	# mentions = relationship("dbmention", backref="dbUser")
 
	def __init__(self, userid, screenname = None):
		self.userid = userid
		self.screenname = screenname
		self.useractive = True
		self.userprotec = False

	def getuserindex(self):
		return self.index

	def revactus(self):
		return self.useractive, self.screenname, self.userid, self.userprotec, self.followers_count, self.friends_count

	def getdeactive(self):
		self.useractive = False

	def setbotscore(self, cap):
		self.botometer = cap

	def recivejson(self, jsql):

		self.userid = jsql["id"]
		self.screenname = jsql["screen_name"]

		self.lang = jsql['lang']
		self.created_at = datetime.strptime(jsql['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
		self.favourites_count = jsql['favourites_count']
		self.followers_count = jsql['followers_count']
		self.friends_count = jsql['friends_count']
		self.statuses_count = jsql['statuses_count']
		self.listed_count = jsql['listed_count']
		self.location = jsql['location']
		self.time_zone = jsql['time_zone']
		self.description = jsql['description']
		self.profile_image_url = jsql['profile_image_url']
		self.userverified = jsql['verified']
		self.useractive = True
		self.userprotec = jsql['protected']
		self.default_profile = jsql['default_profile']

class dbTweet(Base):
	__tablename__ = "dbTweet"
	index = Column('index', Integer, autoincrement=True, primary_key = True)
	postid = Column('postid', BigInteger, unique = True, nullable = False)
	userid = Column(BigInteger, ForeignKey('dbUser.userid'))

	created_at = Column('created_at', DateTime)
	favorite_count = Column('likes', Integer)
	retweet_count = Column('retweets', Integer)
	text = Column('text', String(250))
	lang = Column('lang', String(5))
	full_text = Column('fulltext', Text)
	source = Column('source', Text)

	tweetacsable = Column('tweetacsable', Boolean)
	retweeted = Column('retweeted', Boolean)
	retweetwcom = Column('retweetwithcommand', Boolean)
	addentity = Column('addentity', Boolean)

	user = relationship("dbUser", back_populates="tweets")

	# tweet = relationship("dbretweetedges", backref="dbTweet")
	# retweets = relationship("dbretweetedges", backref="dbTweet")
	
	# urls = relationship("dbUrls", backref="dbTweet")
	# hashtags = relationship("dbHashtag", backref="dbTweet")
	# mentions = relationship("dbmention", backref="dbTweet")

	def __init__(self, postid, userid):
		self.postid = postid
		self.userid = userid
		self.tweetacsable = True
		self.addentity = True
	
	def gettweetindex(self):
		return self.index

	def revacttw(self):
		return self.tweetacsable

	def revuser(self):
		return self.userid

	def getdeactive(self):
		self.tweetacsable = False

	def recivejson(self, jsql):

		# print(jsql)

		self.postid = jsql['id']
		self.created_at = datetime.strptime(jsql['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
		self.favorite_count = jsql['favorite_count']
		self.retweet_count = jsql['retweet_count']
		self.lang = jsql['lang']

		try:
			self.fulltext = jsql['full_text']
		except KeyError:
			self.text = jsql['text']
		
		try:
			self.id_retweeted = jsql['retweeted_status']['id']
			self.retweetwcom = True
		
		except KeyError:
			self.retweet = jsql['retweeted']
			self.retweetwcom = False
		
		self.source = jsql['source']
		self.addentity = False
		self.tweetupdate = True
		self.tweetacsable = True
		
name = jobj["dbname"]

engine = create_engine('sqlite:///sqlite/{}.db'.format(name), echo = False)
Base.metadata.create_all(bind = engine)
DBC = sessionmaker(bind = engine)

# pool = declarative_base()

# class dbUrl(pool):
#     __tablename__ = "dbUrls"
#     index = Column('index', Integer, primary_key = True)
#     body = Column('body', JSON, nullable = False)

#     post_id = Column(Integer, ForeignKey('dbTweet.index'))
#     post = relationship("dbTweet", back_populates="urls")

#     def __init__(self, postid, body):
#         self.post_id = postid
#         self.body = json.dumps(body)

# class dbHashtag(pool):
#     __tablename__ = "dbHashtag"
#     index = Column('index', Integer, primary_key = True)
#     body = Column('body', JSON, nullable = False)

#     post_id = Column(Integer, ForeignKey('dbTweet.index'))
#     post = relationship("dbTweet", back_populates="hashtags")

#     def __init__(self, postid, body):
#         self.post_id = postid
#         self.body = body

# class dbmention(pool):
#     __tablename__ = "dbmention"
#     index = Column('index', Integer, primary_key = True)
#     created_at = Column('created_at', DateTime)
#     retweet_mention = Column('retweet_mention', Boolean)
#     body = Column('body', JSON, nullable = False)

#     post_id = Column(Integer, ForeignKey('dbTweet.index'))
#     # post = relationship("dbTweet", back_populates="mentions")

#     user_mentioned_id = Column(Integer, ForeignKey('dbUser.index')) # point uniqe user twitter id
#     user_mentioned = relationship("dbUser", back_populates = 'mentions') #backref=backref('mentions', uselist=False))

#     def __init__(self, time, postid, usermd, json):
#         self.created_at = datetime.strptime(time, '%a %b %d %H:%M:%S +0000 %Y')
#         self.post_id = postid
#         self.user_mentioned_id = usermd
#         self.body = json.dumps(json)

# engine = create_engine('sqlite:///sqlite/{}-P1pool.db'.format(name), echo = False)
# pool.metadata.create_all(bind = engine)
# DBE = sessionmaker(bind = engine)

#%% json class objects

jsoc = declarative_base()

class dbUSjson(jsoc): 
	__tablename__ = "dbUSjson"
	index = Column('index', Integer, primary_key = True, autoincrement=True)
	userid = Column('userid', BigInteger, nullable=False)
	dbjson = Column('dbjson', JSON, nullable = False)

	def __init__(self, userid, ordj):
		self.userid = userid
		self.dbjson = ordj

	def _rev_json(self):
		return self.dbjson

class dbTWjson(jsoc):
	__tablename__ = "dbTWjson"
	index = Column('index', Integer, primary_key = True, autoincrement=True)
	postid = Column('postid', BigInteger, nullable=False)
	dbjson = Column('dbjson', JSON, nullable = False)

	def __init__(self, postid, ordj):
		self.postid = postid
		self.dbjson = ordj

	def _rev_json(self):
		return self.dbjson
		
engine = create_engine('sqlite:///sqlite/jsonpack.db', echo = False)
jsoc.metadata.create_all(bind = engine)
dbj = sessionmaker(bind = engine)

#%% postgres class objects

Core = declarative_base()

class PSQLTweet(Core):
	__tablename__ = "PSQLTweet"
	postid = Column('postid', BigInteger, primary_key = True, unique = True)
	lastupdate = Column('lastupdate', DateTime)

	def __init__(self, postid):
		self.postid = postid
		self.lastupdate = datetime.now()

	def update(self):
		self.lastupdate = datetime.now()

	def revuptime(self):
		return self.lastupdate

class PSQLUser(Core):
	__tablename__ = "PSQLUser"
	userid = Column('userid', BigInteger, primary_key = True, unique = True)
	lastupdate = Column('lastupdate', DateTime)

	fwpages = relationship("followerlist", backref="PSQLUser")
	frpages = relationship("friendlist", backref="PSQLUser")

	def __init__(self, userid):
		self.userid = userid
		self.lastupdate = datetime.now()

	def update(self):
		self.lastupdate = datetime.now()

	def revuptime(self):
		return self.lastupdate

	def gfrpages(self):
		return self.frpages

	def gfwpages(self):
		return self.fwpages

class followerlist(Core):
	__tablename__ = "followerlist"
	index = Column('index', Integer, autoincrement=True, primary_key = True)
	userid = Column('userid', ForeignKey('PSQLUser.userid'))
	lastupdate = Column('lastupdate', DateTime)
	page = Column('page', BigInteger)
	flist = Column('ListFw', ARRAY(BigInteger))

	user = relationship("PSQLUser", back_populates="fwpages")
	
	def __init__(self, userid, cursor):
		self.userid = userid
		self.page = cursor

	def setlist(self, flist):
		self.flist = flist
		self.lastupdate = datetime.now()
	
	def revpage(self):
		return self.page

	def gfwlist(self):
		return self.flist

class friendlist(Core):
	__tablename__ = "friendlist"
	index = Column('index', Integer, autoincrement=True, primary_key = True)
	userid = Column('userid', ForeignKey('PSQLUser.userid'))
	lastupdate = Column('lastupdate', DateTime)
	page = Column('page', BigInteger)
	flist = Column('ListFr', ARRAY(BigInteger))

	user = relationship("PSQLUser", back_populates="frpages")
	
	def __init__(self, userid, cursor):
		self.userid = userid
		self.page = cursor

	def setlist(self, flist):
		self.flist = flist
		self.lastupdate = datetime.now()

	def revpage(self):
		return self.page

	def gfrlist(self):
		return self.flist

# class temporalEL():
# 	__tablename__ = "dbtemporalEL"
# 	index = Column('index', Integer, primary_key = True)
# 	created_at = Column('created_at', DateTime, oncreate=datetime.now())
# 	query = Column('query', String(20))
# 	snapshot = Column('AMsnapshot', Text)

# 	def __init__(self, query, snapshot):
# 		self.created_at = datetime.now()
# 		self.query = query
# 		self.snapshot = snapshot

engine = create_engine('postgresql://localhost/Psql_dbTwitterMachine')
Core.metadata.create_all(bind = engine)
pCur = sessionmaker(bind = engine)
