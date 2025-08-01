import logging
import discord
from discord.ext import commands
from src.core.agents.job_finding_agent import create_job_finding_agent
from src.core.database.users import save_user, get_user_by_id, update_user
from src.core.schemas.user import User

# --- Bot Configuration ---
BOT_COMMAND_PREFIX = "!"
DISCORD_MESSAGE_LIMIT = 2000

# Initialize the Discord client with necessary intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=BOT_COMMAND_PREFIX, intents=intents)

logger = logging.getLogger(__name__)


async def send_long_message(channel, content: str):
  """Send a message that may exceed Discord's 2000 character limit by splitting it into multiple messages."""
  if len(content) <= DISCORD_MESSAGE_LIMIT:
    await channel.send(content)
    return

  chunks = []
  current_chunk = ""
  for line in content.split("\n"):
    if len(current_chunk) + len(line) + 1 <= DISCORD_MESSAGE_LIMIT:
      current_chunk += line + "\n"
    else:
      if current_chunk:
        chunks.append(current_chunk.strip())
      current_chunk = line + "\n"
  if current_chunk:
    chunks.append(current_chunk.strip())

  for i, chunk in enumerate(chunks):
    if i == 0:
      await channel.send(chunk)
    else:
      await channel.send(f"...\n{chunk}")


@bot.event
async def on_ready():
  """Event handler for when the bot is ready."""
  if bot.user:
    print(f"Logged in as {bot.user.name} ({bot.user.id})")
  print("Bot is ready!")


@bot.event
async def on_message(message: discord.Message):
  """Event handler for when a message is sent."""
  if message.author.bot:
    return

  print(f"Received message from {message.author.name}: {message.content}")

  # Add or update user in the database
  try:
    user = get_user_by_id(message.author.name)
    if user:
      if user.name != message.author.display_name:
        update_user(message.author.name, name=message.author.display_name)
    else:
      new_user = User(
        id=message.author.name, name=message.author.display_name, resume_file=None
      )
      save_user(new_user)
  except Exception as e:
    logger.error(f"Error handling user in database: {e}")

  # Process message with the agent
  if not message.content.startswith(BOT_COMMAND_PREFIX):
    try:
      # Create the job finding agent
      agent_executor = create_job_finding_agent(user_id=message.author.name)
      response = await agent_executor.ainvoke({"messages": [("user", message.content)]})
      await send_long_message(message.channel, response["messages"][-1].content)
    except Exception as e:
      logger.error(f"An error occurred during agent processing: {e}")
      await message.channel.send("An unexpected error occurred.")

  await bot.process_commands(message)
