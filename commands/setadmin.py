import embedtemplates
import permissions


async def Main(self, message, command, arguments):
    if arguments == 0 or arguments == "" or arguments == None or arguments == command:
        await message.channel.send(content="", embed=embedtemplates.help(
            "Sets the admin role of the server."))
        return

    settings = self.database.get_settings(message.guild.id)
    if settings["AdminRole"] != 0:
        if not await permissions.is_guild_admin(self, message.guild.id, message.author.id):
            await message.channel.send(content="", embed=embedtemplates.failure("Permission Denied",
                                                                                "User does not have permission to use this!"))
            return
    if len(message.role_mentions) != 1:
        await message.channel.send(content="", embed=embedtemplates.failure("Incorrect Argument Count", "Please mention the role you want to set."))
        return

    settings["AdminRole"] = message.role_mentions[0].id
    self.database.set_settings(message.guild.id, settings)
    await message.channel.send(content="", embed=embedtemplates.success("Admin Role Set!", "A new Admin role has been set for the server!"))