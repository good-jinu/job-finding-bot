import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { useUser } from "../../contexts/UserContext";
import { makeResume } from "../../lib/api";
import { Button } from "../ui/button";
import { Input } from "../ui/input";

const ResumeMaker = () => {
	const { selectedUserId } = useUser();
	const [jobTarget, setJobTarget] = useState("");

	const mutation = useMutation({
		mutationFn: (jobTarget: string) =>
			makeResume(selectedUserId as string, jobTarget),
	});

	const handleSubmit = (e: React.FormEvent) => {
		e.preventDefault();
		if (jobTarget && selectedUserId) {
			mutation.mutate(jobTarget);
		}
	};

	return (
		<form onSubmit={handleSubmit} className="p-4 border rounded">
			<h2 className="mb-2 text-lg font-bold">Make Resume</h2>
			<Input
				type="text"
				value={jobTarget}
				onChange={(e) => setJobTarget(e.target.value)}
				placeholder="Enter job target"
				className="w-full px-3 py-2 mb-2 border rounded"
			/>
			<Button
				type="submit"
				className="px-4 py-2 text-white bg-blue-500 rounded"
				disabled={!jobTarget || mutation.isPending || !selectedUserId}
			>
				{mutation.isPending ? "Making..." : "Make Resume"}
			</Button>
			{mutation.isError && (
				<p className="mt-2 text-red-500">{mutation.error.message}</p>
			)}
			{mutation.data && (
				<div className="mt-2">
					<p>Resume created successfully!</p>
					<a
						href={mutation.data.resume_path}
						download
						className="text-blue-500"
					>
						Download Resume
					</a>
				</div>
			)}
		</form>
	);
};

export default ResumeMaker;
