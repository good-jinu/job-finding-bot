import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { saveUser } from "../../lib/api";

const AddUser = () => {
	const [userName, setUserName] = useState("");
	const queryClient = useQueryClient();

	const mutation = useMutation({
		mutationFn: saveUser,
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["users"] });
			setUserName("");
		},
	});

	const handleSubmit = (e: React.FormEvent) => {
		e.preventDefault();
		if (userName) {
			mutation.mutate(userName);
		}
	};

	return (
		<form
			onSubmit={handleSubmit}
			className="flex items-center gap-2 p-4 border rounded"
		>
			<Input
				type="text"
				value={userName}
				onChange={(e) => setUserName(e.target.value)}
				placeholder="Enter new user name"
				className="flex-grow"
			/>
			<Button type="submit" disabled={!userName || mutation.isPending}>
				{mutation.isPending ? "Adding..." : "Add User"}
			</Button>
			{mutation.isError && (
				<p className="mt-2 text-red-500">{mutation.error.message}</p>
			)}
		</form>
	);
};

export default AddUser;
