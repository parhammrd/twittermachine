from bckclss import pCur, PSQLUser, DBC, friendlist, followerlist
import networkx as nx
import sys
from sqlalchemy.orm.exc import NoResultFound
import sqlite3 as sql
import csv

print('getting fiendship network for: ', sys.argv[1])


def get_friendship_graph(sqllite_db):
    session_pg = pCur()
    conn = sql.connect("sqlite/" + str(sqllite_db) + ".db")
    cursor = conn.cursor()
    cursor.execute("select userid from dbUser")
    users_list = cursor
    # conn.close()
    edge_list = []
    dlist = []
    for user in users_list:
        try:
            pquser = session_pg.query(PSQLUser). \
                filter(PSQLUser.userid == user[0]).one()
        except NoResultFound:
            dlist.append(user[0])
            continue

        frnpages = pquser.gfrpages()
        flwpages = pquser.gfwpages()
        for page in frnpages:
            for frn in page.gfrlist():
                edge = (user[0], frn)
                edge_list.append(edge)
        for page in flwpages:
            for flw in page.gfwlist():
                edge = (flw, user[0])
                edge_list.append(edge)

        break
    print(edge_list)
    with open("sqlite/" + str(sqllite_db) + ".csv", 'wb') as out:
        csv_out = csv.writer(out, delimiter=";")
        for row in edge_list:
            csv_out.writerow(row)
    conn.close()
    session_pg.close()
    # graph = nx.DiGraph()
    # g=nx.from_edgelist(edge_list)
    # nx.write_graphml(g, "sqlite/"+str(sqllite_db)+".graphml")
    # return graph


get_friendship_graph(sys.argv[1])
print('csv saved: ', sys.argv[1])
