import { useMutation } from "@tanstack/react-query";
import { useUser } from "../../contexts/UserContext";
import { analyzeJobAndResume } from "../../lib/api";

const JobAnalysis = () => {
	const { selectedUserId } = useUser();

	const mutation = useMutation({
		mutationFn: () => {
			if (!selectedUserId) {
				throw new Error("User not selected for job analysis.");
			}
			return analyzeJobAndResume(selectedUserId);
		},
	});

	// This component is simplified. You would typically trigger the mutation
	// from the JobPostingList component and display the results here.

	if (!selectedUserId) return null;

	return (
		<div className="p-4 border rounded">
			<h2 className="mb-2 text-lg font-bold">Job Analysis</h2>
			{mutation.isPending && <p>Analyzing...</p>}
			{mutation.isError && <p>Error: {mutation.error.message}</p>}
			{mutation.data && <pre>{JSON.stringify(mutation.data, null, 2)}</pre>}
		</div>
	);
};

export default JobAnalysis;
