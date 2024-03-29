# bot.py

# load discord
import os
import discord
from discord import app_commands
from typing import Optional
from dotenv import load_dotenv
from io import BytesIO
from random import randint, choice, sample
import math
import json
import asyncio
import requests
from prettytable import PrettyTable
from datetime import timedelta
from arrow import arrow
from discord_timestamps import format_timestamp, TimestampType

intents = discord.Intents.default()
intents.messages = True
intents.reactions = True

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        for guild in self.guilds:
            self.tree.clear_commands(guild=guild)
        self.tree.add_command(self.tree.get_command("help"), override=True)
        self.tree.add_command(self.tree.get_command("run"), override=True)
        await self.tree.sync()

bot = MyClient(intents=intents)

topg = os.getenv('TOPGG_TOKEN')

story = ""
unitss = []




# embeds
class error_embed(discord.Embed):
    def __init__(self, error):
        super().__init__()
        self.title = f"error! invalid {error}."
        self.description = f"check `/help` to see if your {error.split()[-1]} is in the right format. otherwise, please join the support server here.\nhttps://discord.gg/GPfpUNmxPP"
        self.color = discord.Color.dark_red()

# the command
@bot.tree.command(name="help", description="help")
async def help(interaction):
    print(f"/help was used in {interaction.channel} ({interaction.guild}) by {interaction.user}.")

    help1 = """prefix
    
the letter that comes before the serial number (e.g. 'S' for tripleS)

lineup
list of members, space-separated

ggrav
a list of grand gravity strings (strings that specify the number of members, then each unit separated by periods, e.g. '8.aaa.kre'). these gravity strings should be separated by two periods.

egrav
a list of grand gravity strings (strings that specify the number of members, then each song separated by periods, e.g. '10.a.b.c.d.e.f.g.h'). these gravity strings should be separated by two periods.

haus (defaults to the original HAUS 1 and 2 in gyeonggi-do) 
a valid haus.json file, with a seoul HAUS in case of gravity. the default haus.json file can be found here (https://github.com/shuu-wasseo/tripleS-simulator-bot/blob/main/haus.json)"""

    help2 = """random_members (defaults to False)
whether the reveal of the members is random or in the specified order.

unit (defaults to "")
units and their descriptions, in the same format as gravity strings

random_ggrav (defaults to False)
whether grand gravity is random or chosen by the user(s) through voting (with emojis). requires voting for the bot on top.gg to enable.
https://top.gg/bot/1041703388057960479/vote

random_egrav (defaults to False)
whether event gravity is random or chosen by the user(s) through voting (with emojis). requires voting for the bot on top.gg to enable.
https://top.gg/bot/1041703388057960479/vote"""

    sample = """if you don't know where to start, you can try this first!\n```/run prefix: S lineup: ysy jhr ljw kcy kyy ksm knk gyb ked sdh ktn kyj ggrav: 8.aaa.kre egrav: 10.a.b.c.d.e.f.g.h unit: aaa.acid angel from asia..kre.krystal eyes random_ggrav: false random_egrav: false```"""

    embed1 = discord.Embed(title = "compulsory parameters", description = "these parameters must be passed.")
    for x in help1.split("\n\n"):
        embed1.add_field(name = x.split("\n")[0], value = x.split("\n")[1], inline = True)
    embed2 = discord.Embed(title = "optional parameters", description = "these parameters need not be passed.")
    for x in help2.split("\n\n"):
        embed2.add_field(name = x.split("\n")[0], value = x.split("\n")[1], inline = True)
    embed3 = discord.Embed(title = "sample command", description = sample)

    embeds = [embed1, embed2, embed3]

    for e in embeds:
        e.color = discord.Color.teal()

    await interaction.response.send_message("how to use `/run`:", embeds=embeds)

@bot.tree.command(name="run", description="run the simulator")
async def run(
    interaction, 
    prefix: str, lineup: str, 
    haus: Optional[discord.Attachment], 
    random_members: Optional[bool] = False, 
    unit: Optional[str] = "", 
    egrav: Optional[str] = "", random_egrav: Optional[bool] = True, 
    ggrav: Optional[str] = "", random_ggrav: Optional[bool] = True
):

    global unitss
    global story
    global topg

    # parsing strings
    members = lineup.split(" ")
    egravs = [g.split(".") for g in egrav.split("..")]
    ggravs = [g.split(".") for g in ggrav.split("..")]
    unitss = [u.split(".") for u in unit.split("..")]

    # verification
    for x in ggravs:
        if x in ([""], []):
            ggravs.remove(x)
        elif len(x) < 3:
            await interaction.followup.send(embed=error_embed("grand gravity string"))
            return

    for x in egravs:
        if x in ([""], []):
            egravs.remove(x)
        elif len(x) not in [5, 9, 17]:
            await interaction.followup.send(embed=error_embed("event gravity string"))
            return

    if haus != None:
        try:
            ohaus = requests.get(haus).json() 
        except:
            await interaction.followup.send(embed=error_embed("HAUS string"))
            return
    else:
        ohaus = json.load(open("haus.json"))

    print(f"/run was used in {interaction.channel} ({interaction.guild}) by {interaction.user}.")
    print(f"""prefix: {prefix}, lineup, {lineup}, 
    haus: {haus}, random_members: {random_members}
    unit: {unitss}
    egrav: {egravs}, random_egrav: {random_egrav}
    ggrav: {ggravs}, random_ggrav: {random_ggrav}""")

    args = discord.Embed(title=f"{interaction.user.display_name} ({interaction.user.name})'s triple{prefix.upper()} simulation", description=f"lineup:\n{' '.join(lineup.split())}", color=discord.Color.dark_green())

    for name, element in {"haus": haus, "random_members": random_members, "unit": unitss, "egrav": egravs, "random_egrav": random_egrav, "ggrav": ggravs, "random_ggrav": random_ggrav}.items():
        if type(element) == bool:
            if (element == random_members and not element) or (element in [random_egrav, random_ggrav] and element):
                value = f"{element} (default)"
            else:
                value = f"{element}"
        elif type(element) == list:
            if element == []:
                value = "none"
            elif name == "unit":
                value = "\n".join([": ".join(u) for u in element])
            elif name in ["egrav", "ggrav"]:
                value = "\n".join([u[0] + ": " + " ".join(u[1:]) for u in element])
        else:
            if element == None:
                value = "no file provided"
            else:
                value = element.filename
            args.add_field(name=name, value=value)
        args.add_field(name=name, value=value)
            
    await interaction.response.send_message(embed=args)

    # HAUS

    uhaus = ohaus.copy()
        
    class b:
        def __init__(self, haus, room, bed, seoul):
            self.haus = haus
            self.room = room
            self.bed = bed
            self.seoul = seoul
            
    def edhaus(haus, memb, bed):
        dic = haus
        dic[bed.haus][bed.room][bed.bed] = memb
        return dic 

    def pb(bed):
        if bed == "":
            return ""
        else:
            return f"{bed.haus}, {bed.room} room, {bed.bed} bed"

    # member classes + methods
    class memb:
        def __init__(self, serial, name, gravity, beds, seoul, color):
            self.serial = serial
            self.name = name
            self.beds = beds
            self.gravity = gravity
            self.seoul = seoul
            self.color = color

    def pm(memb):
        return f"{prefix}{memb.serial} {memb.name}"
           
    def p(text):
        global story
        story = story + str(text) + "\n"
        return story 

    def move(house, membs, hs, move_event=""):
        global story

        haus = house

        length = len(membs)
        if len(membs) > 1:
            tab = PrettyTable(["member", "room"])
            p("\nmoving time!")
        
        beds = []
        for h in house:
            if h in hs:
                for room in house[h]:
                    for bed in house[h][room]:
                        if move_event != "":
                            beds.append(b(h, room, bed, hs=="seoul"))
                        elif house[h][room][bed] == "":
                            beds.append(b(h, room, bed, hs=="seoul"))
                        
        for m in membs:
            found = False
            if hs == "seoul":
                for room in house["seoul"]:
                    for bed in house["seoul"][room]:
                        if house["seoul"][room][bed] == m:
                            found = True
            if found:
                continue
            try:
                if move_event != "" and m.serial == length:
                    bed = choice([bed for bed in beds if bed.haus == move_event])
                else:
                    bed = choice(beds)
            except:
                p("oops! it appears we are out of beds :(")
                return house, True
            else:
                if (move_event != "" and bed.haus == move_event) or move_event == "":
                    if move_event != "":
                        for h in house:
                            if house != "seoul":
                                for room in house[h]:
                                    for be in house[h][room]:
                                        if house[h][room][be] == m:
                                            house[h][room][be] = ""
                    haus = edhaus(house, m, bed)
                    beds.remove(bed)
                    if len(membs) > 1:
                        tab.add_row([pm(m), pb(bed)])
                    if hs == "seoul":
                        m.seoul = bed
                    else:
                        m.beds.append(bed)
                else:
                    if hs == "seoul":
                        m.seoul = bed
                    else:
                        m.beds.append(m.beds[-1])

        if len(membs) > 1:
            p(tab)
        return haus, False
    
    def perms(ls): # credits to geeksforgeeks i could not bother to do this on my own
        if len(ls) == 0:
            return []
     
        if len(ls) == 1:
            return [ls]
     
        l = []
     
        for i in range(len(ls)):
           m = ls[i]
     
           remlst = ls[:i] + ls[i+1:]
     
           # generating all permutations where m is first
           # element
           for p in perms(remlst):
               l.append([m] + p)
        return l

    async def ggravity(membs, units):
        global story
        global unitss
        global view
        
        msg = []
        votes = []
        emoji = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟", "🫶", "❤️", "😊", "✨", "🥹", "🎄", "🔥", "😂", "👍", "🫡", "🎁", "🎡", "🧀"]
        results = {u: [] for u in units}
            
        p("\ngrand gravity time!")
        tab = PrettyTable(["unit", "description"])
        unis = {}
        for x in units:
            found = False
            for y in unitss:
                if y[0] == x:
                    tab.add_row(y)
                    unis[x] = y[1]
                    found = True
                    break
            if not found:
                tab.add_row([x, "null"])
                unis[x] = "null"
        p(tab)
        if not random_ggrav:
            embed = discord.Embed(title="grand gravity time!", description="\n".join([f"{unit}: {desc}" for unit, desc in unis.items()]), color=discord.Color.magenta())
            gm = await interaction.followup.send(embed=embed)
        tab = PrettyTable(units)
        for x in range(math.ceil(len(membs)/len(units))):
            pair = sample(membs, len(units))
            for m in pair:
                membs.remove(m)
            if not random_ggrav:
                stri = discord.Embed(title=f"\nround {x+1} ({math.factorial(len(units))*5} seconds)\n", color=discord.Color.magenta())
                desc = ""
                for n in range(len(perms(pair))):
                    stri.add_field(name=f"option {emoji[n]}", value=str("\n".join([f"{units[m]}: {pm(perms(pair)[n][m])}" for m in range(len(perms(pair)[n]))])))
                stri.description = desc
                timestamp = format_timestamp(arrow.Arrow.now()+timedelta(seconds=int(math.factorial(len(units))*5)), TimestampType.RELATIVE)
                stri.description += f"\npick the number of your desired permutation.\nvoting ends {timestamp}"
                try:
                    await gm.edit(embeds=[embed, stri])
                except:
                    gm = await interaction.followup.send(embeds=[embed, stri])
                for x in range(math.factorial(len(units))):
                    try:
                        await gm.add_reaction(emoji[x])
                    except:
                        pass

                await asyncio.sleep(math.factorial(len(units))*5)
                
                cache_msg = discord.utils.get(bot.cached_messages, id=gm.id)
                votes = {e.emoji: e.count for e in cache_msg.reactions}
                
                votes = dict(sorted(votes.items(), key=lambda item: item[1]))
                pick = emoji.index(list(votes.keys())[-1])
                await gm.delete()

                try:
                    pair = perms(pair)[int(pick)]
                except:
                    pass

                for x in range(len(pair)):
                    results[units[x]].append(pair[x])

                embed.clear_fields()
                for unit, members in results.items(): 
                    embed.add_field(name=unit, value="\n".join([pm(m) for m in members]))
                
            else:
                tab.add_row([pm(m) for m in pair])
            for y in range(len(units)):
                try:
                    pair[y].gravity.append(units[y])
                except:
                    pass
        p(tab)
        
    def split(lis, count, goal):
        if count == 0:
            lis = [lis]
        if count < goal-1:
            nlis = []
            for x in lis:
                mid = int(len(x)/2)
                x = split([x[:mid], x[mid:]], count+1, goal)
                nlis.append(x)
            lis = nlis
        if count == 0:
            return lis[0]
        return lis
    
    def tree(lis):
        dic = {"final": {"rem": []}}
        rounds = []

        def todic(lis, pround, depth):
            try:
                rounds[depth]
            except:
                rounds.append(0)
            pround["rem"] = lis
            for x in pround["rem"].copy():
                if type(x) == list:
                    pround[f"round {rounds[depth]+1}"] = {"rem": x}
                    rounds[depth] += 1
                    pround["rem"].remove(x)
            for sround in pround.copy():
                if sround != "rem":
                    pround[sround] = todic(pround[sround]["rem"], pround[sround], depth+1)
                    if len(pround[sround].keys()) == 1:
                        pround[sround] = pround[sround]["rem"]
            
            return pround

        return todic(lis, dic["final"], 0)

    def depth(d): # i stole this code from someone on stackoverflow
        if isinstance(d, dict):
            return 1 + (max(map(depth, d.values())) if d else 0)
        return 0

    def name(number):
        name = ["finals", "semi-finals", "quarter-finals"]
        try:
            return name[number]
        except:
            th = 2**number
            if str(th)[-1] == 2:
                return f"{th}nd-finals"
            else:
                return f"{th}th-finals"

    def ptree(lis, rounds):
        for x in rounds.copy():
            if x == [] or x == ['']:
                rounds.remove(x)

        def sp(text, max):
            text = text
            while len(text) < max:
                text += " "
            return text

        def maxsp(str, max):
            return max - len(str.split("\n")[-1])

        songs = lis
        maxl = max([len(s) for s in songs])
        str = ""
        push = []
        for x in range(len(songs)*2-1):
            if x % 2 == 0:
                str += sp(songs[int(x/2)], maxl)
                if x % 4 == 0:
                    str += " ┐"
                else:
                    str += " ┘"
            if x % 4 == 1:
                str += maxsp(str, maxl) * " " + " ├ "
                try:
                    str += sp(rounds[0][int((x-1)/4)], maxl)
                except:
                    str += sp("?", maxl)
                if len(songs) >= 8:
                    if x % 8 == 1:
                        str += " ┐"
                        push.append(2)
                    else:
                        str += " ┘"
                        push.remove(2)
            elif 2 in push:
                str += maxsp(str, (4 + 2*maxl)) * " "
                if x % 4 == 3:
                    str += "├ "
                    try:
                        str += sp(rounds[1][int((x-3)/8)], maxl)
                    except:
                        str += sp("?", maxl)
                    if len(songs) >= 4:
                        if x % 16 == 3:
                            str += " ┐"
                            push.append(1)
                        else:
                            str += " ┘"
                            push.remove(1)
                else:
                    str += "|"
            if 1 in push and x % 16 != 3:
                str += maxsp(str, (7 + 3*maxl)) * " "
                if x % 16 == 7:
                    str += "├ "
                    try:
                        str += sp(rounds[2][int((x-7)/16)], maxl)
                    except:
                        str += sp("?", maxl)
                    if len(songs) >= 16:
                        if x % 32 == 7:
                            str += " ┐"
                            push.append(3)
                        else:
                            str += " ┘" 
                            push.remove(3)
                else:
                    str += "|"
            if 3 in push and x % 32 != 7:
                str += maxsp(str, (10 + 4*maxl)) * " "
                if x % 32 == 15:
                    str += "├ "
                    try:
                        str += sp(rounds[3][int((x-15)/32)], maxl)
                    except:
                        str += sp("?", maxl)
                else:
                    str += "|"
            if x % 8 == 7:
                pass 
            str += "\n" 
        return str

    async def rnd(dic, count, goal, r, gm, rounds, songs): 
        thing = None
        msg = None
        song = None
        cont = gm.content
        emoji = ["0️⃣", "1️⃣"]
        if count < goal and type(dic) == dict or (count == 0 and goal == 0):
            if r == 1:
                rounds.append([])
            for x in dic.copy():
                if x != "rem":
                    if count == goal-1 or (count == 0 and goal == 0):
                        if (count == 0 and goal == 0):
                            ch = dic
                        else:
                            ch = dic[x]
                        table = PrettyTable(["number", "song"])
                        table.add_row([0, ch[0]])
                        table.add_row([1, ch[1]])
                        if not random_egrav:
                            timestamp = format_timestamp(arrow.Arrow.now()+timedelta(seconds=10), TimestampType.RELATIVE)
                            msg = await interaction.followup.send(embed=discord.Embed(title=f"gravity {name(goal)}, round {r}: (10.0 seconds)", description=f"```{table}```\npick the number of your desired song.\nvoting ends {timestamp}", color=discord.Color.yellow()))
                            for n in range(2):
                                try:
                                    await msg.add_reaction(emoji[n])
                                except:
                                    pass
                            await asyncio.sleep(10)
                            cache_msg = discord.utils.get(bot.cached_messages, id=msg.id)
                            votes = {e.emoji: e.count for e in cache_msg.reactions}
                            votes = dict(sorted(votes.items(), key=lambda item: item[1]))
                            chosen = ch[emoji.index(list(votes.keys())[-1])]
                            await msg.delete()
                        else:
                            chosen = choice(ch)
                        rounds[-1].append(chosen)
                        await gm.edit(content = f"event gravity time!\n```{ptree(songs, rounds)}```")
                        if count == 0 and goal == 0:
                            p(f"{chosen} has been picked as the title song for your group!")
                            song = chosen
                        else:
                            p(f"{chosen} has been picked.\n")
                            song = ""
                        if not (count == 0 and goal == 0):
                            dic["rem"].append(chosen)
                            del dic[x]
                            thing = dic["rem"]
                            if len(dic.keys()) == 1:
                                dic = dic["rem"]
                        return dic, thing, msg, song, cont, rounds
                    else:
                        if type(dic[x]) == dict and list(dic[x].keys()) != ["rem"]:
                            dic[x], thing, msg, song, cont, rounds = await rnd(dic[x], count+1, goal, r, gm, rounds, songs)
                            if thing:
                                break
        return dic, thing, msg, song, cont, rounds

    async def egravity(songs):
        p("\nevent gravity time!")
        gm = await interaction.followup.send(embed=discord.Embed(title=f"event gravity time!", description=f"```{ptree(songs, [])}```", color=discord.Color.yellow()))
        tr = tree(split(songs, 0, math.log(len(songs), 2)))
        d = int(math.log(len(songs), 2)) 
        rounds = []
        for x in range(d, -1, -1):
            count = 0
            while 1:
                count += 1
                tr, thing, msg, song, cont, rounds = await rnd(tr, 0, x, count, gm, rounds, songs)
                if not thing:
                    break
        await gm.edit(content=f"event gravity time!\n```{ptree(songs, rounds)}```\n{song} has been chosen as the title track.")
        p(f"event gravity time!\n```{ptree(songs, rounds)}```\n{song} has been chosen as the title track.")

    def phaus(haus, seoul=False, final=False):
        global story

        if seoul:
            str = f"\nHAUS update: (seoul)"
        else:
            str = f"\nHAUS update:"
        if final:
            p(str.replace("HAUS update", "final HAUS"))
        else:
            p(str)
        tab = PrettyTable(["room", "members"])
        for h in haus:
            if (h=="seoul") == seoul:
                for room in haus[h]:
                    row = [f"{h}, {room} room", ""]
                    for bed in haus[h][room]:
                        try:
                            row[-1] += pm(haus[h][room][bed]) + ", "
                        except:
                            pass
                    row[-1] = row[-1][:-2]
                    tab.add_row(row)
        p(tab)

    def full(uhaus, hs):
        full = True
        for haus in uhaus:
            if haus in hs:
                for room in uhaus[haus]:
                    for bed in uhaus[haus][room]:
                        if uhaus[haus][room][bed] == "":
                            full = False

        return full

    def cbeds(uhaus, hs):
        count = 0
        for haus in uhaus:
            if haus in hs:
                for room in uhaus[haus]:
                    for bed in uhaus[haus][room]:
                        count += 1
        
        return count

    async def event(haus, omembers, number, hs, events, gravities, mmoves, tab, wave):
        global story
        brk = False
        
        if number == cbeds(uhaus, hs[:-1]) + 1 and len(hs) > 1:
            events = [["mmove"]] + events

        if len(events) == 0:
            haus, brk = move(haus, [omembers[-1]], hs)
            try:
                bed = pb(omembers[-1].beds[-1])
            except:
                bed = ""
            tab.add_row([pm(omembers[-1]), omembers[-1].color, bed])
        
        moved = False

        for e in events: 
            match e[0]:
                case "mmove":
                    mmoves += 1
                    tab.add_row([pm(omembers[-1]), omembers[-1].color, "TBC"])
                    wave += 1
                    p(f"new wave of {prefix}!")
                    p(f"wave {str(wave)}:")
                    p(tab)
                    tab = PrettyTable(["member", "color", "bed"])
                    moved = True
                    haus, brk= move(haus, omembers, hs, hs[-1])
                    phaus(haus)
                    p("\n")
                case "ggravity" | "egravity":
                    gravities += 1
                    haus, brk = move(haus, [omembers[-1]], hs)
                    if not moved:
                        tab.add_row([pm(omembers[-1]), omembers[-1].color, pb(omembers[-1].beds[-1])])
                        wave += 1
                        p(f"new wave of {prefix}!")
                        p(f"wave {str(wave)}:")
                        p(tab)
                        tab = PrettyTable(["member", "color", "bed"])
                    phaus(haus)
                    if e[0] == "ggravity":
                        await ggravity(omembers, e[1])
                    else:
                        await egravity(e[1])
                    haus, brk = move(haus, omembers, "seoul")
                    phaus(haus, True)
                    p("\n")
                case "end":
                    p(f"new wave of {prefix}!")
                    p(f"wave {str(wave)}:")
                    p(tab)
                    tab = PrettyTable(["member", "color", "bed"])
                    phaus(haus)
                    p("\n") 
        
        if full(ohaus, "seoul") and len(events) > 0:
            p(f"the seoul HAUS is full.\n")

        return haus, gravities, mmoves, tab, wave, brk

    def summary(omembers):
        global story

        p("")
        maxg = 0
        maxm = 0
        
        for memb in omembers:
            if len(memb.gravity) > maxg:
                maxg = len(memb.gravity)
            if len(memb.beds) > maxm:
                maxm = len(memb.beds)

        for memb in omembers:
            while len(memb.gravity) < maxg:
                memb.gravity = [""] + memb.gravity
            while len(memb.beds) < maxm:
                memb.beds = [""] + memb.beds

        gs = []
        bs = []

        for x in range(maxg):
            gs.append(f"unit {x+1}")
        for x in range(maxm):
            bs += [f"haus {x+1}", f"room {x+1}", f"bed {x+1}"]

        tab = PrettyTable(["name", "serial", "color"] + gs + bs + ["seoul room", "seoul bed"])
        
        for m in omembers:
            beds = []
            for bed in m.beds:
                if bed != "":
                    beds += [bed.haus, bed.room, bed.bed]
                else:
                    beds += ["", "", ""]
            try:
                seoul = [m.seoul.room, m.seoul.bed]
            except:
                seoul = ["", ""]
            row = [m.name, prefix + str(m.serial), m.color] + m.gravity + beds + seoul
            tab.add_row(row)
            
        p(tab)

    # main code
    voted = requests.get(f"https://top.gg/api/bots/1041703388057960479/check?userId={interaction.user.id}", headers={"Authorization": topg}).json()["voted"]
    print(voted)
    owners = requests.get(f"https://top.gg/api/bots/1041703388057960479/", headers={"Authorization": topg}).json()["owners"] 
    cowner = str(interaction.user.id) in owners
    if not (voted or cowner) and (not random_ggrav or not random_egrav):
        await interaction.followup.send("to use voted/manual gravity, please vote at https://top.gg/bot/1041703388057960479/vote/.")
        return
    else:
        omembers = []
        gravities = 0
        mmoves = 1
        wave = 0
        tab = PrettyTable(["member", "color", "bed"])
        count = len(members)

        for x in range(len(members)):
            events = []

            # add member to database
            if random_members:
                nmemb = choice(members)
            else:
                nmemb = members[0]
            new = memb(x+1, nmemb, [], [], "", "")
            omembers.append(new)
            members.remove(nmemb)

            # reveal new member
            def genhex():
                n = hex(randint(0,255))[2:]
                if len(n) == 1:
                    return "0" + n
                return n
            hexc = "#" + genhex() + genhex() + genhex()
            omembers[-1].color = hexc
                    
            # moving
            hauses = list(dict.keys(ohaus))
            hauses.remove("seoul")
            for y in range(len(hauses)):
                if x+1 <= cbeds(uhaus, hauses[:y+1]):
                    hs = hauses[:y+1]
                    break

            for grav in ggravs:
                if x+1 == int(grav[0]):
                    events.append(["ggravity", grav[1:]])

            for grav in egravs:
                if x+1 == int(grav[0]):
                    events.append(["egravity", grav[1:]])

            if x == count-1:
                events.append(["end"])
            
            om = omembers.copy()

            uhaus, gravities, mmoves, tab, wave, test = await event(uhaus, om, x+1, hs, events, gravities, mmoves, tab, wave)
            if test:
                break

            
        p("to be continued...")
        phaus(uhaus, False, True)
        phaus(uhaus, True, True)

        # summary table
        summary(omembers)

        as_bytes = map(str.encode, story)
        content = b"".join(as_bytes)
        await interaction.followup.send("your simulation:", file=discord.File(BytesIO(content), "simulated.txt"))
        
@bot.event
async def on_ready():
    print(f'{bot.user} is online.')
    print(f'in {len(bot.guilds)} servers')
    for x in bot.guilds:
        print(f'connected to {x.name}')
    print()
    await bot.setup_hook()

# load stuff
@bot.event
async def on_ready():
    print(f'{bot.user} is online.')
    print(f'in {len(bot.guilds)} servers')
    for x in bot.guilds:
        print(f'connected to {x.name}')
    print()
    await bot.setup_hook()
            
bot.run(TOKEN)
