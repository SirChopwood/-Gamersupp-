import discord
import importlib
import os
import importlib.util
import sys
import traceback
import asyncio
import embedtemplates
import background_tasks
import permissions
import mongodatabase
import json


class DiscordBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.database = mongodatabase.Main()

    async def run_file(self, filename, message="", arguments=""):
        command_found = False
        for command_file in os.listdir("commands"):
            if command_file in ["__init__.py", "__pycache__"]:
                continue
            elif command_file[:-3] == filename:
                spec = importlib.util.spec_from_file_location("module.name", str("commands/" + command_file))
                foo = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(foo)
                await foo.Main(self, message, filename, arguments)
                command_found = True
        if not command_found:
            await message.channel.send("Command not found!")

    async def await_response(self, user):
        def check(message):
            return message.author == user
        try:
            content = await client.wait_for('message', check=check, timeout=100)
        except asyncio.TimeoutError:
            return None
        return content

    async def on_ready(self):
        print('===| Logged In as {0.user} |==='.format(self))
        activity = discord.Activity(name='for lore!', type=discord.ActivityType.watching)
        await self.change_presence(activity=activity)
        self.loop.create_task(await background_tasks.Main(self))

    async def on_error(self, event, *args, **kwargs):
        type, value, tb = sys.exc_info()
        if event == "on_message":
            try:
                channel = " in #" + args[0].channel.name
            except AttributeError:
                channel = " in private DMs"
            await args[0].channel.send(
                "*An error occured, sorry for the inconvenience. Ramiris has been notified of the error.*")
        else:
            channel = ""
        tbs = "*" + type.__name__ + " exception handled in " + event + channel + " : " + str(
            value) + "*\n\n```\n"
        for string in traceback.format_tb(tb):
            tbs = tbs + string
        tbs = tbs + "```"
        print(tbs)
        await self.get_user(110838934644211712).send(tbs)

    async def on_message(self, message):
        if message.author.bot or message.channel.type == discord.ChannelType.private or message.channel.type == discord.ChannelType.group:
            return

        for module_file in os.listdir("modules"):
            if module_file in ["__init__.py", "__pycache__"]:
                continue
            else:
                spec = importlib.util.spec_from_file_location("module.name", str("modules/" + module_file))
                foo = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(foo)
                await foo.Main(self, message)

        if message.content.startswith(">"):
            command = message.content[1:].split(" ")[0]
            arguments = message.content[1:].replace(str(command+" "), "")
            await self.run_file(command, message, arguments)

    async def question(self, user, question, channel=None):  # Ask the user a question, specify a channel or it'll DM
        if channel is not None:
            await channel.send(content="", embed=embedtemplates.question(question, user.display_name))
            response = await self.await_response(user)
            if response is None:
                await channel.send(content="", embed=embedtemplates.failure("Response Timed Out",
                                                                         "You took too long to respond!"))
                return None
            return response
        else:
            try:
                await user.send(content="", embed=embedtemplates.question(question, user.display_name))
                response = await self.await_response(user)
                if response is None:
                    await user.send(content="", embed=embedtemplates.failure("Response Timed Out",
                                                                             "You took too long to respond!"))
                    return None
                return response
            except discord.Forbidden:
                print(user.name, "Could not be messaged.")
                return None

    async def on_voice_state_update(self, member, before, after):
        settings = self.database.get_settings(member.guild.id)
        if settings["VoiceChatRole"] == 0:
            return
        if before.channel is None:
            print("Joined a Voice Channel!")
            role = member.guild.get_role(settings["VoiceChatRole"])
            try:
                await member.add_roles(role)
            except discord.Forbidden:
                print("Do not have permissions to assign roles to:", member.display_name)
                return
        elif after.channel is None:
            print("Left a Voice Channel!")
            role = member.guild.get_role(settings["VoiceChatRole"])
            try:
                await member.remove_roles(role)
            except discord.Forbidden:
                print("Do not have permissions to assign roles to:", member.display_name)
                return
        else:
            print("Changed Voice Channels!")

    async def on_guild_join(self, guild):
        with open("json_files/server_settings.json", "r") as file:
            settingstemplate = json.load(file)
        self.database.add_settings(guild.id, settingstemplate)


if __name__ == '__main__':  # https://discord.com/oauth2/authorize?client_id=822317759323963423&scope=bot&permissions=8
    print("Bot Starting...")
    intents = discord.Intents.default()
    intents.members = True
    intents.voice_states = True
    client = DiscordBot(intents=intents)
    with open("token.txt", "r") as file:
        token = file.readlines()
    client.run(token[0])
