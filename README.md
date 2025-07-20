# job-finding-bot

This bot automates job search activities, providing job posting notifications and AI-powered resume/job analysis via Discord.

## Key Features

  * **Discord Bot**: Supports chat commands and general conversation, fetches the latest job postings, and sends job analysis results.
  * **Job Posting Management**: Stores job postings in an SQLite DB and manages read/unread statuses.
  * **Resume Generation & Management**: Automatically generates and saves resumes based on multiple source files.
  * **AI Analysis**: Utilizes LangChain-based LLMs for resume and job posting analysis, summarization, and suitability assessment.
  * **File Storage**: Manages input, output, job posting, and prompt files.
  * **Scheduling**: Automatically notifies a Discord channel with job analysis results every hour.

## Usage

1.  Set up your Discord bot token and notification channel ID in the `.env` file.
2.  Install the required Python packages:
    ```sh
    uv sync
    ```
3.  The database and file storage will be initialized automatically.
4.  Run the Discord bot:
    ```sh
    uv run python -m src.main
    ```
5.  You can use AI features in Discord.

## Environment Variables

  * `DISCORD_BOT_TOKEN`: Your Discord bot token.
  * `NOTIFICATION_CHANNEL_ID`: The Discord channel ID where job posting notifications will be sent.