import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App";

// Render the App component into the root element
const rootElement = document.getElementById("root");
if (rootElement) {
	createRoot(rootElement).render(<StrictMode><App /></StrictMode>);
}
