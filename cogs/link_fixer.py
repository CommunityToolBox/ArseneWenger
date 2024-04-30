import logging
import re
from urllib.parse import urlparse

from discord.ext import commands

logger = logging.getLogger(__name__)


class LinkFixerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed_domains = {
            "twitter.com": "www.fxtwitter.com",
            "x.com": "www.fxtwitter.com",
            "tiktok.com": "www.vxtiktok.com",
            "instagram.com": "www.ddinstagram.com",
            "reddit.com": "www.rxddit.com"
        }
    def rewrite_media_url(self, message, domain):
        parse_url = urlparse(message)
        #return the value of the domain key in the embed_domains dictionary
        return parse_url._replace(netloc=self.embed_domains[domain]).geturl()

    def find_urls(self, message, domain):
        pattern = re.compile(rf'https?://(?:www\.)?(?:{domain})/\S+')
        return re.findall(pattern, message)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        # Limit fixing Tweets to first found link, to prevent potential spam
        for domain in self.embed_domains.keys():
            try:
                urls = self.find_urls(message.content.lower(), domain)
            except IndexError:
                logger.info(f'{message.content} does not contain any {domain} links')
            if urls:
                original_urls = self.find_urls(message.content, domain)
                url = original_urls[0]
                new_url = self.rewrite_media_url(url, domain)
                await message.edit(suppress=True)
                await message.reply(f"Fx'ed that for you! {new_url}", mention_author=False)


async def setup(bot):
    await bot.add_cog(LinkFixerCog(bot))