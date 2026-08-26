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
            "instagram.com": "www.kkinstagram.com",
            "reddit.com": "www.vxreddit.com",
        }

    def rewrite_media_url(self, message, domain):
        parse_url = urlparse(message)
        # return the value of the domain key in the embed_domains dictionary
        return parse_url._replace(netloc=self.embed_domains[domain]).geturl()

    def find_urls(self, message, domain):
        pattern = re.compile(rf"https?://(?:www\.)?(?:{domain})/\S+")
        return re.findall(pattern, message)

    def twitter_web_viewer_url(self, url):
        """Extra url for twitter and x links that takes the original URL's number and converts it to
            a twitter web viewer url. 
            example: if new_url is "https://www.fxtwitter.com/samimokbel_bbc/status/2092649709462564884?s=46"
            the function should return "https://twitterwebviewer.com/?tweet=2092649709462564884"
        """
        match = re.search(r"status/(\d+)", url)
        if match:
            tweet_id = match.group(1)
            return f"https://twitterwebviewer.com/?tweet={tweet_id}"
        return None

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        # finds all links, we can limit this if we struggle with people spamming.
        for domain in self.embed_domains:
            if message.guild.name != "gunners" and domain == "instagram.com":
                break
            try:
                urls = self.find_urls(message.content.lower(), domain)
            except IndexError:
                logger.info(f"{message.content} does not contain any {domain} links")
            if urls:
                original_urls = self.find_urls(message.content, domain)
                url = original_urls[0]
                new_url = self.rewrite_media_url(url, domain)
                await message.edit(suppress=True)
                if "fxtwitter.com" in new_url:
                    twitter_web_viewer = self.twitter_web_viewer_url(new_url)
                    if twitter_web_viewer:
                        await message.reply(
                            f"Fx'ed that for you! {new_url}\nTwitter Web Viewer version: <{twitter_web_viewer}>", mention_author=False
                        )
                    else:
                        await message.reply(
                            f"Fx'ed that for you! {new_url}", mention_author=False
                        )
                else:
                    await message.reply(
                    f"Fx'ed that for you! {new_url}", mention_author=False
                    )


async def setup(bot):
    await bot.add_cog(LinkFixerCog(bot))
