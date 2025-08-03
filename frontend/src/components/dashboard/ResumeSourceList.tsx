import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import {
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow,
} from "@/components/ui/table";
import { useUser } from "../../contexts/UserContext";
import {
	downloadResumeSource,
	getResumeSources,
	type ResumeSource,
	removeResumeSource,
} from "../../lib/api";

const ResumeSourceList = () => {
	const { selectedUserId } = useUser();
	const queryClient = useQueryClient();

	const { data, error, isLoading } = useQuery({
		queryKey: ["resumeSources", selectedUserId],
		queryFn: () => {
			if (!selectedUserId) {
				throw new Error("User not selected for resume sources.");
			}
			return getResumeSources(selectedUserId);
		},
		enabled: !!selectedUserId,
	});

	const mutation = useMutation({
		mutationFn: (resumeSourceId: number) => {
			if (!selectedUserId) {
				throw new Error("User not selected for removing resume source.");
			}
			return removeResumeSource(selectedUserId, resumeSourceId);
		},
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: ["resumeSources", selectedUserId],
			});
		},
	});

	if (!selectedUserId) return null;
	if (isLoading) return <p>Loading resume sources...</p>;
	if (error) return <p>Error loading resume sources: {error.message}</p>;

	return (
		<div className="p-4 border rounded">
			<h2 className="mb-2 text-lg font-bold">Resume Sources</h2>
			<Table>
				<TableHeader>
					<TableRow>
						<TableHead>File Name</TableHead>
						<TableHead className="text-right">Actions</TableHead>
					</TableRow>
				</TableHeader>
				<TableBody>
					{data?.map((source: ResumeSource) => (
						<TableRow key={source.id}>
							<TableCell>{source.original_file_name}</TableCell>
							<TableCell className="text-right">
								<Button
									variant="destructive"
									size="sm"
									onClick={() => mutation.mutate(source.id as number)}
									disabled={mutation.isPending}
									className="mr-2"
								>
									Delete
								</Button>
								<Button
									variant="outline"
									size="sm"
									onClick={() =>
										downloadResumeSource(
											selectedUserId,
											source.id as number,
											source.original_file_name,
										)
									}
								>
									Download
								</Button>
							</TableCell>
						</TableRow>
					))}
				</TableBody>
			</Table>
		</div>
	);
};

export default ResumeSourceList;
