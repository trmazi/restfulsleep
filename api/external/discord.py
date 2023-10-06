import discord
import requests

class GoodSaniacWebhook:
    def __init__(self) -> None:
        self.webhook: discord.Webhook = discord.Webhook.partial(
            1159993812966453289,
            "cWqU5uxoNGHTPoOYgsAX11bl62lfu0pR277sZ1NUjfMlaQSpqw7wncpOkTKueBj6no-S"
        )

    def sendVideoMessage(self, videoData: bytes):
        self.webhook.send(
            "Check out this new play video! It's too cool!",
            file=discord.File(videoData)
        )