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
import re

# --- Bot Configuration ---
BOT_COMMAND_PREFIX = "!"
DISCORD_MESSAGE_LIMIT = 5000

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


@bot.command(name="포트폴리오 추가")
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


@bot.command(name="채용공고 추가")
async def add_job_posting(ctx: commands.Context, *, message_content: str):
  """채용공고 URL을 통해 새로운 채용공고를 추가합니다."""
  try:
    # Ensure user is in the database
    user = get_user_by_id(ctx.author.name)
    if not user:
      new_user = User(id=ctx.author.name, name=ctx.author.name, resume_file=None)
      save_user(new_user)
    elif user.name != ctx.author.name:
      update_user(ctx.author.name, name=ctx.author.name)

    # URL 추출
    url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
    urls = re.findall(url_pattern, message_content)

    if not urls:
      await ctx.send(
        "채용공고 URL을 찾을 수 없습니다. 채용공고 URL을 포함하여 다시 시도해주세요!"
      )
      return

    job_url = urls[0]

    await ctx.send("채용공고를 분석하고 있습니다... 잠시만 기다려 주세요.")

    # 채용공고 추출 워크플로우 실행
    from src.core.services.job_posting_extractor.workflow import (
      run_job_posting_extractor,
    )

    result = await run_job_posting_extractor(job_url, ctx.author.name)

    if result.success and result.job_posting:
      job = result.job_posting

      # 성공 메시지 전송
      response = f"""
✅ **채용공고 추가 완료!**

**{job.title}** - {job.company}
📍 위치: {job.location or "미지정"}
📅 게시일: {job.posted_at or "지정 안됨"}

**요약 설명:**
{job.description or "설명이 제공되지 않았습니다."}

**저장된 파일:** {result.saved_file_path or "파일 경로 없음"}
**원본 URL:** <{job.url}>
      """

      await send_long_message(ctx, response)
    else:
      await ctx.send(f"채용공고 추출 중 오류가 발생했습니다: {result.error_message}")

  except Exception as e:
    logger.error(f"Error during !채용공고 추가 command: {e}")
    await ctx.send(f"채용공고 추가 중 오류가 발생했습니다: {str(e)}")


@bot.event
async def on_message(message: discord.Message):
  """Event handler for when a message is sent."""
  if message.author.bot:
    return

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

  # Process commands first
  await bot.process_commands(message)

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
