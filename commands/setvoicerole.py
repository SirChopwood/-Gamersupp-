import embedtemplates
import permissions
import discord


async def Main(self, message, command, arguments):
    if arguments == 0 or arguments == "" or arguments == None or arguments == command:
        await message.channel.send(content="", embed=embedtemplates.help(
            "Changes the Discord Role that you get when joining Voice Chat channels."))
        return
    if not await permissions.is_guild_admin(self, message.guild.id, message.author.id):
        await message.channel.send(content="", embed=embedtemplates.failure("Permission Denied",
                                                                            "User does not have permission to use this!"))
        return
    settings = self.database.get_settings(message.guild.id)

    if message.content.endswith("0"):
        settings["VoiceChatRole"] = 0
    else:
        try:
            settings["VoiceChatRole"] = int(message.role_mentions[0].id)
        except AttributeError:
            await message.channel.send(content="", embed=embedtemplates.failure("Invalid Argument",
                                                                                "Please mention (ping) the role you want attached to this Section or type '0' for none!"))
            return

    self.database.set_settings(message.guild.id, settings)
    await message.channel.send(content="", embed=embedtemplates.success("Settings Edited", str("Voice Chat RoleID changed to ``" + str(settings["VoiceChatRole"]) + "``.")))
    try:
        await message.delete()
    except discord.Forbidden:
        return
