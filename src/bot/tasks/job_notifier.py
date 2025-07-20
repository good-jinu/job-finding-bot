import asyncio
import datetime
import os

import discord
from discord.ext import commands, tasks

from src.core.database.db_handler import get_unread_job_posting, mark_job_as_read
from src.core.job_analysis import run_job_analysis
from src.bot.discord.discord_bot import send_long_message

# KST timezone
KST = datetime.timezone(datetime.timedelta(hours=9))


class JobNotifier(commands.Cog):
  """Cog for sending job posting notifications every hour from 7 AM to 10 PM KST."""

  def __init__(self, bot: commands.Bot):
    self.bot = bot
    self.notification_channel_id = int(os.getenv("NOTIFICATION_CHANNEL_ID", 0))
    if self.notification_channel_id == 0:
      print("NOTIFICATION_CHANNEL_ID is not set. The job notifier task will not run.")
    else:
      print(
        f"Job notifier task started. Notification channel ID: {self.notification_channel_id}"
      )
      self.send_hourly_jobs.start()

  def cog_unload(self):
    self.send_hourly_jobs.cancel()

  @tasks.loop(hours=1)
  async def send_hourly_jobs(self):
    """Fetches and sends one unread job posting every hour from 7 AM to 10 PM KST."""

    # Check if current time is between 7 AM and 10 PM KST
    now = datetime.datetime.now(KST)
    if now.hour < 7 or now.hour >= 22:
      return  # Skip if outside business hours

    print(f"Running hourly job notification task at {now.strftime('%H:%M')} KST.")
    channel = self.bot.get_channel(self.notification_channel_id)
    if not channel or not isinstance(channel, discord.TextChannel):
      print(f"Could not find text channel with ID {self.notification_channel_id}.")
      return

    try:
      # Get one unread job posting
      job = await asyncio.to_thread(get_unread_job_posting)

      if not job:
        print("No unread job postings available.")
        return

      print(f"Analyzing job posting: {job.title} at {job.company}")

      # Run job analysis workflow
      analysis_result = await run_job_analysis(
        job_url=job.url,
        job_title=job.title,
        job_company=job.company,
        job_description=job.description,
      )

      # Parse analysis result
      try:
        message = analysis_result["analysis_result"]

        # Send the message
        await send_long_message(channel, message)

        # Mark the job as read
        await asyncio.to_thread(mark_job_as_read, job.url)
        print(f"Sent job analysis: {job.title} at {job.company}")

      except Exception as e:
        print(f"Error parsing analysis result: {e}")
        # Fallback to simple message
        fallback_message = f"""📢 **새로운 채용 공고**

**💼 {job.title}**
**🏢 {job.company}**
**📍 {job.location}**
**📅 {job.posted_at}**
**🔗 URL:** <{job.url}>

*상세 분석 중 오류가 발생했습니다. 원본 URL을 확인해주세요.*"""

        await channel.send(fallback_message)
        await asyncio.to_thread(mark_job_as_read, job.url)

    except Exception as e:
      print(f"Error in hourly job notification task: {e}")
      await channel.send("채용 공고 분석 중 오류가 발생했습니다.")

  @send_hourly_jobs.before_loop
  async def before_send_hourly_jobs(self):
    print("Waiting until bot is ready to start job notifier task...")
    await self.bot.wait_until_ready()
    print("Bot is ready. Job notifier task is running (7 AM - 10 PM KST, every hour).")


async def setup(bot: commands.Bot):
  """Sets up the JobNotifier cog."""
  if not os.getenv("NOTIFICATION_CHANNEL_ID"):
    print(
      "NOTIFICATION_CHANNEL_ID environment variable not set. Skipping JobNotifier cog setup."
    )
    return
  await bot.add_cog(JobNotifier(bot))
