import { Bot, Send } from "lucide-react";
import type React from "react";
import { useEffect, useRef, useState } from "react";
import ChatMessage from "@/components/chat/ChatMessage";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";

interface Message {
	id: string;
	content: string;
	role: "user" | "assistant";
	timestamp: Date;
}

const ChatInterface = () => {
	const [messages, setMessages] = useState<Message[]>([
		{
			id: "1",
			content:
				"Hello! I'm your job finding assistant. I can help you search for jobs, analyze job postings against your resume, and create tailored resumes. What would you like to do today?",
			role: "assistant",
			timestamp: new Date(),
		},
	]);
	const [input, setInput] = useState("");
	const [isLoading, setIsLoading] = useState(false);
	const scrollAreaRef = useRef<HTMLDivElement>(null);

	useEffect(() => {
		if (scrollAreaRef.current) {
			scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
		}
	});

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		if (!input.trim() || isLoading) return;

		// Add user message
		const userMessage: Message = {
			id: Date.now().toString(),
			content: input,
			role: "user",
			timestamp: new Date(),
		};

		setMessages((prev) => [...prev, userMessage]);
		setInput("");
		setIsLoading(true);

		// Simulate bot response
		setTimeout(() => {
			const botMessage: Message = {
				id: (Date.now() + 1).toString(),
				content: `I understand you're looking for help with "${input}". I can assist with job searches, resume analysis, and creating tailored applications. What specific information would you like me to help with?`,
				role: "assistant",
				timestamp: new Date(),
			};
			setMessages((prev) => [...prev, botMessage]);
			setIsLoading(false);
		}, 1000);
	};

	return (
		<Card className="w-full max-w-4xl mx-auto h-[70vh] flex flex-col">
			<CardContent className="p-0 flex flex-col h-full">
				<div className="p-4 border-b">
					<h2 className="text-xl font-bold">Job Finding Assistant</h2>
					<p className="text-sm text-muted-foreground">
						Your AI-powered career companion
					</p>
				</div>

				<ScrollArea className="flex-grow p-4" ref={scrollAreaRef}>
					<div className="space-y-4">
						{messages.map((message) => (
							<ChatMessage
								key={message.id}
								content={message.content}
								role={message.role}
								timestamp={message.timestamp}
							/>
						))}
						{isLoading && (
							<div className="flex justify-start">
								<div className="flex">
									<div className="flex-shrink-0 w-8 h-8 rounded-full bg-green-500 mr-2 flex items-center justify-center">
										<Bot className="w-4 h-4 text-white" />
									</div>
									<div className="bg-gray-100 rounded-lg px-4 py-2">
										<div className="flex space-x-2">
											<div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce"></div>
											<div
												className="w-2 h-2 rounded-full bg-gray-400 animate-bounce"
												style={{ animationDelay: "0.2s" }}
											></div>
											<div
												className="w-2 h-2 rounded-full bg-gray-400 animate-bounce"
												style={{ animationDelay: "0.4s" }}
											></div>
										</div>
									</div>
								</div>
							</div>
						)}
					</div>
				</ScrollArea>

				<form onSubmit={handleSubmit} className="p-4 border-t">
					<div className="flex gap-2">
						<Input
							value={input}
							onChange={(e) => setInput(e.target.value)}
							placeholder="Ask about jobs, resumes, or career advice..."
							className="flex-grow"
							disabled={isLoading}
						/>
						<Button type="submit" disabled={isLoading || !input.trim()}>
							<Send className="w-4 h-4" />
						</Button>
					</div>
				</form>
			</CardContent>
		</Card>
	);
};

export default ChatInterface;
