from src.core.schemas.resume_maker import ResumeMakerState, ResumeSection
from src.core.file_storage.file_manager import FileManager
from src.core.file_storage.paths import FileStoragePaths


async def load_resume_sources_node(state: ResumeMakerState) -> ResumeMakerState:
  """Load source files from resume_sources directory."""
  try:
    paths = FileStoragePaths()
    resume_sources_dir = paths.resume_sources_dir
    file_manager = FileManager()

    source_files = []
    source_contents = {}

    # Get all files in resume_sources directory
    if resume_sources_dir.exists():
      for file_path in resume_sources_dir.iterdir():
        if file_path.is_file():
          filename = file_path.name
          content = await file_manager.read_file_async(file_path)
          if content:
            source_files.append(filename)
            source_contents[filename] = content

    return ResumeMakerState(
      source_files=source_files,
      source_contents=source_contents,
      resume_sections=state.resume_sections,
      final_resume=state.final_resume,
      job_target=state.job_target,
    )

  except Exception as e:
    print(f"Error loading resume sources: {e}")
    return state


async def process_resume_sources_node(state: ResumeMakerState) -> ResumeMakerState:
  """Process loaded resume sources and extract relevant information."""
  try:
    resume_sections = []

    # Extract information from source files
    content = "\n".join(state.source_contents.values())

    # Basic section extraction from content
    sections = [
      ("Professional Summary", extract_summary(content)),
      ("Experience", extract_experience(content)),
      ("Skills", extract_skills(content)),
      ("Education", extract_education(content)),
      ("Projects", extract_projects(content)),
    ]

    for idx, (title, content) in enumerate(sections):
      if content.strip():
        resume_sections.append(ResumeSection(title=title, content=content, order=idx))

    return ResumeMakerState(
      source_files=state.source_files,
      source_contents=state.source_contents,
      resume_sections=resume_sections,
      final_resume=state.final_resume,
      job_target=state.job_target,
    )

  except Exception as e:
    print(f"Error processing resume sources: {e}")
    return state


async def generate_resume_node(state: ResumeMakerState) -> ResumeMakerState:
  """Generate the final resume from processed sections."""
  try:
    # Sort sections by order
    sorted_sections = sorted(state.resume_sections, key=lambda x: x.order)

    # Build final resume
    resume_parts = []

    # Header
    header = f"# Resume for {state.job_target}" if state.job_target else "# Resume"
    resume_parts.append(header)
    resume_parts.append("=" * len(header))
    resume_parts.append("")

    # Add each section
    for section in sorted_sections:
      if section.content.strip():
        resume_parts.append(f"## {section.title}")
        resume_parts.append("")
        resume_parts.append(section.content)
        resume_parts.append("")

    final_resume = "\n".join(resume_parts)

    # Update output file path
    paths = FileStoragePaths()
    output_file = str(paths.get_output_report_path("generated_resume"))

    return ResumeMakerState(
      source_files=state.source_files,
      source_contents=state.source_contents,
      resume_sections=state.resume_sections,
      final_resume=final_resume,
      job_target=state.job_target,
      output_file=output_file,
    )

  except Exception as e:
    print(f"Error generating resume: {e}")
    return state


async def save_resume_node(state: ResumeMakerState) -> ResumeMakerState:
  """Save the generated resume to file."""
  try:
    if state.final_resume:
      file_paths = FileStoragePaths()
      file_manager = FileManager()

      output_path = file_paths.get_resume_path()
      result = await file_manager.write_file_async(output_path, state.final_resume)

      if result:
        print(f"Resume saved to: {output_path}")
      else:
        print("Failed to save resume")

    return state

  except Exception as e:
    print(f"Error saving resume: {e}")
    return state


# Helper functions for content extraction
def extract_summary(content: str) -> str:
  """Extract professional summary from content."""
  lines = content.split("\n")
  summary_lines = []
  capture = False

  for line in lines:
    line_lower = line.lower().strip()
    if any(keyword in line_lower for keyword in ["summary", "profile", "about"]):
      capture = True
      continue

    if capture and line.strip() and not line.startswith("#") and len(summary_lines) < 3:
      summary_lines.append(line.strip())
    elif capture and line.strip() == "" and summary_lines:
      break

  if not summary_lines:
    # Fallback to first paragraph
    paragraphs = content.split("\n\n")
    for para in paragraphs:
      if para.strip() and len(para.strip()) > 50:
        return para.strip()[:500]

  return "\n".join(summary_lines)


def extract_experience(content: str) -> str:
  """Extract experience information from content."""
  lines = content.split("\n")
  experience_lines = []
  capture = False

  for line in lines:
    line_lower = line.lower().strip()
    if any(
      keyword in line_lower for keyword in ["experience", "work history", "employment"]
    ):
      capture = True
      continue

    if capture:
      if line.strip() and (
        line.startswith("-") or line.startswith("*") or line.startswith("•")
      ):
        experience_lines.append(line.strip())
      elif line.strip() == "" and experience_lines:
        break

  return "\n".join(experience_lines)


def extract_skills(content: str) -> str:
  """Extract skills information from content."""
  lines = content.split("\n")
  skills_lines = []
  capture = False

  for line in lines:
    line_lower = line.lower().strip()
    if any(keyword in line_lower for keyword in ["skills", "technologies", "tools"]):
      capture = True
      continue

    if capture:
      if line.strip() and (
        line.startswith("-") or line.startswith("*") or line.startswith("•")
      ):
        skills_lines.append(line.strip())
      elif line.strip() == "" and skills_lines:
        break

  return "\n".join(skills_lines)


def extract_education(content: str) -> str:
  """Extract education information from content."""
  lines = content.split("\n")
  education_lines = []
  capture = False

  for line in lines:
    line_lower = line.lower().strip()
    if any(
      keyword in line_lower
      for keyword in ["education", "degree", "university", "college"]
    ):
      capture = True
      continue

    if capture:
      if line.strip() and not line.startswith("#"):
        education_lines.append(line.strip())
      elif line.strip() == "" and education_lines:
        break

  return "\n".join(education_lines)


def extract_projects(content: str) -> str:
  """Extract projects information from content."""
  lines = content.split("\n")
  projects_lines = []
  capture = False

  for line in lines:
    line_lower = line.lower().strip()
    if any(keyword in line_lower for keyword in ["projects", "portfolio"]):
      capture = True
      continue

    if capture:
      if line.strip() and (
        line.startswith("-") or line.startswith("*") or line.startswith("•")
      ):
        projects_lines.append(line.strip())
      elif line.strip() == "" and projects_lines:
        break

  return "\n".join(projects_lines)
