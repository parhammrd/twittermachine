from bckclss import pCur, PSQLUser
import networkx as nx
import sys

print('getting fiendship network for: ', sys.argv)


def get_friendship_graph(sqllite_db):
    session = pCur()
    users_list = []
    edge_list = []
    for user in users_list:
        pqusers = session.query(PSQLUser). \
            filter(PSQLUser.userid == user)()
        for puser in pqusers:
            frnlist = PSQLUser.getfriends(puser)
            for frn in frnlist:
                edge = (user, frn)
                edge_list.append(edge)
    graph = nx.from_edgelist(edge_list)
    nx.write_graphml(graph, sqllite_db + ".graphml")
    return graph


get_friendship_graph(sys.argv)

print('graphml saved: ', sys.argv)

