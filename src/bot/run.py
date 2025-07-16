import asyncio
import os
from src.bot.discord.discord_bot import bot
from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "YOUR_DISCORD_BOT_TOKEN")


async def run_bot():
  """Runs the Discord bot."""
  if DISCORD_BOT_TOKEN == "YOUR_DISCORD_BOT_TOKEN":
    print(
      "WARNING: Please replace 'YOUR_DISCORD_BOT_TOKEN' in your .env file or config.py."
    )
    return

  async with bot:
    await bot.load_extension("src.bot.tasks.job_notifier")
    await bot.start(DISCORD_BOT_TOKEN)


if __name__ == "__main__":
  asyncio.run(run_bot())
