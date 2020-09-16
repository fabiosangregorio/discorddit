#!/usr/bin/env python

"""
Entrypoint module.

Handles configuration, setup and starting of the bot, as well as receive
messages and dispatch actions to the other modules.
"""

import logging
from typing import List
import os

import sentry_sdk
import discord
from dotenv import load_dotenv

from pyreddit.pyreddit import helpers
from .linker import Linker
from .config import config
from pyreddit.pyreddit.services.services_wrapper import ServicesWrapper


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

    env = os.getenv("REDDIT_BOTS_MACHINE")
    if env is None or len(env) == 0:
        raise Exception("No REDDIT_BOTS_MACHINE env variable found.")

    load_dotenv(
        dotenv_path=os.path.join(
            os.path.dirname(__file__), f"config/{env.lower()}.env"
        )
    )

    if os.getenv("SENTRY_TOKEN"):
        sentry_sdk.init(os.getenv("SENTRY_TOKEN"), environment=env)

    ServicesWrapper.init_services()

    client = DiscoredditClient()
    Linker.set_bot(client)

    print("Listening...")
    client.run(os.getenv("DISCORD_TOKEN"))
