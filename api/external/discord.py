import time
from discord_webhook import DiscordWebhook

class GoodSaniacWebhook:
    def __init__(self) -> None:
        self.webhookUrl = "https://discord.com/api/webhooks/1159993812966453289/cWqU5uxoNGHTPoOYgsAX11bl62lfu0pR277sZ1NUjfMlaQSpqw7wncpOkTKueBj6no-S"

    def sendVideoMessage(self, videoData: bytes):
        Webhook = DiscordWebhook(
            self.webhookUrl,
            content = "Check out this new play video! It's too cool!" 
        )
        Webhook.add_file(videoData, f'playVideo_{str(time.time())}.mp4')
        Webhook.execute()