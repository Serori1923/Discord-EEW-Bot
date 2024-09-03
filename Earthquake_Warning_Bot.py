import os
import time
import discord
from discord.utils import get
import asyncio
import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.ERROR)

gw_logger = logging.getLogger('discord.gateway')
gw_logger.setLevel(logging.ERROR)

client_logger = logging.getLogger('discord.client')
client_logger.setLevel(logging.ERROR)

class GatewayEventFilter(logging.Filter):
    def __init__(self) -> None:
        super().__init__('discord.client')

    def filter(self, record: logging.LogRecord) -> bool:
        if record.exc_info is not None and isinstance(record.exc_info[1], discord.ConnectionClosed):
            return False
        return True
    
logging.getLogger('discord.client').addFilter(GatewayEventFilter())


#設定檔
TOKEN= "Your Token Here"
intents = discord.Intents().all()
client = discord.Client(intents=intents)
last_trigger_time = time.time()
whilesec = 0
intensity = ""
sec = ""
new = False
tooLow = False
tooStrong = False
AlarnNo = 0
alarn = discord.Embed(title="地震警報!" , color=0xffd700)
nowtime = ""
channelID = #Put the channel ID where you want to send the alarm message here (type:int)

async def sendWarning():
    global whilesec, new, alarn, nowtime
    channel = client.get_channel(channelID)
    if(new):
        nowtime=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        print(f"{nowtime} | 地震警報觸發!")
        new = False
        embed=discord.Embed(title="地震警報!" , color=0xffd700)
        embed.add_field(name=f"【**緊急地震速報**】現在發生有感地震 預估震度{intensity}，{whilesec}秒後抵達",value="\u200b", inline=False)
        if(tooLow):
            embed.add_field(name=f"氣象局預警修正，預估震度修正後未達標準，請忽略以上警報",value="\u200b", inline=False)
        if(tooStrong):
            embed.add_field(name=f"強烈地震，⚠️注意掉落物，立即避難⚠️",value="\u200b", inline=False)
        embed.set_footer(text=f"{nowtime} 預警第{AlarnNo}報")
        await channel.send("@everyone")
        alarn=await channel.send(embed=embed)

    else:
        await asyncio.sleep(0.73) #因Discord延遲而未將暫停秒數設定為1秒，請依照實際運行狀況調整此秒數
        whilesec-=1
        if(whilesec < 0):
            whilesec = 0
        new_embed=discord.Embed(title="地震警報!" , color=0xffd700)
        new_embed.add_field(name=f"【**緊急地震速報**】現在發生有感地震 預估震度{intensity}，{whilesec}秒後抵達",value="\u200b", inline=False)
        if(tooLow):
            new_embed.add_field(name=f"氣象局預警修正，預估震度修正後未達標準，請忽略以上警報",value="\u200b", inline=False)
        if(tooStrong):
            new_embed.add_field(name=f"強烈地震，⚠️注意掉落物，立即避難⚠️",value="\u200b", inline=False)
        new_embed.set_footer(text=f"{nowtime} 預警第{AlarnNo}報")
        await alarn.edit(embed=new_embed)

async def monitor_file(file_path):
    await client.wait_until_ready()
    global whilesec, sec, tooLow, tooStrong, intensity, new, AlarnNo, nowtime

    last_modified_time = os.path.getmtime(file_path)
    while not client.is_closed():
        await asyncio.sleep(0.3)
        modified_time = os.path.getmtime(file_path)
        if modified_time != last_modified_time:
            if((modified_time - last_modified_time) > 30):
                new = True
                AlarnNo = 1

            last_modified_time = modified_time

            f = open('file_path')
            text = []
            for line in f:
                text = line.split(" ")
            f.close
            
            intensity = text[0]
            sec = int(text[1])-2
            whilesec = int(sec)

            while True:
                modified_time = os.path.getmtime(file_path)
                if modified_time != last_modified_time:
                    nowtime=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    AlarnNo += 1
                    last_modified_time = modified_time
                    f = open('file_path')
                    text = []
                    for line in f:
                        text = line.split(" ")
                    f.close
                    intensity = text[0]
                    sec = int(text[1])-2
                    whilesec = int(sec)

                match intensity:
                    case "0":
                        intensity = "0級"
                        tooLow = True
                        tooStrong = False
                    case "1":
                        intensity = "1級"
                        tooLow = True
                        tooStrong = False
                    case "2":
                        intensity = "2級"
                        tooLow = True
                        tooStrong = False
                    case "3":
                        intensity = "3級"
                        tooLow = False
                        tooStrong = False
                    case "4":
                        intensity = "4級"
                        tooLow = False
                        tooStrong = False
                    case "5-":
                        intensity = "5弱"
                        tooStrong = True
                        tooLow = False
                    case "5+":
                        intensity = "5強"
                        tooStrong = True
                        tooLow = False
                    case "6-":
                        intensity = "6弱"
                        tooStrong = True
                        tooLow = False
                    case "6+":
                        intensity = "6強"
                        tooStrong = True
                        tooLow = False
                    case "7":
                        intensity = "7級"
                        tooStrong = True
                        tooLow = False
                    case _: 
                        pass
                    
                await sendWarning()

                if(whilesec == 0):
                    break

@client.event
async def on_ready():
    print("\n機器人已上線，請勿關閉本程式\n")
    print(f"預警資訊將發送至 [{client.get_channel(channelID).name}]")
    print("-----------------------------------")
    client.loop.create_task(monitor_file('./EqData.txt'))

client.run(TOKEN)
