import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
	Sidebar,
	SidebarContent,
	SidebarFooter,
	SidebarHeader,
	SidebarInset,
	SidebarMenu,
	SidebarMenuButton,
	SidebarMenuItem,
	SidebarProvider,
} from "@/components/ui/sidebar";
import {
	findJobPostings,
	get_all_users,
	makeResume,
	type User,
} from "@/lib/api";

import AddUser from "../components/dashboard/AddUser";
import JobAnalysis from "../components/dashboard/JobAnalysis";
import JobPostingList from "../components/dashboard/JobPostingList";
import ResumeSourceList from "../components/dashboard/ResumeSourceList";
import UploadResume from "../components/dashboard/UploadResume";
import { useUser } from "../contexts/UserContext";

const Dashboard = () => {
	const [users, setUsers] = useState<User[]>([]);
	const { selectedUserId, setSelectedUserId } = useUser();
	const [progress, setProgress] = useState(0);
	const [isProcessing, setIsProcessing] = useState(false);
	const [generatedResumePath, setGeneratedResumePath] = useState<string | null>(
		null,
	);
	const [jobTarget, setJobTarget] = useState<string>("");

	useEffect(() => {
		get_all_users().then(setUsers);
	}, []);

	const handleStartProcessing = async () => {
		if (!selectedUserId || !jobTarget) return;

		setIsProcessing(true);
		setProgress(0);
		setGeneratedResumePath(null);

		try {
			// Step 1: Make Resume
			setProgress(20);
			const resumeResult = await makeResume(selectedUserId, jobTarget);
			setGeneratedResumePath(resumeResult.resume_path);
			setProgress(50);

			// Step 2: Find Job Postings
			await findJobPostings(selectedUserId);
			setProgress(80);

			// Step 3: Job Analysis (if needed, or integrate into JobPostingList)
			// await analyzeJobAndResume(selectedUserId);
			setProgress(100);
		} catch (error) {
			console.error("Processing failed:", error);
			setProgress(0); // Reset on error
		} finally {
			setIsProcessing(false);
		}
	};

	return (
		<SidebarProvider defaultOpen={true}>
			<Sidebar>
				<SidebarHeader>
					<h2 className="text-xl font-bold">Users</h2>
				</SidebarHeader>
				<SidebarContent>
					<ScrollArea className="h-48">
						<SidebarMenu>
							{users.map((user) => (
								<SidebarMenuItem key={user.id}>
									<SidebarMenuButton
										onClick={() => setSelectedUserId(user.id)}
										isActive={selectedUserId === user.id}
									>
										{user.name}
									</SidebarMenuButton>
								</SidebarMenuItem>
							))}
						</SidebarMenu>
					</ScrollArea>
				</SidebarContent>
				<SidebarFooter>
					<AddUser onUserAdded={() => get_all_users().then(setUsers)} />
				</SidebarFooter>
			</Sidebar>
			<SidebarInset>
				<div className="p-4 space-y-4">
					<h1 className="text-4xl font-bold">Welcome to JobFinder AI</h1>
					<p className="text-lg text-gray-600">
						Select a user from the sidebar to get started, or add a new one.
					</p>

					{selectedUserId && (
						<>
							<div className="flex flex-col gap-4">
								<UploadResume />
								<ResumeSourceList />
								<div className="flex flex-col gap-2">
									<label htmlFor="jobTarget" className="text-lg font-medium">
										Target Job Keyword:
									</label>
									<Input
										id="jobTarget"
										type="text"
										value={jobTarget}
										onChange={(e) => setJobTarget(e.target.value)}
										placeholder="e.g., Software Engineer, Data Scientist"
									/>
								</div>
								<Button
									onClick={handleStartProcessing}
									disabled={isProcessing}
									className="text-2xl py-6"
								>
									{isProcessing
										? "Processing..."
										: "Start Job Search & Resume Generation"}
								</Button>
								{isProcessing && (
									<Progress value={progress} className="w-full" />
								)}
								{generatedResumePath && (
									<div className="mt-4">
										<h3 className="text-xl font-bold">Generated Resume:</h3>
										<a
											href={generatedResumePath}
											download
											className="text-blue-500 underline"
										>
											Download Your Tailored Resume
										</a>
									</div>
								)}
							</div>
							<JobPostingList />
							<JobAnalysis />
						</>
					)}
				</div>
			</SidebarInset>
		</SidebarProvider>
	);
};

export default Dashboard;
