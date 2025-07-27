import asyncio
from pathlib import Path
from typing import Optional


class FileManager:
  """Utility class for file I/O operations."""

  def __init__(self, paths="FileStoragePaths"):
    self.paths = paths

  async def read_file_async(self, file_path: Path) -> Optional[str]:
    """Read file content asynchronously."""
    try:
      if not file_path.exists():
        return None

      def _read():
        with open(file_path, "r", encoding="utf-8") as f:
          return f.read()

      return await asyncio.get_event_loop().run_in_executor(None, _read)
    except Exception as e:
      print(f"Error reading file {file_path}: {e}")
      return None

  def read_file_sync(self, file_path: Path | str) -> Optional[str]:
    """Read file content synchronously."""
    try:
      if isinstance(file_path, str):
        file_path = Path(file_path)
      if not file_path.exists():
        return None

      with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
    except Exception as e:
      print(f"Error reading file {file_path}: {e}")
      return None

  async def write_file_async(self, file_path: Path, content: str) -> bool:
    """Write content to file asynchronously."""
    try:

      def _write():
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
          f.write(content)

      await asyncio.get_event_loop().run_in_executor(None, _write)
      return True
    except Exception as e:
      print(f"Error writing file {file_path}: {e}")
      return False

  def write_file_sync(self, file_path: Path, content: str) -> bool:
    """Write content to file synchronously."""
    try:
      file_path.parent.mkdir(parents=True, exist_ok=True)
      with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
      return True
    except Exception as e:
      print(f"Error writing file {file_path}: {e}")
      return False

  def file_exists(self, file_path: Path) -> bool:
    """Check if file exists."""
    return file_path.exists()
