import os
import psycopg2
import sqlalchemy
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from os.path import join, dirname

database_url = os.environ.get("DATABASE_URL")
engine = create_engine(database_url)

Base = declarative_base(engine)
meta=MetaData(bind=engine)

# All my db table connections
last_msg = Table('last_msg', meta, autoload=True, autoload_with=engine, schema='bot')
people = Table('people', meta, autoload=True, autoload_with=engine, schema='bot')
groups = Table('groups', meta, autoload=True, autoload_with=engine, schema='bot')

# Store the most recent msg of every group in last_msg
def store_last_msg(groupId, msgId, msgText, name, senderId):
    conn = engine.connect()
    print("Storing last msg")
    s = select([last_msg]).where(last_msg.c.group_id == groupId)
    result = conn.execute(s)
    row = result.fetchall()
    if not row:
        print("Insert msg")
        ins = last_msg.insert().values(group_id = groupId, msg_id = msgId, msg_txt = msgText,\
                                        sender_name = name, sender_id = senderId)
        result = conn.execute(ins)
    else:
        print("Update msg")
        upd = last_msg.update().where(last_msg.c.group_id == groupId).\
        values(group_id = groupId, msg_id = msgId, msg_txt = msgText, sender_name = name, sender_id = senderId)
        result = conn.execute(upd)
    result.close()
    conn.close()
    print("Done storing msg")

# Retrieve the last message from a group
def find_last_msg(groupId):
    conn = engine.connect()
    print("Finding last msg")
    s = select([last_msg.c.msg_txt, last_msg.c.sender_name, last_msg.c.sender_id]).where(last_msg.c.group_id == groupId)
    result = conn.execute(s)
    row = result.fetchone()
    if not row:
        print("No group by that name")
        return None
    else:
        print("Found message")
        return row
    result.close()
    conn.close()
    print("Done finding last message")

# Add a person to the people table
def add_person(userId, name):
    conn = engine.connect()
    print("Adding person")
    s = select([people]).where(people.c.user_id == userId)
    result = conn.execute(s)
    row = result.fetchall()
    if not row:
        print("Insert person")
        ins = people.insert().values(user_id = userId, current_name = name)
        result = conn.execute(ins)
    else:
        print("Update person")
        upd = people.update().where(people.c.user_id == userId).values(user_id = userId, current_name = name)
        result = conn.execute(upd)
    result.close()
    conn.close()
    print("Done adding person")

# Add a group to the groups table
def add_group(groupId, botId):
    conn = engine.connect()
    print("Adding group")
    s = select([groups]).where(groups.c.group_id == groupId)
    result = conn.execute(s)
    row = result.fetchall()
    if not row:
        print("Insert group")
        ins = groups.insert().values(group_id = groupId, bot_id = botId)
        result = conn.execute(ins)
    else:
        print("Update group")
        upd = groups.update().where(groups.c.group_id == groupId).values(bot_id = botId)
        result = conn.execute(upd)
    result.close()
    conn.close()
    print("Done adding group")

# Find the bot id based on nickname
def find_bot_nname(nname):
        conn = engine.connect()
        print("Finding bot id from nickname")
        s = select([groups.c.bot_id]).where(groups.c.nickname == nname)
        result = conn.execute(s)
        row = result.fetchall()
        if not row:
            print("No bot here")
            return None
        else:
            print("Found bot")
            return row
        result.close()
        conn.close()
        print("Done finding bot id")

# Show all other availble bots for ventriloquism
def show_all_dummy():
        conn = engine.connect()
        print("Showing all dummies")
        s = select([groups.c.nickname])
        result = conn.execute(s)
        row = result.fetchall()
        if not row:
            print("No dummy bots")
            return None
        else:
            print("Got all dummies")
            return row
        result.close()
        conn.close()
        print("Done showing dummies")

# Get a user's id based on their name from the people table
def get_user_id(user_name):
    conn = engine.connect()
    print("Finding user id")
    s = select([people.c.user_id]).where(people.c.current_name == user_name)
    result = conn.execute(s)
    row = result.fetchone()
    if not row:
        print("No person currently has that name")
        return None
    else:
        print("Found "+ user_name + "'s id")
        return row
    result.close()
    conn.close()
    print("Done finding user id")

# Check if a bot is currently silenced
def check_silenced(botId):
    conn = engine.connect()
    print("Checking bot silence")
    s = select([groups.c.is_silenced]).where(groups.c.bot_id == botId)
    result = conn.execute(s)
    row = result.fetchone()
    if not row:
        print("No group with that bot")
        return None
    else:
        print("Found bot's group")
        return row
    result.close()
    conn.close()
    print("Done checking silence")

# Silence or awaken a particular bot
def silence_awaken_bot(botId, status):
    conn = engine.connect()
    print("Silence/awakening bot")
    s = select([groups.c.is_silenced]).where(groups.c.bot_id == botId)
    result = conn.execute(s)
    row = result.fetchone()
    if not row:
        print("No group with that bot")
        return None
    else:
        print("Bot's group found")
        upd = groups.update().where(groups.c.bot_id == botId).values(is_silenced = status)
        result = conn.execute(upd)
    result.close()
    conn.close()
    print("Done silence/awakening bot")
