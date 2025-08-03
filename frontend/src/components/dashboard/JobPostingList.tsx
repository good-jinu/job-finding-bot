import { useMutation, useQuery } from "@tanstack/react-query";
import { useUser } from "../../contexts/UserContext";
import {
	analyzeJobAndResume,
	getJobPostings,
	type JobPosting,
} from "../../lib/api";

const JobPostingList = () => {
	const { selectedUserId } = useUser();

	const { data, error, isLoading } = useQuery({
		queryKey: ["jobPostings", selectedUserId],
		queryFn: () => getJobPostings(),
		enabled: !!selectedUserId,
	});

	const mutation = useMutation({
		mutationFn: () => {
			if (!selectedUserId) {
				throw new Error("User not selected for job posting analysis.");
			}
			return analyzeJobAndResume(selectedUserId);
		},
	});

	if (!selectedUserId) return null;
	if (isLoading) return <p>Loading job postings...</p>;
	if (error) return <p>Error loading job postings: {error.message}</p>;

	return (
		<div className="p-4 border rounded">
			<h2 className="mb-2 text-lg font-bold">Job Postings</h2>
			<ul>
				{data?.map((job: JobPosting) => (
					<li key={job.id} className="mb-2">
						<h3 className="font-bold">{job.title}</h3>
						<p>{job.company}</p>
						<button
							type="button"
							onClick={() => mutation.mutate()}
							className="px-2 py-1 text-sm text-white bg-green-500 rounded"
							disabled={mutation.isPending}
						>
							{mutation.isPending ? "Analyzing..." : "Analyze"}
						</button>
					</li>
				))}
			</ul>
		</div>
	);
};

export default JobPostingList;
