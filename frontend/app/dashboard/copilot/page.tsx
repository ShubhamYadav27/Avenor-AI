import { Metadata } from "next";
import { CopilotChatWindow } from "@/components/copilot/CopilotChatWindow";

export const metadata: Metadata = {
  title: "AI Revenue Copilot | Avenor Intelligence Platform",
  description:
    "Primary executive interface orchestrating predictive revenue intelligence, high-intent buying signals, CRM deal pipeline, and outreach strategies.",
};

export default function CopilotPage() {
  return (
    <div className="p-4 md:p-6 h-full">
      <CopilotChatWindow />
    </div>
  );
}
