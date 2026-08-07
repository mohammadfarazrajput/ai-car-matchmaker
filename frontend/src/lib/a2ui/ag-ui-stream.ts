import { A2UIFrame } from "./types";

export type AGUIEventType =
  | "RUN_STARTED"
  | "TEXT_MESSAGE_START"
  | "TEXT_MESSAGE_CONTENT"
  | "TEXT_MESSAGE_END"
  | "TOOL_CALL_START"
  | "TOOL_CALL_ARGS"
  | "TOOL_CALL_END"
  | "STATE_SNAPSHOT"
  | "STATE_DELTA"
  | "A2UI_FRAME"
  | "RUN_FINISHED"
  | "RUN_ERROR";

export interface AGUIEvent {
  type: AGUIEventType;
  sessionId?: string;
  messageId?: string;
  content?: string;
  toolName?: string;
  args?: string;
  state?: Record<string, unknown>;
  delta?: Record<string, unknown>;
  frame?: A2UIFrame;
  error?: string;
}

export function parseSSELine(line: string): AGUIEvent | null {
  const trimmed = line.trim();
  if (!trimmed || trimmed.startsWith(":")) return null;

  if (trimmed.startsWith("event:")) {
    const eventType = trimmed.slice(6).trim();
    return { type: eventType as AGUIEventType };
  }

  if (trimmed.startsWith("data:")) {
    const jsonStr = trimmed.slice(5).trim();
    if (!jsonStr) return null;

    try {
      const parsed = JSON.parse(jsonStr);

      if (parsed.type === "A2UI_FRAME" && parsed.frame) {
        return { type: "A2UI_FRAME", frame: parsed.frame };
      }

      return {
        type: (parsed.type || "unknown") as AGUIEventType,
        sessionId: parsed.session_id,
        messageId: parsed.message_id,
        content: parsed.content,
        toolName: parsed.tool_name,
        args: parsed.args,
        state: parsed.state,
        delta: parsed.delta,
        error: parsed.error,
      };
    } catch {
      return null;
    }
  }

  return null;
}

export interface AGUIStreamCallbacks {
  onEvent?: (event: AGUIEvent) => void;
  onText?: (text: string) => void;
  onFrame?: (frame: A2UIFrame) => void;
  onState?: (state: Record<string, unknown>) => void;
  onError?: (error: string) => void;
  onDone?: () => void;
}

export async function consumeAGUIStream(
  response: Response,
  callbacks: AGUIStreamCallbacks,
): Promise<void> {
  const reader = response.body?.getReader();
  if (!reader) throw new Error("No body on response");

  const decoder = new TextDecoder();
  let buffer = "";
  let currentEventType: AGUIEventType | null = null;

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";

      for (const line of lines) {
        if (line.startsWith("event:")) {
          currentEventType = line.slice(6).trim() as AGUIEventType;
          continue;
        }

        if (line.startsWith("data:")) {
          const jsonStr = line.slice(5).trim();
          if (!jsonStr) continue;

          try {
            const parsed = JSON.parse(jsonStr);
            const eventType = currentEventType ?? (parsed.type as AGUIEventType);
            currentEventType = null;

            const event: AGUIEvent = {
              type: eventType,
              sessionId: parsed.session_id,
              messageId: parsed.message_id,
              content: parsed.content,
              toolName: parsed.tool_name,
              args: parsed.args,
              state: parsed.state,
              delta: parsed.delta,
              frame: parsed.frame,
              error: parsed.error,
            };

            callbacks.onEvent?.(event);

            if (eventType === "A2UI_FRAME" && parsed.frame) {
              callbacks.onFrame?.(parsed.frame);
            }

            if (eventType === "TEXT_MESSAGE_CONTENT" && parsed.content) {
              callbacks.onText?.(parsed.content);
            }

            if (eventType === "STATE_SNAPSHOT" && parsed.state) {
              callbacks.onState?.(parsed.state);
            }

            if (eventType === "RUN_ERROR" && parsed.error) {
              callbacks.onError?.(parsed.error);
            }
          } catch {
            // skip malformed JSON
          }
        }
      }
    }

    callbacks.onDone?.();
  } finally {
    reader.releaseLock();
  }
}
