"use client";

import { CopilotKit } from "@copilotkit/react-core";
import { CopilotSidebar } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function CopilotKitProvider({ children }: { children: React.ReactNode }) {
  return (
    <CopilotKit runtimeUrl={`${API_URL}/agent`} publicApiKey="">
      <CopilotSidebar
        defaultOpen={true}
        labels={{
          title: "AI Car Matchmaker",
          initial:
            "Welcome! I'm your AI car matchmaker. Tell me what you're looking for — I'll help you find the perfect vehicle.",
        }}
      >
        {children}
      </CopilotSidebar>
    </CopilotKit>
  );
}
