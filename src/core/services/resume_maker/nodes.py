from typing import Dict
from src.core.schemas.resume_maker import ResumeMakerState
from src.core.file_storage.file_manager import FileManager
from src.core.file_storage.paths import FileStoragePaths
from src.core.llm.providers import get_resume_generation_model
from src.core.database.users import update_user


async def load_resume_sources_node(state: ResumeMakerState) -> Dict:
  """Load source file names from resume_sources directory."""
  try:
    paths = FileStoragePaths()
    resume_sources_dir = paths.resume_sources_dir
    source_files = []

    if resume_sources_dir.exists():
      for file_path in resume_sources_dir.iterdir():
        if file_path.is_file():
          source_files.append(file_path)  # 전체 경로 저장

    print(f"Loaded {len(source_files)} source files.")
    return {"source_files": source_files}

  except Exception as e:
    print(f"Error loading resume sources: {e}")
    return {}


async def plan_resume_node(state: ResumeMakerState) -> Dict:
  """Use LLM to create a detailed plan for writing the resume based on job target."""
  try:
    file_manager = FileManager()
    contents = []
    for file_path in state.source_files:
      content = await file_manager.read_file_async(file_path)
      if content:
        contents.append(content)

    full_content = "\n\n---\n\n".join(contents)

    llm = get_resume_generation_model()

    # Create detailed planning prompt
    planning_prompt = f"""Based on the following source materials and job target, create a comprehensive plan for writing a professional resume.

Job Target: {state.job_target or "General position"}

Source Materials:
{full_content}

Create a detailed plan that includes:
1. Key competencies and skills that should be emphasized for this job target
2. Important achievements and experiences to highlight
3. Specific keywords and terminology relevant to the role
4. Recommended resume structure and sections
5. Tailoring strategies for this specific position
6. Quantifiable achievements to focus on
7. Professional summary points

Be specific and actionable. Focus on what makes this candidate stand out for this particular role."""

    plan_response = await llm.ainvoke(planning_prompt)
    plan_to_write_resume = plan_response.content

    print("Generated detailed resume plan using LLM.")
    return {"plan_to_write_resume": plan_to_write_resume}

  except Exception as e:
    print(f"Error planning resume with LLM: {e}")
    return {}


async def generate_resume_node(state: ResumeMakerState) -> Dict:
  """Use LLM to generate a structured, professional resume based on the plan."""
  try:
    file_manager = FileManager()
    contents = []
    for file_path in state.source_files:
      content = await file_manager.read_file_async(file_path)
      if content:
        contents.append(content)

    full_content = "\n\n---\n\n".join(contents)

    llm = get_resume_generation_model()

    # Generate resume prompt
    resume_prompt = f"""Based on the following source materials and the provided plan, generate a professional, structured resume.

Plan to follow:
{state.plan_to_write_resume}

Source Materials:
{full_content}

Job Target: {state.job_target or "General position"}

Generate a comprehensive, well-formatted resume that:
1. Uses professional language and formatting
2. Highlights relevant skills and experiences for the target role
3. Includes quantifiable achievements and metrics
4. Follows modern resume best practices
5. Is ATS-friendly with appropriate keywords
6. Has clear sections: Summary, Skills, Experience, Education, Projects (if relevant)
7. Uses bullet points for achievements and responsibilities
8. Is concise yet comprehensive

Format the resume in Markdown for clarity."""

    resume_response = await llm.ainvoke(resume_prompt)
    final_resume = resume_response.content

    print("Generated professional resume using LLM.")
    return {"final_resume": final_resume}

  except Exception as e:
    print(f"Error generating resume with LLM: {e}")
    return {}


async def save_resume_node(state: ResumeMakerState) -> None:
  """Save the generated resume to a file."""
  try:
    if state.final_resume:
      file_paths = FileStoragePaths()
      file_manager = FileManager()

      output_path = file_paths.get_resume_path(f"{state.user_id}_resume.md")
      result = await file_manager.write_file_async(output_path, state.final_resume)

      if result:
        print(f"✅ Resume saved to: {output_path}")
      else:
        print("❌ Failed to save resume")
  except Exception as e:
    print(f"Error saving resume: {e}")


async def update_user_resume_file_node(state: ResumeMakerState) -> Dict:
  """Updates the user's resume_file field with the path of the generated resume."""
  try:
    resume_path = f"{state.user_id}_resume.md"

    # Update the user's resume_file field (assuming user_id is available in state)
    if hasattr(state, "user_id") and state.user_id:
      update_user(state.user_id, resume_file=resume_path)
      print(f"✅ Updated user {state.user_id}'s resume_file to: {resume_path}")
    else:
      raise ValueError("User ID is required to update resume file.")

    return {"resume_file": resume_path}

  except Exception as e:
    print(f"Error updating user resume file: {e}")
    return {}
