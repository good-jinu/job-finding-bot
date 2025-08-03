import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useUser } from "../../contexts/UserContext";
import { uploadResumeSource } from "../../lib/api";
import { Button } from "../ui/button";
import { Input } from "../ui/input";

const UploadResume = () => {
	const { selectedUserId } = useUser();
	const queryClient = useQueryClient();
	const [file, setFile] = useState<File | null>(null);

	const mutation = useMutation({
		mutationFn: (file: File) =>
			uploadResumeSource(selectedUserId as string, file),
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: ["resumeSources", selectedUserId],
			});
		},
	});

	const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
		if (e.target.files) {
			setFile(e.target.files[0]);
		}
	};

	const handleSubmit = (e: React.FormEvent) => {
		e.preventDefault();
		if (file && selectedUserId) {
			mutation.mutate(file);
		}
	};

	return (
		<form onSubmit={handleSubmit} className="p-4 border rounded">
			<h2 className="mb-2 text-lg font-bold">Upload Resume</h2>
			<Input type="file" onChange={handleFileChange} className="mb-2" />
			<Button
				type="submit"
				className="px-4 py-2 text-white bg-blue-500 rounded"
				disabled={!file || mutation.isPending || !selectedUserId}
			>
				{mutation.isPending ? "Uploading..." : "Upload"}
			</Button>
			{mutation.isError && (
				<p className="mt-2 text-red-500">{mutation.error.message}</p>
			)}
		</form>
	);
};

export default UploadResume;
