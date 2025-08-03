import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
});

export const uploadResumeSource = async (userId: string, file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await apiClient.post(`/users/${userId}/resume-sources`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getResumeSources = async (userId: string) => {
  const response = await apiClient.get(`/users/${userId}/resume-sources`);
  return response.data;
};


export const getResumeSourceContent = async (userId: string, resumeSourceId: number) => {
  const response = await apiClient.get(`/api/users/${userId}/resume-sources/${resumeSourceId}/content`);
  return response.data;
};

export const makeResume = async (userId: string, jobTarget: string) => {
  const response = await apiClient.post(`/users/${userId}/resumes`, { job_target: jobTarget });
  return response.data;
};

export const findJobPostings = async (userId: string) => {
  const response = await apiClient.post(`/users/${userId}/job-postings`);
  return response.data;
};

export const getJobPostings = async (limit: number = 10) => {
  const response = await apiClient.get(`/job-postings?limit=${limit}`);
  return response.data;
};

export const analyzeJobAndResume = async (userId: string) => {
  const response = await apiClient.post(`/users/${userId}/analyze-job`);
  return response.data;
};
