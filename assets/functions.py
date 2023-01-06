from datetime import *
import os
from nextcord import Embed, Member, TextChannel, User

from assets.not_allowed import no_invites, no_pings
from config import db


def check_illegal_invites(message, channel: int):
    if 'discord.gg' in message:
        if channel in no_invites:
            return True
        else:
            return False

def check_illegal_mentions(message, channel: int):
    pings = ['@everyone', '@here']
    if any(word in message for word in pings):
        if channel in no_pings:
            return True
        else:
            return False

def give_adwarn_auto(channel:TextChannel, member: int, moderator: int, warn_id: int, appeal_id:int):
    data = db.execute("SELECT * FROM warnData WHERE user_id = ?", (member,)).fetchone()
    current_time = datetime.now()
    next_warn = current_time + timedelta(hours=1)

    reason = f"Incorrectly advertising in {channel.mention}"
    if data == None:
        db.execute(
                "INSERT OR IGNORE INTO warnData (user_id, moderator_id, reason, warn_id, appeal_id) VALUES (?,?,?,?,?)",
                (member, moderator, reason, warn_id, appeal_id,))

        db.execute("INSERT OR IGNORE INTO warnData_v2 (user_id, warn_point, time) VALUES (?,?,?)",
                       (member, 1, round(next_warn.timestamp())))
        db.commit()

    elif data[2] < round(current_time.timestamp()):
        db.execute("UPDATE warnDatav2 SET warn_point = warn_point + ? AND time = ? WHERE user_id= ?", (1, round(next_warn.timestamp()), member,))
        
    elif data[2] > round(current_time.timestamp()):
        return False

def give_adwarn(channel, member: int, moderator: int, reason: str, warn_id:int, appeal_id:int):
    data = db.execute("SELECT * FROM warnData WHERE user_id = ?", (member,)).fetchone()
    current_time = datetime.now()
    next_warn = current_time + timedelta(hours=1)
    if data == None:
        db.execute(
                "INSERT OR IGNORE INTO warnData (user_id, moderator_id, reason, warn_id, appeal_id) VALUES (?,?,?,?,?)",
                (member, moderator, '{} - {}'.format(channel, reason), warn_id, appeal_id,))

        db.execute("INSERT OR IGNORE INTO warnData_v2 (user_id, warn_point, time) VALUES (?,?,?)",
                       (member, 1, next_warn))
        db.commit()

    elif data[2] < round(current_time.timestamp()):
        db.execute("UPDATE warnDatav2 SET warn_point = warn_point + ? AND time = ? WHERE user_id= ?", (1, round(next_warn.timestamp()), member,))
        db.commit()
        
    elif data[2] > round(current_time.timestamp()):
        return False
                
def get_warn_points(member: int) -> int:
    try:
        warnpointdata = db.execute(
            "SELECT warn_point FROM warnData_v2 WHERE user_id = ?", (member,)).fetchone()
        db.commit()
        return warnpointdata[0]
    except:
        return 1


def get_warn_id(member: int):
    data = db.execute("SELECT warn_id FROM warnData WHERE user_id = ?", (member,)).fetchone()
    return data[0]


def set_results(member: int):
    warn_point = get_warn_points(member)

    if warn_point < 3:
        result = "No action taken yet"
        return result

    elif warn_point == 3:
        result = "Member has reached the 3 warn point punishment. A 2 hour mute punishment was applied"
        return result

    elif warn_point == 6:
        result = "Member has reached the 6 warn point punishment. A kick punishment was applied"
        return result
    elif warn_point == 10:
        result = "Member has reached the 10 warn point punishment. A ban punishment was applied"
        return result


def send_adwarn(member: Member, reason: str):
    warnpointdata = db.execute("SELECT warn_point FROM warnData_v2 WHERE user_id = ?", (member.id,))
    warn_point = int(warnpointdata.fetchone()[0])

    warn_id = get_warn_id(member.id)

    result = set_results(member.id)

    embed = Embed(
        title="You have been warned", color=0xFF0000)
    embed.add_field(
        name="Reason of warn", value=reason, inline=True)
    embed.add_field(name="Warn ID", value=warn_id, inline=True)
    embed.add_field(name="Warn Points", value=warn_point, inline=True)
    embed.add_field(name="Result", value=result, inline=False)
    embed.set_footer(text="If you feel this warn was a mistake, please use `/appeal WARN_ID`")
    embed.set_thumbnail(url=member.display_avatar)


def strike_staff(department: str, member: int, strike_id: int, appeal_id: int):
    db.execute("INSERT OR IGNORE INTO strikeData (department, user_id, strike_id, appeal_id) VALUES (?,?,?,?)",
               (department, member, strike_id, appeal_id,))
    db.commit()


def get_strikes(department: str, member: int):
    data = db.execute("SELECT * FROM strikeData WHERE department = ? AND user_id = ?", (department, member,))

    try:
        return data.fetchall()
    except:
        return 0


def check_strike_id(strike_id: int, department: str):
    data = db.execute("SELECT * FROM strikeData WHERE strike_id = ? AND department = ?",
                      (strike_id, department,)).fetchone()

    if data == None:
        return None
    else:
        return data


def revoke_strike(department: str, strike_id: int):
    db.execute("DELETE FROM strikeData WHERE strike_id = ? AND department = ?", (strike_id, department))
    db.commit()


def get_appeal_id(strike_id: int, department: str):
    data = db.execute("SELECT appeal_id FROM strikeData WHERE strike_id = ? AND department = ?",
                      (strike_id, department)).fetchone()
    db.commit()
    return data[0]


def fetch_striked_staff(appeal_id: int, department: str):
    data = db.execute("SELECT * FROM strikeData WHERE appeal_id = ? AND department = ?",
                      (appeal_id, department,)).fetchone()
    db.commit()

    if data == None:
        return None
    else:
        return data


def add_partnership_request(user: int, server: int):
    db.execute("INSERT OR IGNORE INTO partnerData (user_id, guild_id) VALUES (?,?)",
               (user, server,))
    db.commit()


def get_partnership_request(user: int, server: int):
    data = db.execute("SELECT * FROM partnerData WHERE user_id = ? and guild_id = ?", (user, server,)).fetchone()
    db.commit()
    return data


def remove_partnership_request(user: int, server: int):
    db.execute("DELETE FROM partnerData WHERE WHERE user_id = ? and guild_id = ?", (user, server,))
    db.commit()

def check_partnership(server:int, user:int):
    if server == 740584420645535775:
        path="/partnerships/orleans/{}.txt".format(user)
        check=os.path.exists(path)
        if check == True:
            return True
        else:
            return "Partnership request not found!"    
    
    elif server == 925790259160166460:
        path = "/partnerships/hazeads/{}.txt".format(user)
        check = os.path.exists(path)
        if check == True:
            return True
        else:
            return "Partnership request not found!"
    
    

def add_verification_request(user:int):
    db.execute("INSERT OR IGNORE INTO verificationData (user) VALUES (?)", (user,))
    db.commit()

def check_verification_request(user:int):
    a=db.execute("SELECT user FROM verificatioData WHERE user=?", (user,)).fetchone()
    db.commit()
    if a==None:
        return False
    else:
        return a[0]

def check_loa_breaks():
    data = db.execute(
        "SELECT * FROM breakData WHERE accepted = ?", (1,)).fetchall()
    db.commit()
    return data

def remove_loa_break(member:Member):
    db.execute("DELETE FROM breakData WHERE user_id = ?", (member.id,))
    db.commit()

def check_plans(server:int):
    data = db.execute(
            "SELECT * FROM planData where server_id = ?", (server,)).fetchall()
    db.commit()
    return data

def remove_plan(plan_id:int, server:int):
    db.execute(
        'DELETE FROM planData WHERE plan_id= ? AND server_id= ?', (plan_id, server,))
    db.commit()

def add_break_request(user:User, server:int, break_id:int, duration:str, reason:str, accepted:int, start:int, ends:int):
    db.execute("INSERT OR IGNORE INTO breakData (user_id, guild_id, break_id, duration, reason, accepted, start, ends) VALUES (?,?,?,?,?,?,?,?)", (user.id, server, break_id, duration, reason, accepted, start, ends,))
    db.commit()

def fetch_break_id(break_id:int, server:int):
    data = db.execute("SELECT * FROM breakData WHERE break_id = ? AND guild_id = ?",
                      (break_id, server,)).fetchone()
    if data == None:
        return None
    else:
        return data

def approve_break(member:User, server:int, start:int, ends:int):
        db.execute("UPDATE breakData SET accepted = ? WHERE user_id = ? and guild_id = ?",
                           (1, member.id, server,))
        db.execute("UPDATE breakData SET start = ? WHERE user_id = ? and guild_id = ?",
                           (start, member.id, server,))
        db.execute("UPDATE breakData SET ends = ? WHERE user_id = ? and guild_id = ?",
                           (ends, member.id, server,))
        db.commit()

def deny_break(break_id:int, server:int):
    db.execute("DELETE FROM breakData WHERE break_id = ? and guild_id = ?", (break_id, server,))
    db.commit()

def end_break(member:User, server:int):
    db.execute("DELETE FROM breakData WHERE user_id = ? and guild_id = ?", (member.id, server,))
    db.commit()

def resign_apply(user:User):
    db.execute(
            "INSERT OR IGNORE INTO resignData (user_id, accepted) VALUES (?, ?)", (user.id, 0))
    db.commit()

def check_resign(member:User):
    data = db.execute(
        "SELECT * FROM resignData WHERE user_id = ?", (member.id,)).fetchone()
    db.commit()
    
    if data==None:
        return None
    else:
        return data

def approve_resign(member:User):
    db.execute("UPDATE resignData SET accepted = ? WHERE user_id = ?", (1, member.id,))
    db.commit()


def deny_resign(member: User):
    db.execute(
        "DELETE FROM resignData WHERE WHERE user_id = ?", (member.id,))
    db.commit()

def mark_untrusted(member:User, ending:int):
    db.execute("INSERT OR IGNORE INTO untrustedData (user, ending) VALUES (?,?)", (member.id, ending,))
    db.commit()

def check_untrusted():
    data=db.execute("SELECT * FROM untrustedData").fetchall()
    db.commit()

    if data == None:
        return None
    else:
        return data

def remove_untrusted(member:Member):
    db.execute("DELETE FROM untrustedData WHERE user = ?", (member.id))
    db.commit()

def add_plan(user:User, until:int, plan:str, claimee:User, plan_id, server:int):
    db.execute(
        "INSERT OR IGNORE INTO planData (user_id, started, until, plans, set_by, plan_id, server_id) VALUES (?,?,?,?,?,?,?)",
        (user.id, round(datetime.now().timestamp()), until, plan, claimee.id, plan_id, server,))
    db.commit()

def get_plan(plan_id:int, server:int):
    data = db.execute(
        "SELECT * FROM planData WHERE plan_id = ? AND server_id = ?", (plan_id, server,)).fetchone()
    
    if data == None:
        return None
    else:
        return data

    
