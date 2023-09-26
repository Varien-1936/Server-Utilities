from typing import Optional

from discord import User, ui, ButtonStyle
from discord.interactions import Interaction

class Confirmation(ui.View):
    def __init__(self, author: Optional[User] = None):
        super().__init__(timeout=600)
        self.value = None
        self.author = author

    @ui.button(label="Confirm", style=ButtonStyle.green)
    async def confirm(self, button: ui.Button, ctx: Interaction):
        self.value = True
        self.stop()

    @ui.button(label="Cancel", style=ButtonStyle.red)
    async def cancel(self, button: ui.Button, ctx: Interaction):
        self.value = False
        self.stop()

    async def interaction_check(self, ctx: Interaction):
        return ctx.user.id == self.author.id


class MobileView(ui.View):
    def __init__(self, author: Optional[User] = None):
        super().__init__(timeout=600)
        self.value = None
        self.author = author

    @ui.button(label="Mobile Version", style=ButtonStyle.green)
    async def confirm(self, button: ui.Button, ctx: Interaction):
        self.value = True
        self.stop()

    async def interaction_check(self, ctx: Interaction):
        return ctx.user.id == self.author.id
