"use client";

import React from "react";
import {
  A2UIComponent,
  DynamicValue,
  Action,
  TextComponent,
  ImageComponent,
  IconComponent,
  RowComponent,
  ColumnComponent,
  ListComponent,
  CardComponent,
  ButtonComponent,
  TextFieldComponent,
  ChoicePickerComponent,
  SliderComponent,
  DateTimeInputComponent,
} from "./types";
import { SurfaceState } from "./store";

function resolveValue(v: DynamicValue | undefined, dataModel: Record<string, unknown>): string {
  if (v === undefined || v === null) return "";
  if (typeof v === "string") return v;
  if (typeof v === "number" || typeof v === "boolean") return String(v);
  if (typeof v === "object" && "path" in v) {
    const parts = (v as { path: string }).path.split("/").filter(Boolean);
    let current: unknown = dataModel;
    for (const p of parts) {
      if (current == null || typeof current !== "object") return "";
      current = (current as Record<string, unknown>)[p];
    }
    return current != null ? String(current) : "";
  }
  if (typeof v === "object" && "call" in v) {
    const fn = v as { call: string; args: Record<string, unknown> };
    if (fn.call === "formatString" && fn.args.value) {
      const template = resolveValue(fn.args.value as DynamicValue, dataModel);
      return template.replace(/\$\{([^}]+)\}/g, (_match: string, expr: string) => {
        const trimmed = expr.trim();
        return resolveValue({ path: trimmed }, dataModel);
      });
    }
    return `[${fn.call}]`;
  }
  return String(v);
}

function resolveChildren(
  children: string[] | { path: string; componentId: string } | undefined,
  dataModel: Record<string, unknown>,
): string[] {
  if (!children) return [];
  if (Array.isArray(children)) return children;
  const items = resolveValue({ path: children.path }, dataModel);
  try {
    const arr = JSON.parse(items);
    if (Array.isArray(arr)) {
      return arr.map((_: unknown, i: number) => `${children.componentId}-${i}`);
    }
  } catch {
    // fall through
  }
  return [];
}

function renderComponent(
  comp: A2UIComponent,
  surface: SurfaceState,
  onAction?: (action: Action) => void,
): React.ReactNode {
  const { dataModel } = surface;

  switch (comp.component) {
    case "Text": {
      const c = comp as TextComponent;
      return (
        <span key={c.id} style={{ fontSize: c.variant === "caption" ? "0.8rem" : "1rem" }}>
          {resolveValue(c.text, dataModel)}
        </span>
      );
    }

    case "Image": {
      const c = comp as ImageComponent;
      const src = resolveValue(c.url, dataModel);
      const alt = resolveValue(c.description, dataModel);
      return <img key={c.id} src={src} alt={alt} style={{ maxWidth: "100%", borderRadius: 4 }} />;
    }

    case "Icon": {
      const c = comp as IconComponent;
      const name = typeof c.name === "string" ? c.name : "";
      return (
        <span key={c.id} aria-label={name}>
          &#9679;
        </span>
      );
    }

    case "Row": {
      const c = comp as RowComponent;
      const childIds = resolveChildren(c.children, dataModel);
      return (
        <div
          key={c.id}
          style={{
            display: "flex",
            flexDirection: "row",
            gap: "0.5rem",
            justifyContent: c.justify ?? "start",
            alignItems: c.align ?? "stretch",
          }}
        >
          {childIds.map((childId) => {
            const childComp = surface.components.get(childId);
            return childComp ? (
              <React.Fragment key={childId}>
                {renderComponent(childComp, surface, onAction)}
              </React.Fragment>
            ) : null;
          })}
        </div>
      );
    }

    case "Column": {
      const c = comp as ColumnComponent;
      const childIds = resolveChildren(c.children, dataModel);
      return (
        <div
          key={c.id}
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "0.5rem",
            justifyContent: c.justify ?? "start",
            alignItems: c.align ?? "stretch",
          }}
        >
          {childIds.map((childId) => {
            const childComp = surface.components.get(childId);
            return childComp ? (
              <React.Fragment key={childId}>
                {renderComponent(childComp, surface, onAction)}
              </React.Fragment>
            ) : null;
          })}
        </div>
      );
    }

    case "List": {
      const c = comp as ListComponent;
      const isHorizontal = c.direction === "horizontal";
      const childIds = resolveChildren(c.children, dataModel);

      if (
        childIds.length === 0 &&
        c.children &&
        typeof c.children === "object" &&
        "path" in c.children
      ) {
        const items = resolveValue({ path: c.children.path }, dataModel);
        try {
          const arr = JSON.parse(items);
          if (Array.isArray(arr)) {
            return (
              <div
                key={c.id}
                style={{
                  display: "flex",
                  flexDirection: isHorizontal ? "row" : "column",
                  gap: "0.5rem",
                  overflowX: isHorizontal ? "auto" : undefined,
                }}
              >
                {arr.map((item: Record<string, unknown>, i: number) => (
                  <div
                    key={i}
                    style={{
                      padding: "0.5rem 0.75rem",
                      background: "#f9f9f9",
                      borderRadius: 6,
                      fontSize: "0.85rem",
                    }}
                  >
                    {!!item.label && <div style={{ fontWeight: 500 }}>{String(item.label)}</div>}
                    {!!item.detail && (
                      <div style={{ color: "#666", fontSize: "0.8rem" }}>{String(item.detail)}</div>
                    )}
                  </div>
                ))}
              </div>
            );
          }
        } catch {
          // fall through
        }
      }

      return (
        <div
          key={c.id}
          style={{
            display: "flex",
            flexDirection: isHorizontal ? "row" : "column",
            gap: "0.5rem",
            overflowX: isHorizontal ? "auto" : undefined,
          }}
        >
          {childIds.map((childId) => {
            const childComp = surface.components.get(childId);
            return childComp ? (
              <React.Fragment key={childId}>
                {renderComponent(childComp, surface, onAction)}
              </React.Fragment>
            ) : null;
          })}
        </div>
      );
    }

    case "Card": {
      const c = comp as CardComponent;
      const title = c.title ? resolveValue(c.title, dataModel) : "";
      const subtitle = c.subtitle ? resolveValue(c.subtitle, dataModel) : "";
      const imageUrl = c.imageUrl ? resolveValue(c.imageUrl, dataModel) : "";
      const body = c.body ? resolveValue(c.body, dataModel) : "";
      const childComp = c.child ? surface.components.get(c.child) : null;

      if (title || subtitle || imageUrl || body) {
        return (
          <div
            key={c.id}
            onClick={() => c.action && onAction?.(c.action)}
            style={{
              border: "1px solid #e0e0e0",
              borderRadius: 8,
              overflow: "hidden",
              background: "#fff",
              boxShadow: "0 1px 3px rgba(0,0,0,0.08)",
              cursor: c.action ? "pointer" : "default",
            }}
          >
            {imageUrl && (
              <img
                src={imageUrl}
                alt={title}
                style={{ width: "100%", height: 160, objectFit: "cover" }}
              />
            )}
            <div style={{ padding: "0.75rem" }}>
              {title && (
                <div style={{ fontWeight: 600, fontSize: "0.95rem", marginBottom: "0.25rem" }}>
                  {title}
                </div>
              )}
              {subtitle && (
                <div style={{ fontSize: "0.8rem", color: "#666", marginBottom: "0.5rem" }}>
                  {subtitle}
                </div>
              )}
              {body && (
                <div style={{ fontSize: "0.85rem", color: "#444", lineHeight: 1.5 }}>{body}</div>
              )}
            </div>
          </div>
        );
      }

      return (
        <div
          key={c.id}
          style={{
            border: "1px solid #e0e0e0",
            borderRadius: 8,
            padding: "1rem",
            background: "#fff",
            boxShadow: "0 1px 3px rgba(0,0,0,0.08)",
          }}
        >
          {childComp ? renderComponent(childComp, surface, onAction) : null}
        </div>
      );
    }

    case "Button": {
      const c = comp as ButtonComponent;
      let label = c.label ? resolveValue(c.label, dataModel) : "";
      if (!label && c.child) {
        const childComp = surface.components.get(c.child);
        if (childComp && childComp.component === "Text") {
          label = resolveValue((childComp as TextComponent).text, dataModel);
        }
      }
      if (!label) label = "Button";
      return (
        <button
          key={c.id}
          onClick={() => c.action && onAction?.(c.action)}
          style={{
            padding: "0.5rem 1rem",
            borderRadius: 6,
            border: c.variant === "primary" ? "none" : "1px solid #ccc",
            background:
              c.variant === "primary"
                ? "#1a1a1a"
                : c.variant === "borderless"
                  ? "transparent"
                  : "#f5f5f5",
            color: c.variant === "primary" ? "#fff" : "#1a1a1a",
            cursor: "pointer",
            fontWeight: c.variant === "primary" ? 600 : 400,
          }}
        >
          {label}
        </button>
      );
    }

    case "TextField": {
      const c = comp as TextFieldComponent;
      return (
        <div key={c.id} style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
          <label style={{ fontSize: "0.85rem", fontWeight: 500 }}>
            {resolveValue(c.label, dataModel)}
          </label>
          <input
            type={
              c.variant === "number" ? "number" : c.variant === "obscured" ? "password" : "text"
            }
            placeholder={resolveValue(c.placeholder, dataModel)}
            defaultValue={resolveValue(c.value, dataModel)}
            style={{
              padding: "0.5rem",
              borderRadius: 4,
              border: "1px solid #ccc",
              fontSize: "0.9rem",
            }}
          />
        </div>
      );
    }

    case "ChoicePicker": {
      const c = comp as ChoicePickerComponent;
      return (
        <div key={c.id} style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
          {c.label && (
            <label style={{ fontSize: "0.85rem", fontWeight: 500 }}>
              {resolveValue(c.label, dataModel)}
            </label>
          )}
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
            {c.options.map((opt) => (
              <button
                key={opt.value}
                onClick={() => c.action && onAction?.(c.action)}
                style={{
                  padding: "0.4rem 0.8rem",
                  borderRadius: 20,
                  border: "1px solid #ccc",
                  background: "#f5f5f5",
                  cursor: "pointer",
                  fontSize: "0.85rem",
                }}
              >
                {resolveValue(opt.label, dataModel)}
              </button>
            ))}
          </div>
        </div>
      );
    }

    case "Slider": {
      const c = comp as SliderComponent;
      return (
        <div key={c.id} style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
          {c.label && (
            <label style={{ fontSize: "0.85rem", fontWeight: 500 }}>
              {resolveValue(c.label, dataModel)}
            </label>
          )}
          <input
            type="range"
            min={c.min ?? 0}
            max={c.max}
            step={c.steps}
            style={{ width: "100%" }}
          />
        </div>
      );
    }

    case "DateTimeInput": {
      const c = comp as DateTimeInputComponent;
      return (
        <div key={c.id} style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
          {c.label && (
            <label style={{ fontSize: "0.85rem", fontWeight: 500 }}>
              {resolveValue(c.label, dataModel)}
            </label>
          )}
          <input
            type={c.enableDate !== false ? "date" : "time"}
            style={{ padding: "0.5rem", borderRadius: 4, border: "1px solid #ccc" }}
          />
        </div>
      );
    }

    case "Divider": {
      return (
        <hr
          key={comp.id}
          style={{ border: "none", borderTop: "1px solid #e0e0e0", margin: "0.5rem 0" }}
        />
      );
    }

    default:
      return (
        <div key={comp.id} style={{ padding: "0.25rem", color: "#999", fontSize: "0.8rem" }}>
          [{comp.component}]
        </div>
      );
  }
}

export function SurfaceRenderer({
  surface,
  onAction,
}: {
  surface: SurfaceState;
  onAction?: (action: Action) => void;
}) {
  const root = surface.components.get("root");
  if (!root) {
    const first = Array.from(surface.components.values())[0];
    if (!first) return null;
    return <>{renderComponent(first, surface, onAction)}</>;
  }
  return <>{renderComponent(root, surface, onAction)}</>;
}

export { resolveValue };
