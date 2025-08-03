import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useUser } from "../../contexts/UserContext";
import { findJobPostings } from "../../lib/api";
import { Button } from "../ui/button";

interface JobSearchProps {
	keyword?: string;
}

const JobSearch = ({ keyword }: JobSearchProps) => {
	const { selectedUserId } = useUser();
	const queryClient = useQueryClient();

	const mutation = useMutation({
		mutationFn: () => findJobPostings(selectedUserId as string, keyword),
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["jobPostings"] });
		},
	});

	return (
		<div className="p-4 border rounded">
			<h2 className="mb-2 text-lg font-bold">Find Jobs</h2>
			<Button
				onClick={() => mutation.mutate()}
				className="px-4 py-2 text-white bg-blue-500 rounded"
				disabled={mutation.isPending || !selectedUserId}
			>
				{mutation.isPending ? "Searching..." : "Find Jobs"}
			</Button>
			{mutation.isError && (
				<p className="mt-2 text-red-500">{mutation.error.message}</p>
			)}
		</div>
	);
};

export default JobSearch;
