import logging
import discord
from discord.ext import commands
from src.core.llm.llm_handler import get_general_llm_response, get_job_ai_response
from src.core.database.job_postings import get_latest_job_postings
from src.core.database.users import save_user, get_user_by_id, update_user
from src.core.schemas.user import User
import os
import aiohttp
from src.core.services.resume_maker.source import upload_resume
from src.core.services.resume_maker.workflow import run_resume_maker

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

  # Split content into chunks that fit within Discord's limit
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

  # Send each chunk as a separate message
  for i, chunk in enumerate(chunks):
    if i == 0:
      await channel.send(chunk)
    else:
      # Add continuation indicator for subsequent messages
      await channel.send(f"...\n{chunk}")


@bot.event
async def on_ready():
  """Event handler for when the bot is ready."""
  if bot.user:
    print(f"Logged in as {bot.user.name} ({bot.user.id})")
  print("Bot is ready!")


@bot.command(name="최신공고")
async def latest_jobs(ctx: commands.Context, limit: int = 5):
  """Fetches and displays the latest job postings."""
  try:
    latest_jobs = get_latest_job_postings(limit=limit)
    if latest_jobs:
      response_message = "**최신 채용 공고:**\n"
      for i, job in enumerate(latest_jobs):
        response_message += f"\n**{i + 1}. {job.title}**\n"
        response_message += f"   회사: {job.company}\n"
        response_message += f"   위치: {job.location}\n"
        response_message += f"   공고일: {job.posted_at}\n"
        response_message += f"   URL: <{job.url}>\n"
      await send_long_message(ctx, response_message)
    else:
      await ctx.send("아직 저장된 채용 공고가 없습니다.")
  except Exception as e:
    logger.error(f"An error occurred during !최신공고 command: {e}")
    await ctx.send("최신 채용 공고를 가져오는 중 오류가 발생했습니다.")


@bot.command(name="포트폴리오")
async def portfolio(ctx: commands.Context):
  """Handles portfolio file uploads and saves them to resume_sources."""
  try:
    # Ensure user is in the database
    user = get_user_by_id(ctx.author.name)
    if not user:
      new_user = User(id=ctx.author.name, name=ctx.author.name, resume_file=None)
      save_user(new_user)
    elif user.name != ctx.author.name:
      update_user(ctx.author.name, name=ctx.author.name)

    # Check for attachments
    if not ctx.message.attachments:
      await ctx.send("포트폴리오 파일을 첨부해 주세요!")
      return

    # Process the first attachment (assuming one resume file per command)
    attachment = ctx.message.attachments[0]
    allowed_extensions = (".pdf", ".docx", ".xlsx", ".txt", ".md", ".pptx", ".html")
    if not attachment.filename.lower().endswith(allowed_extensions):
      await ctx.send(
        "PDF, DOCX, XLSX, TXT, MD, PPTX 또는 HTML 파일만 업로드할 수 있습니다!"
      )
      return

    # Download the attachment
    file_path = f"uploads/{ctx.author.name}_{attachment.filename}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    async with aiohttp.ClientSession() as session:
      async with session.get(attachment.url) as resp:
        if resp.status == 200:
          with open(file_path, "wb") as f:
            f.write(await resp.read())
        else:
          await ctx.send("파일 다운로드 중 오류가 발생했습니다!")
          return

    # Call upload_resume function
    try:
      await upload_resume(file_path, ctx.author.name)
      await ctx.send("포트폴리오가 성공적으로 업로드되었습니다!")
    except Exception as e:
      logger.error(f"Error during upload_resume: {e}")
      await ctx.send("포트폴리오 업로드 중 오류가 발생했습니다!")
      # Clean up file if upload fails
      if os.path.exists(file_path):
        os.remove(file_path)
    finally:
      # Clean up file after successful upload (optional, depending on upload_resume behavior)
      if os.path.exists(file_path):
        os.remove(file_path)

  except Exception as e:
    logger.error(f"An error occurred during !포트폴리오 command: {e}")
    await ctx.send("포트폴리오 처리 중 오류가 발생했습니다.")


@bot.command(name="이력서제작")
async def create_resume(ctx: commands.Context, *, job_target: str = ""):
  """Handles resume creation requests."""
  try:
    # Ensure user is in the database
    user = get_user_by_id(ctx.author.name)
    if not user:
      new_user = User(id=ctx.author.name, name=ctx.author.name, resume_file=None)
      save_user(new_user)

    # Validate job_target
    if not job_target.strip():
      await ctx.send("사용법: `!이력서제작 [직무명]` (예: `!이력서제작 웹개발자`)")
      return

    # Create resume using the workflow
    await ctx.send(f"이력서 제작을 시작합니다... 직무: **{job_target}**")

    result = await run_resume_maker(
      job_target=job_target.strip(), user_id=ctx.author.name
    )

    if result:
      await ctx.send(
        f"✅ 이력서 제작이 완료되었습니다!\n\n**제작된 이력서 정보:**\n- 직무: {job_target}\n이력서내용:"
      )
      await send_long_message(ctx, result["final_resume"])
    else:
      await ctx.send("이력서 제작 중 오류가 발생했습니다.")

  except Exception as e:
    logger.error(f"Error during resume creation: {e}")
    await ctx.send(f"이력서 제작 중 오류가 발생했습니다: {str(e)}")


@bot.command(name="채용공고탐색")
async def add_job_posting(ctx: commands.Context):
  """사용자의 이력서를 기반으로 관련 채용공고를 검색하고 추가합니다."""
  try:
    user_id = ctx.author.name
    user = get_user_by_id(user_id)

    # Check if user has a resume
    if not user or not user.resume_file:
      await ctx.send(
        "이력서가 등록되지 않았습니다. `!포트폴리오 추가` 명령어를 사용하여 먼저 이력서를 등록해주세요."
      )
      return

    await ctx.send(
      "이력서를 기반으로 최적의 채용공고를 검색하고 있습니다... 잠시만 기다려 주세요."
    )

    # Import and run the new job search workflow
    from src.core.services.job_search.workflow import run_job_search_workflow

    result_state = await run_job_search_workflow(user_id)

    scraped_results = result_state.get("scraped_results", [])
    successful_postings = [
      res for res in scraped_results if res["success"] and res["job_posting"]
    ]

    if not successful_postings:
      await ctx.send("관련 채용공고를 찾지 못했거나, 분석에 실패했습니다.")
      return

    response = "✅ **다음 채용공고를 성공적으로 추가했습니다!**\n"
    for i, res in enumerate(successful_postings):
      job = res["job_posting"]
      response += f"\n**{i + 1}. {job.title}** - {job.company}\n"
      response += f"   URL: <{job.url}>\n"

    await send_long_message(ctx, response)

  except Exception as e:
    logger.error(f"Error during !채용공고 추가 command: {e}")
    await ctx.send(f"채용공고 추가 중 오류가 발생했습니다: {str(e)}")


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
      # Update name if user exists
      if user.name != message.author.display_name:
        update_user(message.author.name, name=message.author.display_name)
    else:
      # Insert new user
      new_user = User(
        id=message.author.name, name=message.author.display_name, resume_file=None
      )
      save_user(new_user)
  except Exception as e:
    logger.error(f"Error handling user in database: {e}")

  # If the message is not a command, treat it as a general conversation
  if not message.content.startswith(BOT_COMMAND_PREFIX):
    messages = []
    async for msg in message.channel.history(limit=16):
      user_name = (
        getattr(msg.author, "display_name", None)
        or getattr(msg.author, "global_name", None)
        or msg.author.name
      )

      if hasattr(msg, "content"):
        messages.append({"name": user_name, "content": msg.content})
      else:
        messages.append({"name": "user", "content": ""})
    messages.reverse()

    if (
      isinstance(message.channel, discord.TextChannel)
      and message.channel.name == "구직활동"
    ):
      query = message.content
      if not query:
        return

      try:
        relevant_jobs = []
        response = await get_job_ai_response(messages, relevant_jobs)
        await send_long_message(message.channel, response)
      except Exception as e:
        logger.error(f"An error occurred during job-related question: {e}")
        await message.channel.send("An unexpected error occurred.")
    else:
      try:
        response = await get_general_llm_response(messages)
        await send_long_message(message.channel, response)
      except Exception as e:
        logger.error(f"An error occurred during general message handling: {e}")
        await message.channel.send("An unexpected error occurred.")

  print(f"Processed command from {message.author.name}: {message.content}")
  # Process commands after handling the message
  await bot.process_commands(message)
