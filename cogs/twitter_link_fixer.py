import re
from urllib.parse import urlparse

from discord.ext import commands


class TwitterLinkFixerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def rewrite_url(self, message):
        parse_url = urlparse(message)
        return parse_url._replace(netloc="fxtwitter.com").geturl()

    def find_twitter_urls(self, message):
        twitter_or_x_pattern = re.compile(r'https?://(?:www\.)?(?:twitter\.com|x\.com)/\S+')
        return re.findall(twitter_or_x_pattern, message)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        twitter_urls = self.find_twitter_urls(message.content.lower())
        if twitter_urls:
            for url in twitter_urls:
                await message.channel.send(f"Fixed that for you! {self.rewrite_url(url)}")
async def setup(bot):
    await bot.add_cog(TwitterLinkFixerCog(bot))
