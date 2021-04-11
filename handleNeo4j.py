import twitter
import logging
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

class App:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_friendship(self, userId1, userId2):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(
                self._create_and_return_friendship, userId1, userId2)
            for record in result:
                print("Created friendship between: {p1}, {p2}".format(
                    p1=record['p1'], p2=record['p2']))
    def create_retweet(self, userId1, userId2, hashtag):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(
                self._create_and_return_retweet, userId1, userId2,hashtag)
            for record in result:
                print("Created retweet between: {p1}, {p2}".format(
                    p1=record['p1'], p2=record['p2']))
    @staticmethod
    def _create_and_return_retweet(tx, userId1, userId2,hashtag):
        query=(
            "MERGE (p1:Person {name: $userId1}) ON MATCH SET  p1.hashtag = p1.hashtag + $hashtag, p1.lastLoggedInAt = timestamp() ON CREATE SET  p1.hashtag= [$hashtag], p1.createdAt= timestamp()"
            "MERGE (p2:Person {name: $userId2}) ON MATCH SET p2.hashtag = p1.hashtag +$hashtag, p2.lastLoggedInAt = timestamp() ON CREATE SET  p2.hashtag= [$hashtag], p2.createdAt= timestamp()"
            "MERGE (p1)-[r:retweeted]->(p2)"
            "RETURN p1, p2"
        )

        result = tx.run(query, userId1=userId1, userId2=userId2, hashtag= hashtag)
        try:
            return [{"p1": record["p1"]["name"], "p2": record["p2"]["name"]}
                    for record in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    @staticmethod
    def _create_and_return_friendship(tx, userId1, userId2):
        query=(
            "MERGE (p1:Person {name: $userId1}) ON MATCH SET p1.lastLoggedInAt = timestamp() ON CREATE SET p1.createdAt = timestamp()"
            "MERGE (p2:Person {name: $userId2}) ON MATCH SET p2.lastLoggedInAt = timestamp() ON CREATE SET p2.createdAt = timestamp()"
            "MERGE (p1)-[r:follows]->(p2)"
            "RETURN p1, p2"
        )

        result = tx.run(query, userId1=userId1, userId2=userId2)
        try:
            return [{"p1": record["p1"]["name"], "p2": record["p2"]["name"]}
                    for record in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

def connectToNeo4j():
    url = "bolt://localhost:7687"
    user = "neo4j"
    password = "2871375!!!"
    app = App(url, user, password)
    return app
    #app.close()

def getfrnlayersnetwork(user):
    app=connectToNeo4j()
    frnpages = user.gfrpages()
    flwpages = user.gfwpages()
    for page in frnpages:
        for frn in page.gfrlist():
            app.create_friendship(user[0], frn)
        for page in flwpages:
            for flw in page.gfwlist():
                app.create_friendship(flw, user[0])
    app.close()
def getRetweetLayersNetwork(userId,hashtag,retweetedFromId):
    app=connectToNeo4j()
    app.create_retweet(userId,retweetedFromId,hashtag)
    app.close()
