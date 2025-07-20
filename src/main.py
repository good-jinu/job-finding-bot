import asyncio
from core.database.init import init_db
from src.bot.run import run_bot


async def main():
  """Initializes the database, schedules jobs, and runs the bot."""
  init_db()

  # Start the bot
  bot_task = asyncio.create_task(run_bot())

  await bot_task


if __name__ == "__main__":
  asyncio.run(main())
