# Job Finding Bot

This project is a web application that helps users find jobs, analyze job postings, and create tailored resumes.

## Features

- **User Management**: Create and manage users.
- **Resume Management**: Upload and store multiple resume sources for each user.
- **Job Search**: Search for job postings from various sources using a specified keyword.
- **Job Analysis**: Analyze how well a user's resume matches a job posting.
- **Resume Maker**: Generate a new resume tailored to a specific job target based on a provided keyword.

## Tech Stack

- **Backend**: Python with FastAPI
- **Frontend**: React with TypeScript and Vite
- **Database**: SQLite

## Project Structure

The project is divided into two main parts: the backend and the frontend.

### Backend (`src`)

The backend is a FastAPI application that provides a REST API for the frontend. The core logic is organized into the following modules:

- `src/api`: Defines the API endpoints.
- `src/core/database`: Manages the SQLite database.
- `src/core/services`: Contains the business logic for the core features:
    - `job_analysis`: Analyzes job postings against resumes.
    - `job_search`: Searches for job postings.
    - `resume_maker`: Creates new resumes.
- `src/core/schemas`: Defines the data models used in the application.

### Frontend (`frontend`)

The frontend is a React application built with Vite. It provides a user interface for interacting with the backend API. The main components are:

- `frontend/src/pages/Dashboard.tsx`: The main dashboard where users can access all the features.
- `frontend/src/components/dashboard`: Contains the components for each feature, such as `JobSearch.tsx`, `ResumeMaker.tsx`, etc.

## How to Use

### Backend

1. **Install dependencies**:

   ```bash
   uv add fastapi uvicorn[standard] aiofiles python-multipart
   ```

2. **Start the backend server**:

   ```bash
   uv run python -m src.api.main
   ```

### Frontend

1. **Install dependencies**:

   ```bash
   cd frontend
   npm install
   ```

2. **Start the frontend development server**:

   ```bash
   npm run dev
   ```

3. **Open the application in your browser** at `http://localhost:5173`.

4. **Add a new user** using the "Add User" form.

5. **Select a user** from the list to view their data.

6. **Upload resume sources** for the selected user.

7. **Find job postings** by providing a keyword and using the "Find Jobs" button.

8. **Analyze a job posting** by clicking the "Analyze" button next to it.

9. **Create a new resume** by providing a job target keyword using the "Make Resume" form.