async def is_guild_admin(self, guildid, userid):
    settings = self.database.get_settings(guildid)
    guild = await self.fetch_guild(guildid)
    user = await guild.fetch_member(userid)
    for role in user.roles:
        if role.id == settings["AdminRole"]:
            return True
    return False
