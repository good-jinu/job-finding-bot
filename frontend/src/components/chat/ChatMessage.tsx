import { Bot, User } from "lucide-react";
import ReactMarkdown from "react-markdown";

interface ChatMessageProps {
	content: string;
	role: "user" | "assistant";
	timestamp: Date;
}

const ChatMessage = ({ content, role, timestamp }: ChatMessageProps) => {
	return (
		<div
			className={`flex ${role === "user" ? "justify-end" : "justify-start"}`}
		>
			<div
				className={`flex max-w-[85%] ${role === "user" ? "flex-row-reverse" : ""}`}
			>
				<div
					className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${role === "user" ? "bg-blue-500 ml-2" : "bg-green-500 mr-2"}`}
				>
					{role === "user" ? (
						<User className="w-4 h-4 text-white" />
					) : (
						<Bot className="w-4 h-4 text-white" />
					)}
				</div>
				<div
					className={`rounded-lg px-4 py-2 ${role === "user" ? "bg-blue-500 text-white" : "bg-gray-100"}`}
				>
					<ReactMarkdown
						components={{
							p: ({ node, ...props }) => (
								<p className="mb-2 last:mb-0" {...props} />
							),
							ul: ({ node, ...props }) => (
								<ul className="list-disc pl-5 mb-2" {...props} />
							),
							ol: ({ node, ...props }) => (
								<ol className="list-decimal pl-5 mb-2" {...props} />
							),
							li: ({ node, ...props }) => <li className="mb-1" {...props} />,
							strong: ({ node, ...props }) => (
								<strong className="font-semibold" {...props} />
							),
							em: ({ node, ...props }) => <em className="italic" {...props} />,
						}}
					>
						{content}
					</ReactMarkdown>
					<div
						className={`text-xs mt-1 ${role === "user" ? "text-blue-100" : "text-gray-500"}`}
					>
						{timestamp.toLocaleTimeString([], {
							hour: "2-digit",
							minute: "2-digit",
						})}
					</div>
				</div>
			</div>
		</div>
	);
};

export default ChatMessage;
