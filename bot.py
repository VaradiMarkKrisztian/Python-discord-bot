import discord
import random
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from discord.ext import commands


def run_discord_bot():
    with open("token.txt") as f:
        token = f.readline()
    bot = commands.Bot(command_prefix=">", intents=discord.Intents.all())

    @bot.event
    async def on_ready():
        print(f'{bot.user} is now running')

    @bot.command(aliases=['osu'])
    async def send_embedded_osu_username(ctx, username=""):
        # 3 testcases
        # 1st IF statement checks if the username is empty
        # 2nd IF statement checks if the Username contains more than 15 characters
        # the TRY block checks if the Username opens a "User not found" page where the CSS_Selector element can be found
        # Finally it will resume the search for the existing username
        if not username:
            await ctx.send("`No username was given`")
        elif len(username) > 15:
            await ctx.send("`Username input too long`")
        else:
            print("this is the new ", username)
            service = Service(r"c:/webdrivers/geckodriver.exe")
            driver = webdriver.Firefox(service=service)
            driver.get(f"https://osu.ppy.sh/users/{username}/osu")
            try:
                if bool(driver.find_element(By.CLASS_NAME, "osu-page--generic").size) > 0:
                    driver.quit()
                    await ctx.send("`User not found`")
            finally:
                "why wont it enter in ELSE ?"
                # format description with the stats
                stat_name = driver.find_elements(By.CLASS_NAME, "profile-stats__key")
                stat_score = driver.find_elements(By.CLASS_NAME, "profile-stats__value")
                person_name = driver.find_element(By.CLASS_NAME, "u-ellipsis-pre-overflow")
                description_text = ""
                for name in range(len(stat_name)):
                    description_text = description_text + f'▸ **{stat_name[name].text}:** {stat_score[name].text}\n'

                # format profile picture from site
                image_url = driver.find_element(By.XPATH,
                                                "/html/body/div[8]/div/div/div/div[2]/div[1]/div[1]/div[2]/div[1]/span"
                                                ).value_of_css_property("background-image").split('"')[1]
                print("image url is ", image_url)
                # 1.find the element at the location of the copied the XPath from HTML Inspect on the site
                # 2.target the style CSS element with value_of_css_property
                # 3.obtain the URL by splitting the string generating a list of elements
                # 4 assign the URL string to the variable located at index 1 in the list

                # get active/inactive status
                active_status = driver.find_element(By.CSS_SELECTOR,
                                                    'div.profile-links__row:nth-child(1) > div:nth-child(2)')

                # generate the embed with the gathered values
                embed = discord.Embed(title=f"{person_name.text}", url=f"https://osu.ppy.sh/users/{username}/osu",
                                      colour=discord.Colour.blue(), description=description_text)
                embed.set_thumbnail(url=image_url)
                embed.set_footer(text=active_status.text)

                # other ways to show the stats
                # for name in range(len(stat_name)):
                #       embed.add_field(name=stat_name[name].text, value=stat_score[name].text, inline=False)

                # un formatted description, doesn't work well in FOR loop
                # embed.description(f'**{stat_name[name].text}: ** {stat_score[name].text}\n')
                driver.quit()
                await ctx.send(embed=embed)

    @bot.event
    async def on_member_join(member):
        channel = member.guild.system_channel
        await channel.send(f"{member.mention} Welcome")

    @bot.event
    async def on_member_remove(member):
        channel = member.guild.system_channel
        await channel.send(f"Bye {member.mention}")

    @bot.command()
    async def ping(ctx):
        await ctx.reply(f"Pong! {round(bot.latency * 1000)}ms")

    @bot.command(aliases=['8ball', 'test'])
    # * saves the entire message after ctx space into a list
    # omitting the * before a  variable will result for that variable to take in only the first word given like in the
    # send_embed function from above
    async def eightball(ctx, *, question):
        responses = ["yes", "no", "maybe", "maybe yes", "maybe no", "unsure", "probably"]
        await ctx.send(f"**Question: ** {question}\n **Answers: ** {random.choice(responses)}")

    @bot.command()
    async def command_list(ctx):
        await ctx.send(f"`>ping returns the bot latency ms\n"
                       f">8ball 'question' and >test 'question' return a random answer to the question\n"
                       f">osu 'username' returns an embedded answer with the stats of the user if found\n"
                       f">command_list gives an explanation of every command and its use`")

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return
        if message.content == "hi":
            await message.channel.send("yo")

        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)
        print(f'{username} said: {user_message} in ({channel})')
        await bot.process_commands(message)

    bot.run(token)
