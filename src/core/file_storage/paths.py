from pathlib import Path


class FileStoragePaths:
  """Centralized file storage path management."""

  def __init__(self, base_path: str = ".file_storage"):
    self.base_path = Path(base_path)
    self._ensure_directories()

  def _ensure_directories(self):
    """Create necessary directories if they don't exist."""
    directories = [
      self.base_path,
      self.base_path / "input",
      self.base_path / "output",
      self.base_path / "job_postings",
      self.base_path / "prompts",
    ]

    for directory in directories:
      directory.mkdir(parents=True, exist_ok=True)

  @property
  def input_dir(self) -> Path:
    """Input directory for user files."""
    return self.base_path / "input"

  @property
  def output_dir(self) -> Path:
    """Output directory for generated reports."""
    return self.base_path / "output"

  @property
  def job_postings_dir(self) -> Path:
    """Directory for job posting content files."""
    return self.base_path / "job_postings"

  @property
  def prompts_dir(self) -> Path:
    """Directory for prompt files."""
    return self.base_path / "prompts"

  def get_resume_path(self) -> Path:
    """Get resume file path."""
    return self.input_dir / "resume.md"

  def get_job_content_path(self, filename: str) -> Path:
    """Get job posting content file path."""
    return self.job_postings_dir / filename

  def get_output_report_path(self, prefix: str) -> Path:
    """Get output report file path with timestamp."""
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_prefix = "".join(
      c for c in prefix if c.isalnum() or c in (" ", "-", "_")
    ).rstrip()
    return self.output_dir / f"{safe_prefix}_{timestamp}.md"
