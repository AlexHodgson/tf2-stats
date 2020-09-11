# -*- coding: utf-8 -*-
"""
Created on Sun Aug 23 19:27:14 2020

Saves ETF2L and logs.tf data to clever cloud mysql database

@author: Alex
"""

import mysql.connector as sql
from sql_info import SQL_HOST, SQL_PORT, SQL_DB, SQL_USER, SQL_PW



#def read_from_db():
    #print()
    
    
def write_player_info_to_db(playerInfo):
    """
    Writes player information to the SQL server

    :param playerInfo: dict
    Player info to be sent to server

    """

    # Connect to the sql server
    db_connection = sql.connect(host=SQL_HOST, port=SQL_PORT, database=SQL_DB, user=SQL_USER, password=SQL_PW)
    db_cursor = db_connection.cursor()

    local_hash = playerInfo['hash']

    check_hash_sql = ("SELECT Update_Hash "
                      "FROM Players "
                      "WHERE ETF2L_ID = %(ETF2L_ID)s")

    # Check if the entry is already in the server
    db_cursor.execute(check_hash_sql, playerInfo)

    try:
        server_hash = db_cursor.fetchone()[0]
    except sql.errors.InterfaceError and TypeError:
        server_hash = None
        print("Cannot find hash in server table")

    # Add entry, unless the server is already up to date
    if server_hash != local_hash:

        add_entry_sql = ("INSERT INTO Players "
                         "(ETF2L_ID, Name, Steam_ID, Join_Date, Update_Hash) "
                         "VALUES (%(ETF2L_ID)s, %(Name)s, %(Steam_ID)s, %(Join_Date)s, %(hash)s) "
                         "ON DUPLICATE KEY UPDATE "
                         "ETF2L_ID = %(ETF2L_ID)s, Name = %(Name)s, Steam_ID = %(Steam_ID)s, Join_Date = %(Join_Date)s, Update_Hash = %(hash)s")

        db_cursor.execute(add_entry_sql, playerInfo)
        db_connection.commit()

        print(f"Player record inserted/updated, ID: {db_cursor.lastrowid}")

    else:
        print("Server table already up to date")

    db_cursor.close()
    db_connection.close()
