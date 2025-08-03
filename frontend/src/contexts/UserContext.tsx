import { createContext, type ReactNode, useContext, useState } from "react";

interface UserContextType {
	selectedUserId: string | null;
	setSelectedUserId: (userId: string | null) => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider = ({ children }: { children: ReactNode }) => {
	const [selectedUserId, setSelectedUserId] = useState<string | null>(null);

	return (
		<UserContext.Provider value={{ selectedUserId, setSelectedUserId }}>
			{children}
		</UserContext.Provider>
	);
};

export const useUser = () => {
	const context = useContext(UserContext);
	if (context === undefined) {
		throw new Error("useUser must be used within a UserProvider");
	}
	return context;
};
