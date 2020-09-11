"""Linker class which handles all telereddit requests."""

import logging

from discord import Client, Embed
from .config.config import (
    MAX_TRIES,
)
from pyreddit.pyreddit import reddit, helpers
from pyreddit.pyreddit.models.media import ContentType
from pyreddit.pyreddit.exceptions import RedditError, SubredditError
from discoreddit.exceptions import (
    DiscoredditError,
    PostSendError,
)


class Linker:
    """
    Handle a single telereddit request.

    Gets instanciated at every telereddit request. (new message, messsage
    callback, etc.)

    Attributes
    ----------
    bot : `discord.Client`
        discord.py's Bot instance: initialized by `set_bot()`.
    chat_id : Int
        Discord's chat id to which to send the message.
    args : dict
        Args to construct the Discord message.

    """

    bot: Client = None

    @classmethod
    def set_bot(cls, bot: Client) -> None:
        """
        Set the discord.py's Bot instance for the Linker object.

        This should be set only once, at the package startup.

        .. note:: This needs to be set before starting the bot loop.

        Parameters
        ----------
        bot : Client
            The bot instance provided by discord.py

        """
        cls.bot = bot

    def __init__(self, channel: int) -> None:
        self.channel: int = channel

    async def send_random_post(self, subreddit: str) -> None:
        """
        Send a random post to the chat from the given subreddit.

        Potentially catch Telereddit exceptions.

        Parameters
        ----------
        subreddit : str
            Valid subreddit name.

            .. note:: This should be a r/ prefixed subreddit name.

        """
        for _ in range(MAX_TRIES):
            try:
                return await self.send_post(helpers.get_random_post_url(subreddit))
            except (RedditError, DiscoredditError) as e:
                err = e
                if isinstance(e, SubredditError):
                    break
        return await self._send_exception_message(err)

    async def send_post_from_url(self, post_url: str) -> None:
        """
        Try to send the reddit post relative to post_url to the chat.

        Potentially catch Telereddit exceptions.

        Parameters
        ----------
        post_url : str
            Reddit share link of the post.

        """
        try:
            await self.send_post(post_url, from_url=True)
        except (RedditError, DiscoredditError) as e:
            await self._send_exception_message(e)

    async def send_post(self, post_url: str, from_url: bool = False) -> None:
        """
        Send the reddit post relative to post_url to the chat.

        This is the core functionality of Linker.

        Parameters
        ----------
        post_url : str
            Reddit share link of the post.

        from_url : Boolean
            (Default value = False)

            Indicates whether the post url has been received from the chat or
            from the random post.

        """
        post = reddit.get_post(post_url)
        assert post is not None

        try:
            if post.get_type() == ContentType.VIDEO:
                return await self.channel.send("Video not supported yet.")
            elif post.get_type() == ContentType.YOUTUBE:
                return await self.channel.send("Yotube not supported yet.")

            embed: Embed = Embed(
                title=post.title,
                description=post.text,
                url=post.permalink,
                type="rich",
            )
            embed.add_field(name="** **", value=post.get_footer())
            if any(post.get_type() == c for c in [ContentType.PHOTO, ContentType.GIF]):
                assert post.media is not None
                embed.set_image(url=post.media.url)

            await self.channel.send(embed=embed)

        except Exception as e:
            raise PostSendError(
                {"post_url": post.permalink, "media_url": post.media.url}  # type: ignore
            ) from e

    async def _send_exception_message(self, e: Exception) -> None:
        """
        Send the exception text as a Telegram message to notify the user.

        Parameters
        ----------
        e : Exception
            Error to send as a message.
        """
        await self.channel.send(str(e))
