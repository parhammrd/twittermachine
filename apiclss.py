#!/usr/bin/python
'''
	   softly config appending
	base  python-twitter
'''

import twitter
import time
import os
import sys
import importlib

try:
    os.mkdir("configs")
except FileExistsError:
    pass

sys.path.append('./configs/')

config = []
for file in os.listdir("./configs/"):
    if file.startswith("config") and file.endswith(".py"):
        config.append(importlib.import_module(file[:-3]))  # use secure class objects


def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=50, fill='█'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r %s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
    # Print New Line on Complete
    if iteration == total:
        print("{} is finished\n".format(prefix))


class apisugg(object):
    tag = 0

    def __init__(self, config):
        self.api = config
        self.rid = apisugg.tag
        self.init = time.time()
        apisugg.tag += 1

        # self.updatelimitrate(self.api)

    def __str__(self):
        return "{} {} {} // {} {} {} // {}\n".format(self.cous, self.cofw, self.cofr, self.coss, self.cosr, self.cosw,
                                                     self.costt)

    def updatelimitrate(self, api):

        if (self.init - time.time()) < 0:
            try:
                api.InitializeRateLimit()
            except:  # twitter.error.TwitterError:
                return False
            # print("api {}: Initialized\n".format(self.rid))

            self.usersshow = api.CheckRateLimit("/users/show")
            self.cous = self.usersshow.remaining

            self.followersids = api.CheckRateLimit("/followers/ids")
            self.cofw = self.followersids.remaining

            self.friendsids = api.CheckRateLimit("/friends/ids")
            self.cofr = self.friendsids.remaining

            self.statusshow = api.CheckRateLimit("/statuses/show/:id")
            self.coss = self.statusshow.remaining

            self.statusretweeters = api.CheckRateLimit("/statuses/retweeters/ids")
            self.cosr = self.statusretweeters.remaining

            self.statusretweets = api.CheckRateLimit("/statuses/retweets/ids")
            self.cosw = self.statusretweets.remaining

            self.searchtweet = api.CheckRateLimit("/search/tweets")
            self.costt = self.searchtweet.remaining

            print(self.__str__())

        return True

    def getapi(self, method, initvalue=False):

        check = self.updatelimitrate(self.api)
        if not check:
            method = {}
            initvalue = True

        print("api {}: adjust initial time as method {}".format(self.rid, method))

        if "us" in method:
            if self.cous > 3:
                self.cous -= 1
                print("api %s available: user show " % str(self.rid))  # api.GetUser(ID)
            else:
                check = False
                self.init = self.usersshow.reset
                print("api %s: user show is down" % str(self.rid))

        elif "fw" in method:
            if self.cofw > 1:
                self.cofw -= 1
                print("api %s available: follower list" % str(self.rid))  # api.GetFollowerIDsPaged
            else:
                check = False
                self.init = self.followersids.reset
                print("api %s: follower list is down" % str(self.rid))

        elif "fr" in method:
            if self.cofr > 1:
                self.cofr -= 1
                print("api %s available: friend list" % str(self.rid))  # api.GetFriendIDsPaged
            else:
                check = False
                self.init = self.friendsids.reset
                print("api %s: friend list is down" % str(self.rid))

        elif "ss" in method:
            if self.coss > 2:
                self.coss -= 1
                print("api %s available: status show" % str(self.rid))  # api.GetStatus(TweetID)
            else:
                check = False
                self.init = self.statusshow.reset
                print("api %s: status show is down" % str(self.rid))

        elif "sr" in method:
            if self.cosr > 2:
                self.cosr -= 1
                print("api %s available: status retweeter" % str(self.rid))  # api.GetRetweeters(TweetID, count=100)
            else:
                check = False
                self.init = self.statusretweeters.reset
                print("api %s: status retweeter is down" % str(self.rid))

        elif "sw" in method:
            if self.cosw > 2:
                self.cosw -= 1
                print("api %s available: status retweet" % str(self.rid))  # api.GetRetweets(a, count=100)
            else:
                check = False
                self.init = self.statusretweets.reset
                print("api %s: status retweet is down" % str(self.rid))

        elif "st" in method:
            if self.costt > 2:
                self.costt -= 1
                print("api %s available: search tweet" % str(self.rid))  # api.GetSearch(a, count=100)
            else:
                check = False
                self.init = self.searchtweet.reset
                print("api %s: search tweet is down" % str(self.rid))

        if check:
            return self.api
        else:
            if initvalue:
                self.init = time.time()
                time.sleep(1)
                check = self.updatelimitrate(self.api)

                if "us" in method:
                    self.init = self.usersshow.reset
                elif "fw" in method:
                    self.init = self.followersids.reset
                elif "fr" in method:
                    self.init = self.friendsids.reset
                elif "ss" in method:
                    self.init = self.statusshow.reset
                elif "sr" in method:
                    self.init = self.statusretweeters.reset
                elif "sw" in method:
                    self.init = self.statusretweets.reset
                elif "st" in method:
                    self.init = self.searchtweet.reset
                if check:
                    return self.init
                else:
                    return time.time() + 450
            else:
                return None


apilist = []
for conf in config:
    try:
        apilist.append(apisugg(twitter.Api(consumer_key=getattr(conf, "consumer_key"),
                                           consumer_secret=getattr(conf, "consumer_secret"),
                                           access_token_key=getattr(conf, "token"),
                                           access_token_secret=getattr(conf, "token_secret"))))
    except EOFError:
        print("config gets out, because an Error")
        continue

print("{} configs import\n".format(len(apilist)))

del config

ride = 0


def selectapi(method=""):
    global ride

    apit = apilist[ride % len(apilist)].getapi(method)

    if not type(apit) == twitter.api.Api:
        # sys.setrecursionlimit((len(apilist)*3))
        try:
            ride += 1
            # ; time.sleep(60)
            return selectapi(method)
        except:  # twitter.error.TwitterError and RecursionError : # ride < (len(apilist) * 3)
            ride = 0
            print("api sleeptimes initialized")
            timesc = [(i.getapi(method, True) - time.time()) for i in apilist]  # TypeError
            print("\t {}".format(timesc))

            sleep_time = max(timesc)
            print("\n\t program is going to sleep for {} s".format(sleep_time))
            printProgressBar(0, 1, prefix='sleeptime:', suffix='Load', length=50)

            for i in range(100):
                printProgressBar(i + 1, 100, prefix='sleeptime:', suffix='Load', length=50)
                time.sleep(abs(sleep_time) / 100)

            # sys.setrecursionlimit(1000)
            return selectapi(method)
    else:
        return apit
