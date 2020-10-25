from bckclss import pCur, PSQLUser, DBC, friendlist, followerlist
import networkx as nx
import sys
import sqlite3 as sql


print('getting fiendship network for: ', sys.argv)


def get_friendship_graph(sqllite_db):
    session_pg = pCur()
    conn = sql.connect(sqllite_db+".db")
    cursor = conn.cursor()
    cursor.execute("select userid from dbUser")
    users_list = cursor
    edge_list = []
    for user in users_list:
        pquser = session_pg.query(PSQLUser). \
            filter(PSQLUser.userid == user)
        frnlist = friendlist.get_friend_list(pquser)
        flwlist = followerlist.get_follower_list(pquser)
        for frn in frnlist:
            edge = (user, frn)
            edge_list.append(edge)
        for flw in flwlist:
            edge = (flw, user)
            edge_list.append(edge)
    graph = nx.DiGraph()
    graph.from_edgelist(edge_list)
    nx.write_graphml(graph, sqllite_db + ".graphml")
    return graph


get_friendship_graph(sys.argv)

print('graphml saved: ', sys.argv)

