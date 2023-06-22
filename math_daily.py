import asyncio
import json
import os

import discord
from discord.ext import tasks, commands
import datetime
from dotenv import load_dotenv

load_dotenv()


class MathChecker(commands.Bot):
    REPORTS = {}
    
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.week_sum = 0
        self.reactions = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣',
                         '7️⃣']
        today = datetime.datetime.now()
        self.week_day = today.weekday()
        self.week_number = today.isocalendar()[1]
        self.user_id = int(os.getenv('USER_ID'))
        self.thread_id = int(os.getenv('THREAD_ID'))

    async def on_ready(self):
        print('Logged in as {0.user}'.format(self))
        self.daily_survey.start()

    @tasks.loop(hours=24)
    async def daily_survey(self):
        def check_report():
            today = datetime.datetime.now()
            self.week_day = today.weekday()
            self.week_number = today.isocalendar()[1]

            if self.week_day == 0:  # Monday is represented by 0
                self.REPORTS[self.week_number-1]["sum"] = self.week_sum
                self.week_sum = 0
            if self.week_number not in self.REPORTS:
                self.REPORTS[self.week_number] = {}
            self.REPORTS[self.week_number][self.week_day] = 0
        check_report()
        channel = self.get_channel(self.thread_id)
        message = f"""<@{self.user_id}>     
        \n 0️⃣ - nic, a nic... :pleading_face:                                      
        \n 1️⃣ - 0.5 godzinki: lepszy rydz niż nic? :sweat_smile:                
        \n 2️⃣ - 1 godzinkę: half way.                             
        \n 3️⃣ - 1.5 godzinki: prawie, prawie :sweat_smile:                     
        \n 4️⃣ - 2 godzinki: yuuupie!                              
        \n 5️⃣ - 2.5 godzinki: wymiatam 😄                         
        \n 6️⃣ - 3 godzinki: ale flow! :exploding_head:                              
        \n 7️⃣ - więcej niż 3 godzinki: upsik, trochę mnie poniosło 😃"""
        poll = discord.Embed(
            title=f"Jak długo uczyłaś się dzisiaj matematyki?",
            description=message,
            color=0x00FF00)
        sent_message = await channel.send(embed=poll)
        for emoji in self.reactions:
            await sent_message.add_reaction(emoji)

        # Wait for a reaction event within a timeframe
        try:
            await self.wait_for(
                'reaction_add',
                check=lambda r, u: u.id == self.user_id,
                timeout=14 * 3600)

        except asyncio.TimeoutError:
            # No reaction was added within the timeframe
            await channel.send(f"<@{self.user_id}> Pamiętaj, żeby wprowadzić "
                               f"odpowiedź na pytanie :)")
        with open('reports.json', 'w') as f:
            json.dump(self.REPORTS, f, indent=4)
    
    async def on_raw_reaction_add(self, payload):
        if payload.user_id != self.user_id:
            return

        old_sum = self.week_sum
        channel = self.get_channel(payload.channel_id)
        if channel.id == self.thread_id:
            if payload.emoji.name in self.reactions:
                if payload.emoji == self.reactions[0]:  # 0️⃣
                    self.week_sum += 0
                    await channel.send("Odpowiedziałaś 0. No, no, no...")
                elif payload.emoji.name == self.reactions[1]:  # 1️⃣
                    self.week_sum += 0.5
                    await channel.send(
                        f"Odpowiedziałeś 0.5 godzinki. No... to zawsze coś :)")
                elif payload.emoji.name == self.reactions[2]:  # 2️⃣
                    self.week_sum += 1
                    await channel.send(
                        f"Odpowiedziałeś Godzinkę. Półmetek, półmetek. Może "
                        f"jutro znajdzie się więcej czasu 💙")
                elif payload.emoji.name == self.reactions[3]:  # 3️⃣
                    self.week_sum += 1.5
                    await channel.send(
                        f"Odpowiedziałeś Godzinkę i pół. Nieźle :) Już prawie u "
                        f"celu!")
                elif payload.emoji.name == self.reactions[4]:  # 4️⃣
                    self.week_sum += 2
                    await channel.send(f"Odpowiedziałeś 2 godzinki. Wow! Co za "
                                       f"wojownik! Jestem dumna :) 💙")
                elif payload.emoji.name == self.reactions[5]:  # 5️⃣
                    self.week_sum += 2.5
                    await channel.send(
                        f"Odpowiedziałeś 2 i pół godzinki. Wow! Ktoś tu "
                        f"miał super zapał! Super :)💙")
                elif payload.emoji.name == self.reactions[6]:  # 6️⃣
                    self.week_sum += 3
                    await channel.send(
                        f"Odpowiedziałeś 3 godzinki. Wow! Uważaj, matematyka "
                        f"wciąga! Super! To musiało być niezłe wyzwanie :)")
                elif payload.emoji.name == self.reactions[7]:  # 7️⃣
                    self.week_sum += 3.5
                    await channel.send(
                        f"Odpowiedziałeś więcej niż 3 godzinki. No niezłe masz "
                        f"tempo! Despacito, seniorita. Czasami wolniej znacyz "
                        f"lepiej :)")
                diff = self.week_sum - old_sum
                if diff > 0:
                    self.REPORTS[self.week_number][self.week_day] += diff
                await self.sum_week(channel)

    async def on_raw_reaction_remove(self, payload):
        if payload.user_id != self.user_id:
            return

        channel = self.get_channel(payload.channel_id)
        if channel.id == self.thread_id:
            if payload.emoji.name in self.reactions:
                if payload.emoji.name == self.reactions[0]:  # 0️⃣
                    self.week_sum -= 0
                elif payload.emoji.name == self.reactions[1]:  # 1️⃣
                    self.week_sum -= 0.5
                elif payload.emoji.name == self.reactions[2]:  # 2️⃣
                    self.week_sum -= 1
                elif payload.emoji.name == self.reactions[3]:  # 3️⃣
                    self.week_sum -= 1.5
                elif payload.emoji.name == self.reactions[4]:  # 4️⃣
                    self.week_sum -= 2
                elif payload.emoji.name == self.reactions[5]:  # 5️⃣
                    self.week_sum -= 2.5
                elif payload.emoji.name == self.reactions[6]:  # 6️⃣
                    self.week_sum -= 3
                elif payload.emoji.name == self.reactions[7]:  # 7️⃣
                    self.week_sum -= 3.5
                await self.sum_week(channel)

    async def sum_week(self, channel):
        if self.week_sum < 10:
            message = f"W tym tygodniu uczyłaś się matematyki przez " \
                      f"{self.week_sum} godizn. Jeszcze" \
                      f" {10 - self.week_sum} to " \
                      f"go! Dasz radę, wierzę w Ciebie! 💙"
        else:
            message = f"Wow! Już {self.week_sum} godzin za tobą! " \
                      f"Gratulacje! 💙 Reszta tygodnia jest twoja!"
        await channel.send(message)

    @commands.command()
    async def report(self, ctx):
        poll = discord.Embed(title="Podsumowanie wszystkich tygodni:",
                             description=self.REPORTS,
                             color=0x00FF00)
        await ctx.send(embed=poll)


intents = discord.Intents.default()
intents.typing = False
intents.presences = False

math_bot = MathChecker(command_prefix='!', intents=intents)
print(os.environ.get("TOKEN"))
math_bot.run(os.getenv('TOKEN'))
