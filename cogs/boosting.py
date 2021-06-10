import discord
from discord.ext import commands
import re

class Boosting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.category = "Boosting"

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Boosting Loaded")

    @commands.command(help="Configure the boosting feature for your guild, and welcome new booster in a good way!\nThe message you set, if you have embed enabled, will be automatically placed as embed description.\n"
                            "`ami setboost preview` to see the preview of the message\n"
                            "`ami setboost settings` to check the boosting module setting for the guild\n"
                            "`ami setboost enable / disable` to enable / disable the boosting module\n"
                            "`ami setboost embed enable / disable` to enable / disable the embed for the message\n"
                            "`ami setboost message [set]` to set the message to send on new boosts\n"
                            "`ami setboost channel [set]` to set the channel where send the message (you can mention it or use the ID)\n"
                            "`ami setboost embed-title [set]` to set the title of the embed\n"
                            "`ami setboost embed-image` to set the image to use in the embed\n"
                            "`ami setboost embed-footer` to set the footer of the embed\n\n"
                            "**You can also use some variables in the boosting message:**```py\n{name} : return the member name\n{member} : return the complete member name\n{mention} : return the member mention\n{boosts} : return the boosts of the guild\n{guild_level} : return the level of the guild\n```")
    @commands.has_permissions(manage_guild=True)
    async def setboost(self, ctx, option, *, set=None):

        if option.lower() == "disable":
            await self.bot.pg_con.execute("INSERT INTO boosting (guild_id, toggle) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET toggle = $2", ctx.guild.id, False)
            return await ctx.send("<:4430checkmark:848857812632076314> Boosting module disabled!")

        if option.lower() == "enable":
            await self.bot.pg_con.execute("INSERT INTO boosting (guild_id, toggle) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET toggle = $2", ctx.guild.id, True)
            return await ctx.send("<:4430checkmark:848857812632076314> Boosting module enabled!")


        valid = ["settings", "preview", "embed", "embed-image", "embed-title", "embed-footer", "message", "channel"]
        if option.lower() not in valid:
            return await ctx.send("<:4318crossmark:848857812565229601> This option is not valid, check `ami help setboost` for more info's.")

        if option.lower() == "settings":
            db = await self.bot.pg_con.fetch("SELECT * FROM boosting WHERE guild_id = $1", ctx.guild.id)
            if not db:
                return await ctx.send("<:4318crossmark:848857812565229601> This guild has no boosting module configuration yet.")

            mex = db[0]["message"]
            chan = db[0]["channel_id"]
            foot = db[0]["embed_footer"]
            tit = db[0]["embed_title"]
            im = db[0]["embed_image"]
            emb = db[0]["embed"]
            tgf = db[0]["toggle"]

            dcf = ""

            if tgf is True:
                dcf = "Enabled"
                
            elif not tgf:
                dcf = "Disabled"

            s1 = "Message: None"
            s2 = "Channel: None"
            s3 = "Embed Footer: None"
            s4 = "Embed Title: None"
            s5 = "Embed Image: None"
            s6 = ""

            if mex:
                s1 = f"Message: {mex}"
            if chan:
                s2 = f"Channel: <#{chan}>"
            if foot:
                s3 = f"Embed Footer: {foot}"
            if tit:
                s4 = f"Embed Title: {tit}"
            if im:
                s5 = f"Embed Image: {im}"
            if emb:
                if emb is True:
                    s6 = f"Embed: **Enabled**"
                elif emb is False:
                    s6 = f"Embed: **Disabled**"

            em = discord.Embed(title="Boosting Panel", description=f"Boosting feature in this guild is **{dcf}**", color=0xffcff1)
            em.add_field(name=f"{ctx.guild.name} settings", value=f"{s1}\n\n{s2}")
            em.add_field(name="Embed Settings", value=f"{s3}\n{s4}\n{s5}\n{s6}")
            em.set_thumbnail(url=ctx.guild.icon_url)
            return await ctx.send(embed=em)

        if option.lower() == "preview":
            db = await self.bot.pg_con.fetch("SELECT * FROM boosting WHERE guild_id = $1", ctx.guild.id)
            if not db:
                return await ctx.send("<:4318crossmark:848857812565229601> This guild has no boosting module configuration yet.")

            mex = db[0]["message"]
            chan = db[0]["channel_id"]
            foot = db[0]["embed_footer"]
            tit = db[0]["embed_title"]
            im = db[0]["embed_image"]
            emb = db[0]["embed"]
                
            namespace = {"{name}": ctx.author.name, 
            "{member}": f"{ctx.author.name}#{ctx.author.discriminator}",
            "{mention}": ctx.author.mention,
            "{boosts}": ctx.guild.premium_subscription_count,
            "{guild_level}": ctx.guild.premium_tier}

            def replace_all(m: str) -> str:
                for k in namespace.keys():
                    m = m.replace(k, str(namespace[k]))
                return m

            msg = replace_all(mex)

            if emb is False or not emb:
                if not mex:
                    return await ctx.send("<:4318crossmark:848857812565229601> This guild has no boosting message set.")
                return await ctx.send(msg)
            
            elif emb is True:
                em = discord.Embed(description = msg, color=0xffcff1)
                if tit:
                    namespace = {"{name}": ctx.author.name, 
                    "{member}": f"{ctx.author.name}#{ctx.author.discriminator}",
                    "{mention}": ctx.author.mention,
                    "{boosts}": ctx.guild.premium_subscription_count,
                    "{guild_level}": ctx.guild.premium_tier}

                    def replace_all(m: str) -> str:
                        for k in namespace.keys():
                            m = m.replace(k, str(namespace[k]))
                        return m

                    msgsd = replace_all(tit)
                    em.title = msgsd
                if foot:
                    namespace = {"{name}": ctx.author.name, 
                    "{member}": f"{ctx.author.name}#{ctx.author.discriminator}",
                    "{mention}": ctx.author.mention,
                    "{boosts}": ctx.guild.premium_subscription_count,
                    "{guild_level}": ctx.guild.premium_tier}

                    def replace_all(m: str) -> str:
                        for k in namespace.keys():
                            m = m.replace(k, str(namespace[k]))
                        return m

                    msgs = replace_all(foot)
                    em.set_footer(text=msgs)
                if im:
                    em.set_thumbnail(url=im)
                return await ctx.send(embed=em)

        if option.lower() == "message":
            if not set:
                return await ctx.send("<:4318crossmark:848857812565229601> You forgot the `[set]` parameter, which is the message you want to send when someone boost the server.")

            if len(set) > 500:
                return await ctx.send(f"<:4318crossmark:848857812565229601> Message too long, max. is **500** characters, your is **{len(set)}.**")

            await self.bot.pg_con.execute("INSERT INTO boosting (guild_id, message) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET message = $2", ctx.guild.id, set)
            return await ctx.send("<:4430checkmark:848857812632076314> Message succesfully edited for boosting message!")

        if option.lower() == "channel":
            if not set:
                return await ctx.send("<:4318crossmark:848857812565229601> You forgot the `[set]` parameter, which is the channel where i need to send the message.")

            d = set.strip("<#>")
            c = self.bot.get_channel(int(d))
            if not c:
                return await ctx.send("<:4318crossmark:848857812565229601> This isn't a valid channel.")

            await self.bot.pg_con.execute("INSERT INTO boosting (guild_id, channel_id) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET channel_id = $2", ctx.guild.id, int(d))
            return await ctx.send("<:4430checkmark:848857812632076314> Channel succesfully edited for boosting message!")

        if option.lower() == "embed":
            if not set:
                return await ctx.send("<:4318crossmark:848857812565229601> You forgot the `[set]` parameter, which needs to be `enable` or `disable`.")
        
            if set.lower() == "enable":
                await self.bot.pg_con.execute("INSERT INTO boosting (guild_id, embed) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET embed = $2", ctx.guild.id, True)
                return await ctx.send("<:4430checkmark:848857812632076314> Embed succesfully enabled for boosting message!")

            if set.lower() == "disable":
                await self.bot.pg_con.execute("INSERT INTO boosting (guild_id, embed) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET embed = $2", ctx.guild.id, False)
                return await ctx.send("<:4430checkmark:848857812632076314> Embed succesfully disabled for boosting message!")

        if option.lower() == "embed-image":
            if not set:
                return await ctx.send("<:4318crossmark:848857812565229601> You forgot the `[set]` parameter, which needs to be a valid url which redirects to an image\nYou can also use emojis link to set them as embed image!")

            url = re.match("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", set)
            if not url:
                return await ctx.send("<:4318crossmark:848857812565229601> This isn't a valid url schema for embed image.")

            await self.bot.pg_con.execute("INSERT INTO boosting (guild_id, embed_image) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET embed_image = $2", ctx.guild.id, set)
            return await ctx.send("<:4430checkmark:848857812632076314> Embed image succesfully edited for boosting message!")

        if option.lower() == "embed-title":
            if not set:
                return await ctx.send("<:4318crossmark:848857812565229601> You forgot the `[set]` parameter, which needs to be a phrase with max. 50 letters.")

            if len(set) > 120:
                return await ctx.send(f"<:4318crossmark:848857812565229601> Message too long, max. is **50** characters, your is **{len(set)}.**")

            await self.bot.pg_con.execute("INSERT INTO boosting (guild_id, embed_title) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET embed_title = $2", ctx.guild.id, set)
            return await ctx.send("<:4430checkmark:848857812632076314> Embed title succesfully edited for boosting message!")

        if option.lower() == "embed-footer":
            if not set:
                return await ctx.send("<:4318crossmark:848857812565229601> You forgot the `[set]` parameter, which needs to be a phrase with max. 50 letters.")

            if len(set) > 100:
                return await ctx.send(f"<:4318crossmark:848857812565229601> Message too long, max. is **50** characters, your is **{len(set)}.**")

            await self.bot.pg_con.execute("INSERT INTO boosting (guild_id, embed_footer) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET embed_footer = $2", ctx.guild.id, set)
            return await ctx.send("<:4430checkmark:848857812632076314> Embed footer succesfully edited for boosting message!")
    

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.guild.premium_subscriber_role not in before.roles and after.guild.premium_subscriber_role not in after.roles:
            return

        db = await self.bot.pg_con.fetch("SELECT * FROM boosting WHERE guild_id = $1", after.guild.id)
        if not db:
            return

        mex = db[0]["message"]
        chan = db[0]["channel_id"]
        foot = db[0]["embed_footer"]
        tit = db[0]["embed_title"]
        im = db[0]["embed_image"]
        emb = db[0]["embed"]
        tgf = db[0]["toggle"]

        if not chan:
            return

        if tgf is False:
            return
        
        if not tgf:
            return

        if not mex:
            return
        
        if before.guild.premium_subscriber_role not in before.roles and after.guild.premium_subscriber_role in after.roles:
            namespace = {"{name}": after.name, 
            "{member}": f"{after.name}#{after.discriminator}",
            "{mention}": after.mention,
            "{boosts}": after.guild.premium_subscription_count,
            "{guild_level}": after.guild.premium_tier}

            def replace_all(m: str) -> str:
                for k in namespace.keys():
                    m = m.replace(k, str(namespace[k]))
                return m

            msg = replace_all(mex)

            if emb == True:
                em = discord.Embed(description = msg, color = 0xffcff1)
                if tit:
                    em.title = tit
                if foot:
                    em.set_footer(text=foot)
                if im:
                    em.set_thumbnail(url=im)

                channel = self.bot.get_channel(chan)
                if channel:
                    return await channel.send(embed=em)

            channel = self.bot.get_channel(chan)
            if channel:
                return await channel.send(msg)

def setup(bot):
    bot.add_cog(Boosting(bot))
