#!./venv/bin/python
# -*- coding: utf-8 -*-
import json
import twitter
import logging

from bckclss import DBC, DBE, dbj, pCur
from bckclss import dbUser, dbTweet, dbUSjson, dbTWjson, dbEdges
from bckclss import PSQLTweet, PSQLUser, followerlist, friendlist

from order import wizard
from apiclss import selectapi
from datetime import datetime
from datetime import date

from sqlalchemy.orm.exc import NoResultFound

wiz = wizard()
nameewiz = wiz.revdir()

dbtquery = open(nameewiz, "r")
jobj = json.load(dbtquery)
dbtquery.close()

class clsuser(object):
	conjson = jobj['user']
	def __init__(self, userid, username=None):
		self.uinte = userid
		self.uname = username
		self._set_element()
		#if self.revindex():
			# pass
		#	self._get_user_info()
			# self._get_followers()
			# self._get_friends()

	def _set_element(self):
		session = DBC()
		try:
			if isinstance(self.uinte, int):
				usdb = session.query(dbUser).\
					filter(dbUser.userid == self.uinte).one()
			elif (self.uinte is None) and (self.uname is not None):
				usdb = session.query(dbUser).\
					filter(dbUser.screenname == self.uname).one()
		except NoResultFound:
			logging.error("object creation is not valid or didnt present in event cluster")
			usdb = False
			session.close()

		if usdb:
			self.index = usdb.getuserindex()
			self.active, self.uname, self.uinte , self.protected, self.followers_count, self.friends_count = usdb.revactus()
			session.close()
		else:
			self.index = False
			self.active = True
			self.protected, self.followers_count, self.friends_count = False, 0, 0

	def revindex(self):
		if self.index:
			return self.index
		else:
			if isinstance(self.uinte, int):
				self._get_user_info()
				return self.index
			else:
				return False

	def askpg(self):
		session = pCur()
		pquser = session.query(PSQLUser).\
			filter(PSQLUser.userid == self.uinte).one_or_none()

		if pquser is None:
			self.lastupdate = None
		else:
			self.lastupdate = pquser.revuptime()

		session.close()

	def _intermediator(self, obj):
		def _update_pg(uuid, userid):
			session = pCur()

			if uuid:
				point = session.query(PSQLUser).filter(PSQLUser.userid == userid).one()
				point.update()

			else:
				session.add(PSQLUser(userid))

			session.commit()
			session.close()

		def _json_pack(userid, inputjson):

			session = dbj()

			session.add(dbUSjson(userid, inputjson))
			session.commit()
			session.close()

		if self.uinte == obj['id'] or self.uname == obj['screen_name']:
			self.uinte = obj['id']
			self.uname = obj['screen_name']

			_update_pg((self.lastupdate is not None), self.uinte)
		else:
			logging.error("input and user doesn't match")
			return (0, 0, 0)

		lis = {}

		for key in obj.keys():
			if not isinstance(obj[key], dict):
				lis[key] = obj[key]

				# policy commit in document database

		_json_pack(self.uinte, lis)

		return obj

	def _recive_json(self, ext, inputjson):
		def _sqlite_commit_query(index, userid, uname, fjson):
			session = DBC()
			if fjson:
				if index:
					point = session.query(dbUser).filter(dbUser.index == index).one()
					point.recivejson(fjson)
					session.commit()
					session.close()
					return (0,1,0)
				else:
					point = dbUser(userid, uname)
					point.recivejson(fjson)
					session.add(point)
					session.commit()
					session.close()

					return (0,1,1)
			else:
				if index:
					point = session.query(dbUser).filter(dbUser.index == index).one()
					point.getdeactive()
					session.commit()
					session.close()
					return (1,1,0)
				else:
					if userid is not None:
						point = dbUser(userid, uname)
						point.getdeactive()
						session.add(point)
						session.commit()
						session.close()
						return (1,1,1)
					else:
						return (1,1,0)

		result = (0, 0, 0)
		if ext:
			result = _sqlite_commit_query(self.index, self.uinte, self.uname, inputjson)

		return result

	def _get_user_info(self, jjt = None):
		def _call_api_GUI( input):
			try: 
				if isinstance( input, int):
					usjsonfile = selectapi(["us"]).GetUser(user_id = input)
				else:
					usjsonfile = selectapi(["us"]).GetUser(screen_name = input)

				logging.debug("{} ==> Get User Info".format(input))
				return usjsonfile._json

			except twitter.error.TwitterError:
				logging.debug("TW: {} User Not Valid".format(input))
				return False

		def _call_json( id):

			'''
			this part must link with elasticsearch to determine document
			as jsonpack a sqlite intermediate data define to be for elasticsearch
			so just now we used this sqlite database

			'''
			session = dbj()
			try:
				dbjson = session.query(dbUSjson).\
					filter(dbUSjson.userid == id).\
					order_by(dbUSjson.index.desc()).first()

				js = dbjson._rev_json()
			except NoResultFound:
				logging.debug("unexpected uuid from jsonpack")
				return None

			session.close()

			return js

		config = self.conjson
		if isinstance(self.uinte, int):
			self.askpg()

			try:
				detla = datetime.now() - self.lastupdate
				delta = detla.seconds < config["fram"]*60
			except TypeError:
				delta = False
		else:
			self.lastupdate = None
			delta = False

		if delta:
				jjt = _call_json(self.uinte)
		elif jjt is None:
			if self.active or config["deactive"]:
				if isinstance(self.uinte, int):
					jjt = _call_api_GUI(self.uinte)

				elif (self.uinte is None) and (self.uname is not None):
					jjt = _call_api_GUI(self.uname)

				if jjt:
					jjt = self._intermediator(jjt)
			else:
				return (0, 0, 0)
		else:
			#print(jjt)
			jjt = self._intermediator(jjt)

		return self._recive_json( config["ext"], jjt)

	def _get_user_timeline(self):
		# def _gets_tweets(userid):

		pass
		# if self.active and not self.protected:
		# 	, ncursor = 

		# while ncursor:

		# 	= selectapi(["fw"]).GetUserTimeline(user_id = self.uinte, since_id = ,count = 200)

	def _get_followers(self):
		def _pass_page(userid, plist, npage):
			session = pCur()
			pquser = session.query(PSQLUser).\
				filter(PSQLUser.userid == userid).one()

			pqpage = session.query(followerlist).\
				filter(and_(followerlist.userid == userid, followerlist.page == npage)).one_or_none()

			if pqpage is None:
				pagfw = followerlist(userid, ncursor)
				pagfw.setlist(plist)
				pquser.fwpages.append(pagfw)
			else:
				pqpage.setlist(plist)

			session.commit()
			session.close()

		def _get_access(userid):
			session = pCur()
			gauser = session.query(PSQLUser).\
				filter(PSQLUser.userid == userid).one_or_none()
			number = session.query(followerlist).\
				filter(followerlist.userid == userid).count()

			if gauser is None:
				return 0, None
			else:
				if not number:
					session.close()
					return 0, -1
				else:
					n = gauser.fwpages[-1].revpage() # or -1
					session.close()
					return number, n  

		if self.active and (not self.protected):
	
			nfwpages, ncursor = _get_access(self.uinte)
		
			if ((int(self.followers_count) % 5000) + 1) == nfwpages and (ncursor is None):

				# print('dont need update now \n')
				return
		else:
			return

		while ncursor:
			try:
				fwjson = selectapi(["fw"]).GetFollowerIDsPaged(user_id=self.uinte, cursor=ncursor, count=5000)
			except twitter.error.TwitterError:
				try:
					if selectapi(["us"]).GetUser(self.uinte).protected :    
						# print("\t\t$ user protected {} \n\t\t\t ~follower list failed".format(self.uinte))
						break
					else:
						# print("\t\t$ access denied {} \n\t\t\t ~follower list failed".format(self.uinte))
						continue
				except twitter.error.TwitterError:
					# print("\t\t$ access denied {} \n\t\t\t ~follower list failed".format(self.uinte))
					break

			_pass_page(self.uinte, fwjson[2], ncursor)
			ncursor = fwjson[0]

		return

	def _get_friends(self):
		def _pass_page(userid, plist, npage):
			session = pCur()
			pquser = session.query(PSQLUser).\
				filter(PSQLUser.userid == userid).one()

			pqpage = session.query(friendlist).\
				filter(and_(friendlist.userid == userid, friendlist.page == npage)).one_or_none()

			if pqpage is None:
				pagfr = friendlist(userid, ncursor)
				pagfr.setlist(plist)
				session.add(pagfr)
			else:
				pqpage.setlist(plist)

			session.commit()
			session.close()

		def _get_access(userid):
			session = pCur()
			gauser = session.query(PSQLUser).\
				filter(PSQLUser.userid == userid).one_or_none()
			number = session.query(friendlist).\
				filter(friendlist.userid == userid).count()

			if gauser is None:
				return 0, None
			else:
				if not number:
					session.close()
					return 0, -1
				else:
					n = gauser.frpages[-1].revpage() # or -1
					print(n)
					session.close()
					return number, n  

		if self.active and not self.protected:
	
			nfrpages, ncursor = _get_access(self.uinte)
		
			if ((int(self.friends_count) % 5000) + 1) == nfrpages and (ncursor is None):

				print('dont need update now \n')
				return

		else:
			return

		while not ncursor == 0:
			try:
				frjson = selectapi(["fr"]).GetFriendIDsPaged(user_id=self.uinte, cursor=ncursor, count=5000)
			except twitter.error.TwitterError:
				try:
					if selectapi(["us"]).GetUser(self.uinte).protected :    
						# print("\t\t$ user protected {} \n\t\t\t ~ friend list failed".format(self.uinte))
						break
					else:
						# print("\t\t$ access denied {} \n\t\t\t ~ friend list failed".format(self.uinte))
						continue
				except twitter.error.TwitterError:
					# print("\t\t$ access denied {} \n\t\t\t ~ friend list failed".format(self.uinte))
					break

			_pass_page(self.uinte, frjson[2], ncursor)
			ncursor = frjson[0]

		return

class clstweet(object):
	conjson = jobj['tweet']
	def __init__(self, postid, userid=None):
		self.postid = postid
		self.userid = userid
		self._set_element()
		#if self.revindex():
		#	self._get_tweet_info()

	def _set_element(self):
		session = DBC()
		if isinstance(self.postid, int):
			twdb = session.query(dbTweet).\
				filter(dbTweet.postid == self.postid).one_or_none()
		else:
			logging.error("object creation is not valid")
			twdb = False

		session.close()

		if twdb:
			self.index = twdb.gettweetindex()
			self.active = twdb.revacttw()
			self.userid = twdb.revuser()
		else:
			self.index = False
			self.active = True

	def revindex(self):
		if self.index:
			return self.index
		else:
			if isinstance(self.postid, int):
				self._get_tweet_info()
				return self.index
			else:
				return False

	def askpg(self):
		session = pCur()
		pqutweet = session.query(PSQLTweet).\
			filter(PSQLTweet.postid == self.postid).one_or_none()
		
		session.close()

		if pqutweet is None:
			self.lastupdate = None
		else:
			self.lastupdate = pqutweet.revuptime()

	def _intermediator(self, obj):
		def _update_pg(uuid, postid):
			session = pCur()

			if uuid:
				point = session.query(PSQLTweet).filter(PSQLTweet.postid == postid).one()
				point.update()

			else:
				session.add(PSQLTweet(self.postid))

			session.commit()
			session.close()

		def _json_pack(postid, inputjson):

			session = dbj()

			session.add(dbTWjson(postid, inputjson))
			session.commit()
			session.close()


		if self.postid == obj['id']:
			self.postid = obj['id']
			self.userid = obj['user']['id']

			_update_pg((self.lastupdate is not None), self.postid)
		else:
			logging.debug("input and tweet doesn't match")
			return (0, 0, 0)

		lis = {}

		for key in obj.keys():
			if not isinstance(obj[key], dict):
				lis[key] = obj[key]

				# policy commit in document database

		_json_pack(self.postid, lis)

		return obj

	def _recive_json(self, ext, inputjson):
		def _sqlite_commit_query(index, postid, userid, fjson):
			session = DBC()
			if fjson:
				if index:
					point = session.query(dbTweet).filter(dbTweet.index == index).one()
					point.recivejson(fjson)
					session.commit()
					session.close()
					return (0,1,0)
				else:
					point = dbTweet(postid, userid)
					point.recivejson(fjson)
					session.add(point)
					session.commit()
					session.close()
					return (0,1,1)
			else:
				if index:
					point = session.query(dbTweet).filter(dbTweet.index == index).one()
					point.getdeactive()
					session.commit()
					session.close()
					return (1,1,0)
				else:
					point = dbTweet(postid, None)
					point.getdeactive()
					session.add(point)
					session.commit()
					session.close()
					return (1,1,1)

		result = (0, 0, 0)
		if ext:
			result = _sqlite_commit_query(self.index, self.postid, self.userid, inputjson)
		
		return result
		
	def _get_tweet_info(self, jjt = None):
		def _call_api_GTI( input):
			try: 
				twjsonfile = selectapi(["ss"]).GetStatus(input)
				logging.debug("{} ==> Get tweet Info".format(input))
				return twjsonfile._json

			except twitter.error.TwitterError:
				logging.debug("TW: {} tweet Not Valid".format(input))
				return False

		def _call_json( id):

			'''
			this part must link with elasticsearch to determine document
			as jsonpack a sqlite intermediate data define to be for elasticsearch
			so just now we used this sqlite database

			'''
			session = dbj()
			try:
				dbjson = session.query(dbTWjson).\
					filter(dbTWjson.postid == id).first()
					# order_by(dbTWjson.index.desc()).first()

				# print(dbjson)
				
				js = dbjson._rev_json()

			except NoResultFound:
				logging.debug("unexpected uuid from jsonpack")
				return None

			session.close()

			return js

		config = self.conjson
		self.askpg()
		
		try:
			detla = datetime.now() - self.lastupdate
			delta = detla.seconds < config["fram"]*60
		except TypeError:
			delta = False

		if delta:
			jjt = _call_json(self.postid)
		elif jjt is None:
			if self.active or config["deactive"]:
				jjt = _call_api_GTI(self.postid)

				if jjt:
					jjt = self._intermediator(jjt)
			else:
				return (0, 0, 0)
		else:
			jjt = self._intermediator(jjt)

		return self._recive_json( config["ext"], jjt)

class uevent:
	conjson = jobj
	def __init__(self, qindex):
		try:
			self.qindex = qindex
			qry = self.conjson["query"][qindex]
			query = qry["qname"]
			if qry['expire']:
				return 
		except ValueError:
			logging.debug("json query has problem {}".format(self.conjson['dbname']))
			return

		try:
			point = date.fromisoformat(query)
		except ValueError:
			point = False

		if query.endswith(".json"):
			self.listinput(query)
		elif query.endswith(".user"):
			clsuser(None, query[:-5])
		elif query.endswith(".export"):
			exfredges(self.conjson["dbname"]+query[:-7])
		elif isinstance(point, date):
			# point.replace(day = point.day-1)
			# limitapi = abs(point - date.today())
			# if limitapi.days > 7 :
			# 	qry['expire'] = True
			# 	self.commitchanges(qry)
			# 	return 
			qry['qname'] = ' '
			qry['until'] = query
			qry['since'] = point.replace(day = (point.day-1)).isoformat()

			self.commitchanges(qry)
			self.searchkeyword( qindex, qry)
		else:
			try:
				point = date.fromisoformat(qry['until'])
				# limitapi = abs(point - date.today())
				# if limitapi.days > 6 :
				# 	qry['expire'] = True
				# 	self.commitchanges(qry)
				# 	return
				point = date.fromisoformat(qry['since'])

				self.searchkeyword(qindex, qry)
			except TypeError:
				logging.debug("date queries need maintenance")
				return

	def commitchanges(self, config):
		self.conjson["query"][self.qindex] = config
		wiz.mkjson(self.conjson)
		wiz.reloadjson()

	def monitor(self, comstr, user):
		# doc = {'date': date.isoformat(date.today()),
		# 	'udeac': 0
		# 	'uchec': 0
		# 	'utotl': self.conjson['user']['number']
		# 	'tdeac': 0
		# 	'tchec': 0
		# 	'ttotl': self.conjson['tweet']['number']
		# 	'dbname': self.conjson["dbname"],
		# 	'runner': ""}
		# def desk( **config):
		# 	screen = "## \t \t \t \t \t ##\n" + "## \t \t \t {} \t ##\n".format(config['date']) + "   \t {}/{}/{} \t \t \t   \n".format(config['udeac'], config['uchec'], config['utotl']) 
		# 		+ "   \t {}/{}/{} \t {} \t   \n".format(config['tdeac'], config['tchec'], config['ttotl'], config['dbname']) + "## \t \t \t \t \t ##\n" + "## >/ {} ".format(config['runner'])
			
		# 	return print(screen, end = '\r')

		# doc['udeac'] += user[0]
		# doc['uchec'] += user[1]
		# doc['utotl'] += user[2]
		# doc['tdeac'] += tweet[0]
		# doc['tchec'] += tweet[1]
		# doc['ttotl'] += tweet[2]
		# doc['runner'] = comstr

		# desk(doc)

		return #doc['utotl'], doc['ttotl']

	def connected(self, query):
		session = DBC()

		if query.startswith("users"):
			points = session.query(dbUser).all()

			csv_file = open('./'+ self.conjson["dbname"] +'-users.csv', mode='w')

			csv_file.write("index , userid, screenname , followers , friends\n")

			for po in points:

				csv_file.write("{}, {}, {}, {}, {}\n".format(po.index ,po.userid ,po.screenname ,po.followers_count ,po.friends_count))


		elif query.startswith("tweets"):
			points = session.query(dbTweet).all()

			csv_file = open('./'+ self.conjson["dbname"] +'-tweets.csv', mode='w')
		elif query.startswith("edges"):

			# points = session.query(dbUser).all()

			csv_file = open('./'+self.conjson["dbname"]+'-edges.csv', mode='w')

			# csv_file.write("user, fr\n")

			session_edge = pCur()

			# for point in points:
			pquser = session_edge.query(PSQLUser).\
			filter(PSQLUser.userid == '240664869').one()

			if (not pquser is None): #or (point.userid == '240664869'):
				if not len(pquser.fwpages) == 0: #point.userid == '240664869':
					for page in pquser.fwpages:
						for i in page.flist:
							# if i in [pi.userid for pi in points]:
							# us = clsuser(i)
							csv_file.write("{}, {}\n".format(i, '240664869'))

				if not len(pquser.frpages) == 0:
					for page in pquser.frpages:
						for i in page.flist:
							# if i in [pi.userid for pi in points]:
							# us = clsuser(i)
							csv_file.write("{}, {}\n".format('240664869', i))
				# else:
				# 	continue

			session_edge.close()

		#         # get info to update
			# else:
			#     js = json.loads(user.usjson)

		#         csv_file.write("%s , %s , %s , %s , %s , %s , %s , %s , %s , %s , %s \n" % (str(user.index) ,str(user.screenname) ,str(user.lastupdate) ,str(js["created_at"]) ,str(js["statuses_count"]) ,str(js["favourites_count"]) ,str(js["followers_count"]) ,str(js["friends_count"]) ,str(js["default_profile"]) ,str(js["verified"]) ,str(js["protected"])))

			# if not user.botometer == None:
			#     uvb += 1
		session.close()
		csv_file.close()
		# print("total users: {} \t need GetUserInfo users: {} include botometer scores: {} \n \t\t total edges store: \n".format(len(users), uvu, uvb))    
		# input("press enter to continue ... ")

		# print("total tweets: {} \t total urls: {} & hashtags: {} & mention links: {} \n".format( len(tweets), len(urls), len(hashs), len(mentions))) 
		# for tweet in reversed(tweets):
		#     jj = json.loads(tweet.twjson)
		#     print("{}: {} : {} \n\t retweeted : {} favorited : {} \n\t hash : {}\n\t {} \n".format(tweet.index, jj['id'], jj['created_at'], jj['retweet_count'], jj['favorite_count'], len(jj['entities']['hashtags']),jj['full_text']))   
		#     break
		input("press enter to continue ... ")

	def exfredges(dbname):
		session_db = DBC()
		users_list = session_db.query(dbUser.userid).all()
		session_db.close()

		for uid in users_list:
			fid = clsuser(uid)
			fid.GetUserInfo()
			fid._get_followers()
			fid._get_friends()

		session_pg = pCur()
		seesion_eg = DBE()

		edge_list = []
		dlist = []

		# delete csv file for start

		for user in users_list:
		    try:
		        pquser = session_pg.query(PSQLUser). \
		            filter(PSQLUser.userid == user).one()
		    except NoResultFound:
		        dlist.append(user)
		        continue

		    frnpages = pquser.gfrpages()
		    flwpages = pquser.gfwpages()
		    for page in frnpages:
		        for frn in page.gfrlist():
		            edge = [user, frn]
		            edge_list.append(edge)
		    for page in flwpages:
		        for flw in page.gfwlist():
		            edge = [flw, user]
		            edge_list.append(edge)

		    # with open("sqlite/" + str(dbname) + ".csv", 'wb') as out:
		    #     csv_out = csv.writer(out, delimiter=";")

	        for row in edge_list:
	        		point = dbEdges(row[0], row[1])
					session.add(point)
					session.commit()

		print(dlist)
		session_pg.close()

	def getfrnlayersnetwork(layer, user, limit, edge_list):
	    clsuser._get_followers(user)
	    clsuser._get_friends(user)
	    for i in layer:
	        frnpages = user.gfrpages()
	        flwpages = user.gfwpages()
	        for page in frnpages:
	            for frn in page.gfrlist():
	                edge = (user[0], frn)
	                edge_list.append(edge)
	                newuser = clsuser._get_user_info(frn)
	                if newuser.followers_count() < limit:
	                    getfrnlayersnetwork(i, newuser, limit, edge_list)
	        for page in flwpages:
	            for flw in page.gfwlist():
	                edge = (flw, user[0])
	                edge_list.append(edge)
	                newuser = clsuser._get_user_info(flw)
	                if newuser.followers_count() < limit:
	                    getfrnlayersnetwork(i, newuser, limit, edge_list)

	        return edge_list

	def searchkeyword(self, qindex, config):

		if config['since'] is None:
			since = ""
		else:
			since = "%20since%3A{}".format(config['since'])

		if config['until'] is None:
			until = ""
		else:
			until = "%20until%3A{}".format(config['until'])

		if config['idpoint'] is None :
			idpoint = 0
		else:
			idpoint = config['idpoint']

		if config['idsince'] is None:
			idsince = 0
		else:
			idsince = config['idsince']

		if ' ' == config['qname']:
			subcon = "q=%20%20lang%3Afa"
		else:
			subcon = "q={}%20lang%3Afa".format(config['qname'])

		maxid = ""
		minid = ""
		
		#q=%20%20lang%3Afa%20until%3A2020-04-01%20since%3A2020-03-31&src=typed_query
		# idpoint = 1170673654583066624

		while(True):
			# print("spleep for 30s \n")
			# time.sleep(30)

			if not idsince or not until == "":
				maxid = ""
				minid = ""
	
			elif not idpoint:
				maxid = ""
				minid = "%20since_id%3A{}".format(idsince)
			elif idpoint < idsince:
				maxid = "%20max_id%3A{}".format(idpoint)
				# minid = "%20since_id%3A{}".format(idsince)
			else:
				maxid = "%20max_id%3A{}".format(idpoint)
				minid = "%20since_id%3A{}".format(idsince)
				try:
					idsince = tweets[0].id
				except UnboundLocalError:
					idsince = idpoint + 1

				config['idpoint'] = idpoint
				config['idsince'] = idsince

				self.commitchanges(config)

			tweets =[]

			print("{}{}{}{}{}".format(subcon, minid, maxid, until, since))
			try:
				tweets = selectapi(["st"]).GetSearch(raw_query= "{}{}{}{}{}".format(subcon, minid, maxid, until, since)) 
			except:
				continue
			#result_type='mixed' ,term=None, geocode=None, locale=None, return_json=False #until=euntil, since=esince,
			# since_id=1170115915964268545,      #, until=euntil, since=esince, count=15, include_entities=True
			
			until = ""

			if len(tweets):
				for result in tweets:

					user = clsuser(result.user.id)  ##
					user._get_user_info(result._json["user"])
					tweet = clstweet(result.id, result.user.id)   ##
					tweet._get_tweet_info(result._json)

					# self.monitor(str(result.id), user, tweet)

					if not idpoint:
						idpoint = result.id
						config['idpoint'] = idpoint
						if not idsince:
							idsince = result.id
							config['idsince'] = idsince
						
						self.commitchanges(config)
					else:
						idpoint = min(result.id, idpoint)
						config['idpoint'] = idpoint
						
						self.commitchanges(config)
			else:

				self.commitchanges(config)
				break

			idpoint = idpoint - 1

		return

	def listinput(self, filename):
		us = open('./'+filename, 'r')
		idlist = json.load(us)
		us.close()

		for i in idlist:
			fus = clsuser(i)

		 #    fus.GetUserInfo()
		    # fus._get_followers()
		    # fus._get_friends()

	# def botometerinput(self):
	#     us = open("./SNAPP_twitterUsers_bomResults_all-2.json")
	#     us = json.loads(us.read())

	#     for idd in us:
	#         session = DBC()
	#         session.query(dbUser).filter(dbUser.userid == idd).one()
	#         dbUser.botometer = json.dumps(us[idd])
	#         session.commit()
	
	#       return
