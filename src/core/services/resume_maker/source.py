import os
import time
from pathlib import Path
from markitdown import MarkItDown
from src.core.database.resume_sources import save_resume_source
from src.core.schemas.resume_source import ResumeSource
from src.core.file_storage.file_manager import FileManager
from src.core.file_storage.paths import FileStoragePaths
from src.core.services.utils.generate_random_data import generate_random_string


async def upload_resume(file_path: str, user_id: str) -> ResumeSource:
  """
  Converts a resume file to Markdown, saves it, and stores metadata in the database.

  Args:
      file_path (str): Path to the input resume file (e.g., PDF or DOCX).
      user_id (str): ID of the user uploading the resume.

  Returns:
      ResumeSource: The created resume source record.

  Raises:
      FileNotFoundError: If the input file does not exist.
      ValueError: If the file cannot be converted to Markdown.
  """
  # Check if file exists
  if not os.path.exists(file_path):
    raise FileNotFoundError(f"File not found: {file_path}")

  # Get original file name without path
  original_file_name = Path(file_path).name

  # Convert file to Markdown
  try:
    md = MarkItDown()
    result = md.convert(file_path)
    markdown_content = result.text_content
  except Exception as e:
    raise ValueError(f"Failed to convert file to Markdown: {str(e)}")

  # Generate unique filename
  timestamp = int(time.time())
  random_str = generate_random_string()
  filename = f"{user_id}_{timestamp}_{random_str}.md"

  try:
    file_paths = FileStoragePaths()
    file_manager = FileManager()

    output_path = file_paths.resume_sources_dir / filename
    result = await file_manager.write_file_async(output_path, markdown_content)
  except Exception as e:
    raise ValueError(f"Failed to save Markdown file: {str(e)}")

  # Save metadata to resume_sources table
  resume_source = ResumeSource(
    user_id=user_id, 
    source_file_name=str(output_path),
    original_file_name=original_file_name
  )
  resume_source_id = save_resume_source(resume_source)
  resume_source.id = resume_source_id

  return resume_source