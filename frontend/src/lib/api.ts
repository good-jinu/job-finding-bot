import axios from "axios";

const apiClient = axios.create({
	baseURL: "http://localhost:8000",
});

export interface User {
	id: string;
	name: string;
	resume_file: string | null;
	created_at: string;
}

export interface JobPosting {
	id?: number;
	title: string;
	company?: string;
	location?: string;
	description?: string;
	posted_at?: string;
	url?: string;
	content_doc?: string;
}

export interface ResumeSource {
	id?: number;
	user_id: string;
	source_file_name: string;
	original_file_name: string;
}

export const get_all_users = async (): Promise<User[]> => {
	const response = await apiClient.get("/users");
	return response.data;
};

export const get_user_by_id = async (userId: string): Promise<User> => {
	const response = await apiClient.get(`/users/${userId}`);
	return response.data;
};

export const get_resume_sources_by_user = async (userId: string) => {
	const response = await apiClient.get(`/users/${userId}/resume-sources`);
	return response.data;
};

export const get_latest_job_postings = async (limit: number = 10) => {
	const response = await apiClient.get(`/job-postings?limit=${limit}`);
	return response.data;
};

export const uploadResumeSource = async (userId: string, file: File) => {
	const formData = new FormData();
	formData.append("file", file);
	const response = await apiClient.post(
		`/users/${userId}/resume-sources`,
		formData,
		{
			headers: {
				"Content-Type": "multipart/form-data",
			},
		},
	);
	return response.data;
};

export const getResumeSources = async (userId: string) => {
	const response = await apiClient.get(`/users/${userId}/resume-sources`);
	return response.data;
};

export const getResumeSourceContent = async (
	userId: string,
	resumeSourceId: number,
) => {
	const response = await apiClient.get(
		`/api/users/${userId}/resume-sources/${resumeSourceId}/content`,
	);
	return response.data;
};

export const makeResume = async (userId: string, jobTarget: string) => {
	const response = await apiClient.post(
		`/users/${userId}/${jobTarget}/resumes`,
	);
	return response.data;
};

export const findJobPostings = async (userId: string, keyword?: string) => {
	const response = await apiClient.post(
		`/users/${userId}/job-postings`,
		{},
		{ params: { keyword } },
	);
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

export const saveUser = async (userName: string) => {
	const response = await apiClient.post("/users", { name: userName });
	return response.data;
};

export const removeResumeSource = async (
	userId: string,
	resumeSourceId: number,
) => {
	const response = await apiClient.delete(
		`/users/${userId}/resume-sources/${resumeSourceId}`,
	);
	return response.data;
};

export const downloadResumeSource = async (
	userId: string,
	resumeSourceId: number,
	originalFileName: string,
) => {
	const response = await apiClient.get(
		`/users/${userId}/resume-sources/${resumeSourceId}/download`,
		{
			responseType: "blob", // Important for downloading files
		},
	);
	const url = window.URL.createObjectURL(new Blob([response.data]));
	const link = document.createElement("a");
	link.href = url;
	link.setAttribute("download", originalFileName);
	document.body.appendChild(link);
	link.click();
	link.remove();
	window.URL.revokeObjectURL(url);
};
