#!/usr/bin/env python

"""
Entrypoint module.

Handles configuration, setup and starting of the bot, as well as receive
messages and dispatch actions to the other modules.
"""

import logging
from typing import List

import sentry_sdk
import discord

from pyreddit.pyreddit import helpers
from .linker import Linker
from .config import config
from pyreddit.pyreddit.services.services_wrapper import ServicesWrapper
from pyreddit.pyreddit.config.config import load_secret as pyreddit_load_secret


class DiscoredditClient(discord.Client):
    async def on_message(self, message: discord.Message) -> None:
        """
        Entrypoint of the bot's logic. Handles a single message.

        Parameters
        ----------
        update : Update
            The Update object provided by python-telegram-bot
        context : CallbackContext
            The Context object provided by python-telegram-bot

        """
        if message.author == self.user:
            return

        linker: Linker = Linker(channel=message.channel)
        text: str = message.content.lower()
        if any(r in text for r in config.REDDIT_DOMAINS):
            posts_url: List[str] = helpers.get_urls_from_text(message.content)
            for url in posts_url:
                await linker.send_post_from_url(url)
        elif "r/" in text:
            subreddits: List[str] = helpers.get_subreddit_names(text)
            for subreddit in subreddits:
                await linker.send_random_post(subreddit)


def main() -> None:
    """Entrypoint of telereddit. Handles configuration, setup and start of the bot."""
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s\n\n",
        level=logging.INFO,
    )

    config.load_secret()
    pyreddit_load_secret(config.secret)

    if config.SENTRY_ENABLED:
        sentry_sdk.init(config.secret.SENTRY_TOKEN, environment=config.ENV)

    ServicesWrapper.init_services()

    client = DiscoredditClient()
    Linker.set_bot(client)

    print("Listening...")
    client.run(config.secret.DISCORD_TOKEN)
