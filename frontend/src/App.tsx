import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { CookiesProvider } from "react-cookie";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import Dashboard from "./pages/Dashboard";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
	<QueryClientProvider client={queryClient}>
		<CookiesProvider>
			<TooltipProvider>
				<Toaster />
				<BrowserRouter>
					<Routes>
						<Route path="/" element={<Index />} />
						<Route path="/dashboard/*" element={<Dashboard />} />
						{/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
						<Route path="*" element={<NotFound />} />
					</Routes>
				</BrowserRouter>
			</TooltipProvider>
		</CookiesProvider>
	</QueryClientProvider>
);

export default App;
