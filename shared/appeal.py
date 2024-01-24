from asyncio import TimeoutError

from discord import Color, Member, app_commands as serverutil, Forbidden
from discord import Interaction, Embed, Object
from discord import Message
from discord.ext.commands import GroupCog, Bot

from assets.functions import Warn, Appeal
from config import hazead


class AppealCog(GroupCog, name="appeal"):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def ha_appeal(self, ctx: Interaction, warn_id: int):
        check_warn = Warn(user=ctx.user, warn_id=warn_id).check()
        if check_warn is None:
            await ctx.followup.send("Invalid warn ID", ephemeral=True)
            return

        appeal_log = ctx.guild.get_channel(951783773006073906)

        try:
            await ctx.followup.send(
                "Please make sure your DMs are opened to start the appealing process",
                ephemeral=True,
            )

            await ctx.user.send(
                "Please tell us why we should revoke your warn. Please supply video or images if required.\nYou have 3 minutes to tell"
            )

            def check(m: Message):
                attachments = bool(m.attachments)
                content = bool(m.content)
                if attachments is True:
                    if content is True:
                        return m.author == ctx.user and m.content and m.attachments
                    if content is True:
                        return m.author == ctx.user and m.content
                    if attachments is True:
                        return m.author == ctx.user and m.attachments
                    if attachments is True and content is False:
                        return m.author == ctx.user and m.attachments
                if content is True:
                    return m.author == ctx.user and m.content
                if attachments is True:
                    return m.author == ctx.user and m.attachments
                if attachments is True and content is False:
                    return m.author == ctx.user and m.attachments

            try:
                msg: Message = await self.bot.wait_for(
                    "message", check=check, timeout=180
                )

                await ctx.user.send(
                    "Thank you for appealing for your warn. The appropriate staff member will review it and will send updates if any action is needed\nPlease do not rush us or your appeal will be denied."
                )

                reason = check_warn[2]
                moderator = await self.bot.fetch_user(check_warn[1])

                appeal = Embed(title=f"{ctx.user}'s appeal")
                appeal.add_field(name="Warn ID", value=warn_id, inline=True)
                appeal.add_field(
                    name="Warn reason",
                    value=f"{reason}\nWarned by: {moderator}",
                    inline=False,
                )
                appeal.set_footer(
                    text="To approve the appeal, use `/appeal accept warn_id``"
                )

                try:
                    image_urls = [x.url for x in msg.attachments]
                    images = "\n".join(image_urls)
                    await appeal_log.send(
                        "{}\n{}".format(msg.content, images), embed=appeal
                    )
                except Exception:
                    await appeal_log.send(msg.content, embed=appeal)
            except TimeoutError:
                await ctx.user.send("You have ran out of time. Please try again.")
        except Forbidden:
            await ctx.followup.send(
                "Please open your DMs to start the appeal process", ephemeral=True
            )


    async def approve_ha_appeal(self, ctx: Interaction, member: Member, warn_id: int):
        if ctx.channel.id == 951783773006073906:
            appeal_data = Appeal(member, warn_id)
            check = appeal_data.check()

            if check is None:
                await ctx.followup.send(
                    "Invalid Warn ID or member was not warned with this Warn " "ID"
                )
                return
            member_id: int = check[0]
            warn_id: int = check[3]
            member = await self.bot.fetch_user(member_id)

            appeal_data.remove()

            try:
                await member.send(
                    f"Hello {member.mention},\nUpon looking into your appeal, we have decided to revoke your warn (**Warn ID:** {warn_id}).\nWe apologies for this and promised that we will be more careful when doing ad moderations against you and other members.\nThank you and enjoy your day!"
                )
            except Forbidden:
                pass

            await ctx.followup.send("Warning revoked and message sent to member")
        else:
            ch = await self.bot.fetch_channel(951783773006073906)
            await ctx.followup.send(
                "Please do the command in {}".format(ch.mention), ephemeral=True
            )



    @serverutil.command(description="Apply for an adwarn appeal")
    @serverutil.describe(warn_id="Insert the warn ID that you wish to appeal your warn")
    async def apply(self, ctx: Interaction, warn_id: int):
        await ctx.response.defer()
        if ctx.guild.id == 925790259160166460:
            await self.ha_appeal(ctx, warn_id)


    @serverutil.command(description="Approve an appeal")
    @serverutil.checks.has_any_role(
        925790259319558159,
        925790259319558158,
        925790259319558157,
        1011971782426767390,
        925790259319558154,
        889019375988916264,
        749608853376598116,
        919410986249756673,
        947109389855248504,
        849778145087062046,
    )
    @serverutil.describe(warn_id="Insert the warn_id ID shown from the member's appeal")
    async def approve(self, ctx: Interaction, member: Member, warn_id: int):
        await ctx.response.defer()
        if ctx.guild.id == 925790259160166460:
            await self.approve_ha_appeal(ctx, member, warn_id)



async def setup(bot: Bot):
    await bot.add_cog(AppealCog(bot), guild=Object(hazead))
