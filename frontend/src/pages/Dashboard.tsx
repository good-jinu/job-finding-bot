import { useEffect, useState } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { get_all_users, type User } from "@/lib/api";
import AddUser from "../components/dashboard/AddUser";
import JobAnalysis from "../components/dashboard/JobAnalysis";
import JobPostingList from "../components/dashboard/JobPostingList";
import JobSearch from "../components/dashboard/JobSearch";
import ResumeMaker from "../components/dashboard/ResumeMaker";
import ResumeSourceList from "../components/dashboard/ResumeSourceList";
import UploadResume from "../components/dashboard/UploadResume";
import { useUser } from "../contexts/UserContext";

const Dashboard = () => {
	const [users, setUsers] = useState<User[]>([]);
	const { selectedUserId, setSelectedUserId } = useUser();

	useEffect(() => {
		get_all_users().then(setUsers);
	}, []);

	return (
		<div className="flex h-screen">
			<div className="w-1/4 p-4 space-y-4 overflow-y-auto border-r">
				<AddUser />
				<h2 className="text-xl font-bold">Users</h2>
				<ScrollArea className="h-48">
					<ul>
						{users.map((user) => (
							<button
								key={user.id}
								type="button"
								onClick={() => setSelectedUserId(user.id)}
								className={`cursor-pointer p-2 w-full text-left ${selectedUserId === user.id ? "bg-gray-200" : ""}`}
							>
								{user.name}
							</button>
						))}
					</ul>
				</ScrollArea>
				{selectedUserId && (
					<>
						<UploadResume />
						<ResumeSourceList />
						<JobSearch />
						<ResumeMaker />
					</>
				)}
			</div>
			<div className="flex-1 p-4 overflow-y-auto">
				{selectedUserId && (
					<>
						<JobPostingList />
						<JobAnalysis />
					</>
				)}
			</div>
		</div>
	);
};

export default Dashboard;
