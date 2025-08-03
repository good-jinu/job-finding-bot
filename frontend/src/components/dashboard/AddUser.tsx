import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogFooter,
	DialogHeader,
	DialogTitle,
	DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { saveUser } from "../../lib/api";

interface AddUserProps {
	onUserAdded: () => void;
}

const AddUser = ({ onUserAdded }: AddUserProps) => {
	const [userName, setUserName] = useState("");
	const [open, setOpen] = useState(false);
	const queryClient = useQueryClient();

	const mutation = useMutation({
		mutationFn: saveUser,
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["users"] });
			setUserName("");
			setOpen(false); // Close the dialog on success
			onUserAdded();
		},
	});

	const handleSubmit = (e: React.FormEvent) => {
		e.preventDefault();
		if (userName) {
			mutation.mutate(userName);
		}
	};

	return (
		<Dialog open={open} onOpenChange={setOpen}>
			<DialogTrigger asChild>
				<Button className="w-full">Add New User</Button>
			</DialogTrigger>
			<DialogContent className="sm:max-w-[425px]">
				<DialogHeader>
					<DialogTitle>Add New User</DialogTitle>
					<DialogDescription>
						Enter a name for the new user. This will create a new profile.
					</DialogDescription>
				</DialogHeader>
				<form onSubmit={handleSubmit} className="grid gap-4 py-4">
					<Input
						id="name"
						type="text"
						value={userName}
						onChange={(e) => setUserName(e.target.value)}
						placeholder="User Name"
						className="col-span-3"
					/>
				</form>
				<DialogFooter>
					<Button
						type="submit"
						onClick={handleSubmit}
						disabled={!userName || mutation.isPending}
					>
						{mutation.isPending ? "Adding..." : "Add User"}
					</Button>
				</DialogFooter>
				{mutation.isError && (
					<p className="text-red-500 text-sm mt-2">
						Error: {mutation.error.message}
					</p>
				)}
			</DialogContent>
		</Dialog>
	);
};

export default AddUser;
