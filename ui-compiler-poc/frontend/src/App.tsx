import React, { useCallback, useMemo, useState } from "react";
import {
  Alert,
  Button,
  Card,
  ConfigProvider,
  Form,
  Input,
  InputNumber,
  Row,
  Col,
  Space,
  Typography,
  message,
} from "antd";

type DerivedMap = Record<string, unknown>;

function safeEvalExpr(
  expr: string,
  ctx: { state: Record<string, unknown>; derived: DerivedMap }
): unknown {
  try {
    // Minimal safety: disallow obvious dangerous tokens / statements.
    const forbidden = [
      "function",
      "=>",
      "while",
      "for",
      "class",
      "new ",
      "this",
      "window",
      "document",
      "globalThis",
      "eval",
      "Function",
      "constructor",
      "import",
      "export",
      "require",
      ";",
      "{",
      "}",
    ];
    const lowered = expr.toLowerCase();
    for (const t of forbidden) {
      if (lowered.includes(t.trim().toLowerCase())) {
        return `{{${expr}}}`;
      }
    }

    // Allow only references to state.* and derived.* plus literals/operators.
    // If other identifiers exist, bail.
    const stripped = expr
      .replace(/'[^']*'/g, "''")
      .replace(/"[^"]*"/g, '""')
      .replace(/`[^`]*`/g, "``")
      .replace(/\bstate\b/g, "")
      .replace(/\bderived\b/g, "")
      .replace(/[0-9]/g, "")
      .replace(/[+\-*/%<>=!&|?:().,\s\[\]]/g, "")
      .replace(/true|false|null|undefined/g, "");

    // Remaining letters (if any) indicate unknown identifiers.
    if (/[a-zA-Z_$]/.test(stripped)) {
      return `{{${expr}}}`;
    }

    // eslint-disable-next-line no-new-func
    const fn = new Function("state", "derived", `return (${expr});`);
    return fn(ctx.state, ctx.derived);
  } catch {
    return `{{${expr}}}`;
  }
}

function getTargetKey(target: string): string | null {
  if (!target) return null;
  if (target.startsWith("state.")) return target.slice("state.".length);
  if (target.startsWith("derived.")) return null; // disallow writes to derived
  // treat plain as state key
  if (!target.includes(".")) return target;
  return null;
}

function layoutTypeFor(id: string): { type: "vertical" | "horizontal" | "grid"; gap?: number } | null {
  const map: Record<string, { type: "vertical" | "horizontal" | "grid"; gap?: number }> = {
    page_root: { type: "vertical", gap: 16 },
    form_card: { type: "vertical", gap: 12 },
    form_container: { type: "vertical", gap: 12 },
  };
  return map[id] ?? null;
}

export default function GeneratedApp() {
  // -------------------------
  // State (from data_ir.state)
  // -------------------------
  const [studentName, setStudentName] = useState<string>("");
  const [studentAge, setStudentAge] = useState<number | null>(null);
  const [studentClass, setStudentClass] = useState<number | null>(null);
  const [studentGpa, setStudentGpa] = useState<number | null>(null);
  const [studentLocation, setStudentLocation] = useState<string>("");
  const [studentLevel, setStudentLevel] = useState<"Primary" | "Secondary" | "High School" | null>(null);

  const stateObj = useMemo(
    () => ({
      studentName,
      studentAge,
      studentClass,
      studentGpa,
      studentLocation,
      studentLevel,
    }),
    [studentName, studentAge, studentClass, studentGpa, studentLocation, studentLevel]
  );

  // -------------------------
  // Derived (from data_ir.derived)
  // -------------------------
  const studentLevelDerived = useMemo(() => {
    return safeEvalExpr(
      "state.studentClass <= 5 ? 'Primary' : (state.studentClass <= 10 ? 'Secondary' : 'High School')",
      { state: stateObj, derived: {} }
    );
  }, [stateObj]);

  const derivedObj: DerivedMap = useMemo(
    () => ({
      studentLevelDerived,
    }),
    [studentLevelDerived]
  );

  const setters: Record<string, (v: any) => void> = useMemo(
    () => ({
      studentName: setStudentName,
      studentAge: setStudentAge,
      studentClass: setStudentClass,
      studentGpa: setStudentGpa,
      studentLocation: setStudentLocation,
      studentLevel: setStudentLevel,
    }),
    []
  );

  const applyUpdates = useCallback(
    (updates: Array<{ target: string; expr: string }>) => {
      if (!Array.isArray(updates)) return;
      for (const upd of updates) {
        const key = getTargetKey(upd?.target);
        if (!key) continue;
        const setter = setters[key];
        if (!setter) continue;
        const value = safeEvalExpr(String(upd?.expr ?? ""), { state: stateObj, derived: derivedObj });
        setter(value as any);
      }
    },
    [setters, stateObj, derivedObj]
  );

  // -------------------------
  // Events (from behaviour_ir.events)
  // -------------------------
  const evt_setStudentLevel = useCallback(() => {
    applyUpdates([
      {
        target: "state.studentLevel",
        expr: "state.studentClass <= 5 ? 'Primary' : (state.studentClass <= 10 ? 'Secondary' : 'High School')",
      },
    ]);
  }, [applyUpdates]);

  // -------------------------
  // Actions (from behaviour_ir.actions)
  // -------------------------
  const act_determineStudentLevel = useCallback(() => {
    // Validation based on rules
    const errors: string[] = [];

    const requiredFields: Array<{ key: string; label: string; value: unknown }> = [
      { key: "studentName", label: "Student Name", value: studentName },
      { key: "studentAge", label: "Age", value: studentAge },
      { key: "studentClass", label: "Class", value: studentClass },
      { key: "studentGpa", label: "GPA", value: studentGpa },
      { key: "studentLocation", label: "Location", value: studentLocation },
    ];

    for (const f of requiredFields) {
      if (f.value === null || f.value === undefined || (typeof f.value === "string" && f.value.trim() === "")) {
        errors.push(`${f.label} is required.`);
      }
    }

    const gpa = studentGpa;
    if (typeof gpa === "number") {
      if (gpa < 0 || gpa > 4) errors.push("GPA must be between 0.0 and 4.0.");
    }

    const age = studentAge;
    if (typeof age === "number") {
      if (age < 1) errors.push("Age must be at least 1.");
      if (!Number.isInteger(age)) errors.push("Age must be an integer.");
    }

    const cls = studentClass;
    if (typeof cls === "number") {
      if (cls < 1) errors.push("Class must be at least 1.");
      if (!Number.isInteger(cls)) errors.push("Class must be an integer.");
    }

    if (errors.length > 0) {
      message.error("Please complete all fields with valid values before determining the student level.");
      return;
    }

    // operation == emit_event (payload.event_id = evt_setStudentLevel)
    // plus provided updates
    evt_setStudentLevel();
    applyUpdates([
      {
        target: "state.studentLevel",
        expr: "state.studentClass <= 5 ? 'Primary' : (state.studentClass <= 10 ? 'Secondary' : 'High School')",
      },
    ]);

    message.success("Student level determined.");
  }, [studentName, studentAge, studentClass, studentGpa, studentLocation, evt_setStudentLevel, applyUpdates]);

  const handlers: Record<string, (() => void) | undefined> = useMemo(
    () => ({
      evt_setStudentLevel,
      act_determineStudentLevel,
    }),
    [evt_setStudentLevel, act_determineStudentLevel]
  );

  // -------------------------
  // Render helpers (component_ir + layout_ir)
  // -------------------------
  const childrenMap: Record<string, string[]> = useMemo(
    () => ({
      page_root: ["title", "form_card"],
      form_card: ["form_container"],
      form_container: [
        "inp_name",
        "inp_age",
        "inp_class",
        "inp_gpa",
        "inp_location",
        "btn_determine_level",
        "result_alert",
      ],
    }),
    []
  );

  const renderNode = useCallback(
    (id: string): React.ReactNode => {
      const components: any = {
        page_root: {
          type: "Container",
          label: null,
          bind: null,
          onClick: null,
          props: { padding: 24 },
          styles: { maxWidth: 720, margin: "0 auto" },
        },
        title: {
          type: "TypographyTitle",
          label: "Student Information",
          bind: null,
          onClick: null,
          props: { level: 2 },
          styles: {},
        },
        form_card: {
          type: "Card",
          label: null,
          bind: null,
          onClick: null,
          props: { title: "Enter details" },
          styles: {},
        },
        form_container: {
          type: "Form",
          label: null,
          bind: null,
          onClick: null,
          props: { layout: "vertical", requiredMark: true },
          styles: {},
        },
        inp_name: {
          type: "Input",
          label: "Student Name",
          bind: "state.studentName",
          onClick: null,
          props: { placeholder: "e.g., Alex Johnson" },
          styles: {},
        },
        inp_age: {
          type: "InputNumber",
          label: "Age",
          bind: "state.studentAge",
          onClick: null,
          props: { min: 1, precision: 0, style: { width: "100%" } },
          styles: {},
        },
        inp_class: {
          type: "InputNumber",
          label: "Class",
          bind: "state.studentClass",
          onClick: null,
          props: { min: 1, precision: 0, style: { width: "100%" } },
          styles: {},
        },
        inp_gpa: {
          type: "InputNumber",
          label: "GPA",
          bind: "state.studentGpa",
          onClick: null,
          props: { min: 0, max: 4, step: 0.1, precision: 2, style: { width: "100%" } },
          styles: {},
        },
        inp_location: {
          type: "Input",
          label: "Location",
          bind: "state.studentLocation",
          onClick: null,
          props: { placeholder: "e.g., Nairobi" },
          styles: {},
        },
        btn_determine_level: {
          type: "Button",
          label: "Determine Student Level",
          bind: null,
          onClick: "act_determineStudentLevel",
          props: { type: "primary", block: true },
          styles: {},
        },
        result_alert: {
          type: "Alert",
          label: null,
          bind: "state.studentLevel",
          onClick: null,
          props: { message: "Student Level", type: "success", showIcon: true },
          styles: {},
        },
      };

      const node = components[id];
      if (!node) {
        return <div key={id}>Missing component: {id}</div>;
      }

      const layout = layoutTypeFor(id);
      const kids = childrenMap[id] || [];
      const renderedChildren = kids.map((cid) => <React.Fragment key={cid}>{renderNode(cid)}</React.Fragment>);

      const commonStyle: React.CSSProperties | undefined = node.styles || undefined;

      const wrapChildren = (content: React.ReactNode) => {
        if (!layout) return content;
        if (layout.type === "vertical") {
          return (
            <Space direction="vertical" size={layout.gap ?? 8} style={{ width: "100%" }}>
              {content}
            </Space>
          );
        }
        if (layout.type === "horizontal") {
          return (
            <Space direction="horizontal" size={layout.gap ?? 8} style={{ width: "100%" }}>
              {content}
            </Space>
          );
        }
        if (layout.type === "grid") {
          const gutter = layout.gap ?? 12;
          return (
            <Row gutter={[gutter, gutter]} style={{ width: "100%" }}>
              {React.Children.map(content as any, (child, idx) => (
                <Col key={idx} span={24}>
                  {child}
                </Col>
              ))}
            </Row>
          );
        }
        return content;
      };

      const handleClickId: string | null = node.onClick ?? null;
      const onClick = handleClickId ? handlers[handleClickId] : undefined;

      switch (node.type) {
        case "Container": {
          const padding = node.props?.padding;
          const style: React.CSSProperties = {
            ...(typeof padding === "number" ? { padding } : {}),
            ...(commonStyle || {}),
          };
          return <div style={style}>{wrapChildren(renderedChildren)}</div>;
        }
        case "TypographyTitle": {
          const { level, ...restProps } = node.props || {};
          return (
            <Typography.Title level={level ?? 2} style={commonStyle} {...restProps}>
              {node.label ?? ""}
            </Typography.Title>
          );
        }
        case "Card": {
          const { title, ...restProps } = node.props || {};
          return (
            <Card title={title ?? node.label ?? undefined} style={commonStyle} {...restProps}>
              {wrapChildren(renderedChildren)}
            </Card>
          );
        }
        case "Form": {
          const restProps = node.props || {};
          return (
            <Form style={commonStyle} {...restProps}>
              {wrapChildren(renderedChildren)}
            </Form>
          );
        }
        case "Input": {
          const bind: string | null = node.bind ?? null;
          const key = bind?.startsWith("state.") ? bind.slice("state.".length) : bind;
          const value = key && key in stateObj ? (stateObj as any)[key] : undefined;
          const setter = key ? setters[key] : undefined;

          const inputEl = (
            <Input
              value={typeof value === "string" ? value : value ?? ""}
              onChange={(e) => setter?.(e.target.value)}
              style={commonStyle}
              {...(node.props || {})}
            />
          );

          return node.label ? <Form.Item label={node.label}>{inputEl}</Form.Item> : inputEl;
        }
        case "InputNumber": {
          const bind: string | null = node.bind ?? null;
          const key = bind?.startsWith("state.") ? bind.slice("state.".length) : bind;
          const value = key && key in stateObj ? (stateObj as any)[key] : undefined;
          const setter = key ? setters[key] : undefined;

          const { style: innerStyle, ...restProps } = node.props || {};
          const mergedStyle = { ...(innerStyle || {}), ...(commonStyle || {}) };

          const inputEl = (
            <InputNumber
              value={typeof value === "number" ? value : value ?? null}
              onChange={(v) => setter?.(v === null ? null : v)}
              style={mergedStyle}
              {...restProps}
            />
          );

          return node.label ? <Form.Item label={node.label}>{inputEl}</Form.Item> : inputEl;
        }
        case "Button": {
          return (
            <Button onClick={onClick} style={commonStyle} {...(node.props || {})}>
              {node.label ?? ""}
            </Button>
          );
        }
        case "Alert": {
          const bind: string | null = node.bind ?? null;
          const key = bind?.startsWith("state.") ? bind.slice("state.".length) : bind;
          const value = key && key in stateObj ? (stateObj as any)[key] : undefined;

          const description =
            value === null || value === undefined || value === ""
              ? "No level determined yet."
              : typeof value === "string"
              ? value
              : String(value);

          // Hide alert if nothing set
          if (value === null || value === undefined || value === "") {
            return null;
          }

          return (
            <Alert
              onClick={onClick}
              style={commonStyle}
              description={description}
              {...(node.props || {})}
            />
          );
        }
        default: {
          return (
            <div style={commonStyle}>
              Unsupported component: {String(node.type)}
              {kids.length > 0 ? <div style={{ marginTop: 8 }}>{wrapChildren(renderedChildren)}</div> : null}
            </div>
          );
        }
      }
    },
    [childrenMap, derivedObj, handlers, renderNode, setters, stateObj]
  );

  const theme = {
    token: {
      colorPrimary: "#22c55e",
      colorInfo: "#ef4444",
      fontFamily: "Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif",
      borderRadius: 8,
    },
  } as const;

  return <ConfigProvider theme={theme}>{renderNode("page_root")}</ConfigProvider>;
}
