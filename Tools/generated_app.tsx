import React, { useCallback, useMemo, useState } from "react";
import {
  Alert,
  Button,
  Card,
  Col,
  ConfigProvider,
  Form,
  Input,
  InputNumber,
  Modal,
  Row,
  Space,
  Typography,
  message,
} from "antd";

type AnyRecord = Record<string, any>;

function safeEvalExpression(
  expr: string,
  ctx: { state: AnyRecord; derived: AnyRecord }
): any {
  try {
    // Allow only simple expressions with these characters/tokens.
    // Disallow braces, semicolons, backticks, newlines to reduce injection risk.
    const forbidden = /[{};`\\\n\r]/;
    if (forbidden.test(expr)) return `[[unsafe_expr:${expr}]]`;

    // Disallow obvious dangerous identifiers.
    const dangerousWords = /\b(window|document|globalThis|Function|eval|constructor|prototype|__proto__|process|require|import)\b/;
    if (dangerousWords.test(expr)) return `[[unsafe_expr:${expr}]]`;

    // Ensure only references are via state.* or derived.* (plus literals/operators).
    // This is a heuristic check: any bare identifier that isn't true/false/null/undefined/NaN/Infinity
    // indicates potentially unsafe or unsupported expression.
    const identifiers = expr.match(/[A-Za-z_$][A-Za-z0-9_$]*/g) ?? [];
    const allowedBare = new Set(["true", "false", "null", "undefined", "NaN", "Infinity"]);
    for (const id of identifiers) {
      if (allowedBare.has(id)) continue;
      if (id === "state" || id === "derived") continue;
      // If it's part of state.xxx or derived.xxx, it will still appear as tokens (state, studentClass, etc).
      // We only allow bare identifiers if they appear as property names after '.'; we approximate by checking
      // that every non-allowed identifier is either 'state'/'derived' or appears after a dot in the string.
      const re = new RegExp(`\\.${id}\\b`);
      if (!re.test(expr)) return `[[unsupported_expr:${expr}]]`;
    }

    // Evaluate in a constrained scope.
    // eslint-disable-next-line no-new-func
    const fn = new Function("state", "derived", `"use strict"; return (${expr});`);
    return fn(ctx.state, ctx.derived);
  } catch {
    return `[[error_expr:${expr}]]`;
  }
}

function normalizeTarget(target: string): { scope: "state" | "derived"; key: string } | null {
  if (!target) return null;
  const t = String(target).trim();
  if (!t) return null;

  if (t.startsWith("state.")) return { scope: "state", key: t.slice("state.".length) };
  if (t.startsWith("derived.")) return { scope: "derived", key: t.slice("derived.".length) };

  // Plain key -> state
  return { scope: "state", key: t };
}

function mergeStyles(a?: React.CSSProperties, b?: React.CSSProperties): React.CSSProperties | undefined {
  if (!a && !b) return undefined;
  return { ...(a || {}), ...(b || {}) };
}

export default function GeneratedApp() {
  // ----- State (from data_ir.state) -----
  const [studentName, setStudentName] = useState<string>("");
  const [studentAge, setStudentAge] = useState<number | null>(null);
  const [studentClass, setStudentClass] = useState<number | null>(null);
  const [studentGpa, setStudentGpa] = useState<number | null>(null);
  const [studentLocation, setStudentLocation] = useState<string>("");
  const [studentLevel, setStudentLevel] = useState<"Primary" | "Secondary" | "High School" | null>(null);

  // Optional modal state support (not present in IR)
  // const [is_modal_open, setIsModalOpen] = useState<boolean>(false);

  const state = useMemo(
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

  // ----- Derived (from data_ir.derived) -----
  const studentLevelDerived = useMemo(() => {
    const expr =
      "state.studentClass <= 5 ? 'Primary' : (state.studentClass <= 10 ? 'Secondary' : 'High School')";
    return safeEvalExpression(expr, { state, derived: {} });
  }, [state]);

  const derived = useMemo(
    () => ({
      studentLevelDerived,
    }),
    [studentLevelDerived]
  );

  // ----- Mutation runner -----
  const applyMutationUpdates = useCallback(
    (updates: Array<{ target: string; expr: string }>) => {
      if (!Array.isArray(updates)) return;

      for (const upd of updates) {
        const targetInfo = normalizeTarget(upd?.target);
        if (!targetInfo) continue;

        const value = safeEvalExpression(String(upd?.expr ?? ""), { state, derived });

        if (targetInfo.scope !== "state") continue;

        switch (targetInfo.key) {
          case "studentName":
            setStudentName(value ?? "");
            break;
          case "studentAge":
            setStudentAge(value === "" ? null : (value as number | null));
            break;
          case "studentClass":
            setStudentClass(value === "" ? null : (value as number | null));
            break;
          case "studentGpa":
            setStudentGpa(value === "" ? null : (value as number | null));
            break;
          case "studentLocation":
            setStudentLocation(value ?? "");
            break;
          case "studentLevel":
            setStudentLevel(value ?? null);
            break;
          // case "is_modal_open":
          //   setIsModalOpen(Boolean(value));
          //   break;
          default:
            // Unknown state key; ignore
            break;
        }
      }
    },
    [state, derived]
  );

  // ----- Events (from behaviour_ir.events) -----
  const evt_setStudentLevel = useCallback(() => {
    applyMutationUpdates([
      {
        target: "state.studentLevel",
        expr: "state.studentClass <= 5 ? 'Primary' : (state.studentClass <= 10 ? 'Secondary' : 'High School')",
      },
    ]);
  }, [applyMutationUpdates]);

  // ----- Actions (from behaviour_ir.actions) -----
  const validateActDetermineStudentLevel = useCallback((): boolean => {
    // required: name, age, class, gpa, location
    if (!studentName || String(studentName).trim().length < 1) return false;
    if (studentAge == null || !Number.isFinite(studentAge) || studentAge < 1 || Math.floor(studentAge) !== studentAge)
      return false;
    if (
      studentClass == null ||
      !Number.isFinite(studentClass) ||
      studentClass < 1 ||
      Math.floor(studentClass) !== studentClass
    )
      return false;
    if (studentGpa == null || !Number.isFinite(studentGpa) || studentGpa < 0 || studentGpa > 4) return false;
    if (!studentLocation || String(studentLocation).trim().length < 1) return false;

    return true;
  }, [studentName, studentAge, studentClass, studentGpa, studentLocation]);

  const act_determineStudentLevel = useCallback(() => {
    const ok = validateActDetermineStudentLevel();
    if (!ok) {
      message.error("Please complete all fields with valid values before determining the student level.");
      return;
    }

    // operation: emit_event -> evt_setStudentLevel
    evt_setStudentLevel();

    // Also run its updates (present in IR)
    applyMutationUpdates([
      {
        target: "state.studentLevel",
        expr: "state.studentClass <= 5 ? 'Primary' : (state.studentClass <= 10 ? 'Secondary' : 'High School')",
      },
    ]);

    message.success("Student level determined.");
  }, [applyMutationUpdates, evt_setStudentLevel, validateActDetermineStudentLevel]);

  // ----- Component registry (from component_ir.components) -----
  const components: Record<string, any> = {
    page_root: {
      type: "Container",
      label: null,
      bind: null,
      onClick: null,
      props: { padding: 24 },
      styles: { maxWidth: 720, margin: "0 auto" },
    },
    title: { type: "TypographyTitle", label: "Student Information", bind: null, onClick: null, props: { level: 2 }, styles: {} },
    form_card: { type: "Card", label: null, bind: null, onClick: null, props: { title: "Enter details" }, styles: {} },
    form_container: { type: "Form", label: null, bind: null, onClick: null, props: { layout: "vertical", requiredMark: true }, styles: {} },
    inp_name: { type: "Input", label: "Student Name", bind: "state.studentName", onClick: null, props: { placeholder: "e.g., Alex Johnson" }, styles: {} },
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
    inp_location: { type: "Input", label: "Location", bind: "state.studentLocation", onClick: null, props: { placeholder: "e.g., Nairobi" }, styles: {} },
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

  const layoutRoot = "page_root";
  const layoutChildren: Record<string, string[]> = {
    page_root: ["title", "form_card"],
    form_card: ["form_container"],
    form_container: ["inp_name", "inp_age", "inp_class", "inp_gpa", "inp_location", "btn_determine_level", "result_alert"],
  };
  const layoutHints: Record<string, { type: "vertical" | "horizontal" | "grid"; gap?: number }> = {
    page_root: { type: "vertical", gap: 16 },
    form_card: { type: "vertical", gap: 12 },
    form_container: { type: "vertical", gap: 12 },
  };

  const resolveOnClickHandler = useCallback(
    (idOrNull: any) => {
      if (!idOrNull) return undefined;
      const id = String(idOrNull);

      if (id === "evt_setStudentLevel") return evt_setStudentLevel;
      if (id === "act_determineStudentLevel") return act_determineStudentLevel;

      return undefined;
    },
    [evt_setStudentLevel, act_determineStudentLevel]
  );

  const renderLeafComponent = useCallback(
    (componentId: string): React.ReactNode => {
      const def = components[componentId];
      if (!def) {
        return (
          <div style={{ padding: 12, border: "1px solid #f0f0f0", borderRadius: 6 }}>
            Missing component: {componentId}
          </div>
        );
      }

      const { type, label, bind, onClick, props, styles } = def as {
        type: string;
        label?: string | null;
        bind?: string | null;
        onClick?: string | null;
        props?: AnyRecord;
        styles?: React.CSSProperties;
      };

      const clickHandler = resolveOnClickHandler(onClick);

      const bindInfo = bind ? normalizeTarget(bind) : null;
      const boundKey = bindInfo?.scope === "state" ? bindInfo.key : null;

      const commonStyle = styles ?? undefined;

      switch (type) {
        case "Container": {
          // Handled as layout node; leaf fallback:
          return <div style={mergeStyles({ padding: props?.padding }, commonStyle)} onClick={clickHandler} {...props} />;
        }
        case "TypographyTitle": {
          const level = props?.level ?? 2;
          return (
            <Typography.Title level={level} style={commonStyle} onClick={clickHandler} {...props}>
              {label ?? ""}
            </Typography.Title>
          );
        }
        case "Card": {
          return (
            <Card style={commonStyle} onClick={clickHandler as any} {...props}>
              {renderNode(componentId)}
            </Card>
          );
        }
        case "Form": {
          // We'll render children inside; Form.Item will be created for inputs via their labels.
          return (
            <Form style={commonStyle} onFinish={undefined} {...props}>
              {renderNode(componentId)}
            </Form>
          );
        }
        case "Input": {
          const value = boundKey === "studentName" ? studentName : boundKey === "studentLocation" ? studentLocation : undefined;

          const onChange =
            boundKey === "studentName"
              ? (e: React.ChangeEvent<HTMLInputElement>) => setStudentName(e.target.value)
              : boundKey === "studentLocation"
                ? (e: React.ChangeEvent<HTMLInputElement>) => setStudentLocation(e.target.value)
                : undefined;

          const inputEl = (
            <Input
              value={value}
              onChange={onChange}
              onClick={clickHandler as any}
              style={commonStyle}
              {...props}
            />
          );

          if (label) {
            const required =
              boundKey === "studentName" || boundKey === "studentLocation" ? true : false;
            return (
              <Form.Item
                label={label}
                required={required}
                validateStatus={undefined}
                help={undefined}
                style={{ marginBottom: 0 }}
              >
                {inputEl}
              </Form.Item>
            );
          }

          return inputEl;
        }
        case "InputNumber": {
          const value =
            boundKey === "studentAge"
              ? studentAge
              : boundKey === "studentClass"
                ? studentClass
                : boundKey === "studentGpa"
                  ? studentGpa
                  : undefined;

          const onChange =
            boundKey === "studentAge"
              ? (v: number | null) => setStudentAge(v)
              : boundKey === "studentClass"
                ? (v: number | null) => setStudentClass(v)
                : boundKey === "studentGpa"
                  ? (v: number | null) => setStudentGpa(v)
                  : undefined;

          const inputEl = (
            <InputNumber
              value={value as any}
              onChange={onChange as any}
              onClick={clickHandler as any}
              style={mergeStyles(commonStyle, props?.style)}
              {...props}
            />
          );

          if (label) {
            const required =
              boundKey === "studentAge" || boundKey === "studentClass" || boundKey === "studentGpa";
            return (
              <Form.Item label={label} required={required} style={{ marginBottom: 0 }}>
                {inputEl}
              </Form.Item>
            );
          }

          return inputEl;
        }
        case "Button": {
          return (
            <Button style={commonStyle} onClick={clickHandler} {...props}>
              {label ?? "Button"}
            </Button>
          );
        }
        case "Alert": {
          const boundValue = boundKey === "studentLevel" ? studentLevel : undefined;
          const description =
            boundValue == null || boundValue === ""
              ? "No level determined yet."
              : String(boundValue);

          // Only show once we have a determined level (or keep visible with info)
          const show = boundValue != null && String(boundValue).length > 0;

          return (
            <div style={commonStyle}>
              {show ? (
                <Alert
                  {...props}
                  description={description}
                />
              ) : null}
            </div>
          );
        }
        case "Modal": {
          // If modal appears as regular node, render it closed by default (no is_modal_open in IR)
          const open = Boolean((state as any).is_modal_open);
          return (
            <Modal open={open} title={label ?? props?.title} onCancel={() => {}} footer={null} {...props}>
              {renderNode(componentId)}
            </Modal>
          );
        }
        default: {
          return (
            <div style={mergeStyles({ padding: 12, border: "1px dashed #d9d9d9", borderRadius: 6 }, commonStyle)}>
              Unsupported component: &lt;class '{type}'&gt;
            </div>
          );
        }
      }
    },
    [
      components,
      resolveOnClickHandler,
      renderNode,
      state,
      studentAge,
      studentClass,
      studentGpa,
      studentLevel,
      studentLocation,
      studentName,
    ]
  );

  function renderWithLayout(containerId: string, childrenIds: string[]): React.ReactNode {
    const hint = layoutHints[containerId];
    const gap = hint?.gap ?? 12;

    if (hint?.type === "horizontal") {
      return (
        <Space direction="horizontal" size={gap} style={{ width: "100%" }} align="start">
          {childrenIds.map((cid) => (
            <React.Fragment key={cid}>{renderNode(cid)}</React.Fragment>
          ))}
        </Space>
      );
    }

    if (hint?.type === "grid") {
      const gutter = gap;
      const span = Math.max(6, Math.floor(24 / Math.max(1, childrenIds.length)));
      return (
        <Row gutter={[gutter, gutter]}>
          {childrenIds.map((cid) => (
            <Col key={cid} span={span}>
              {renderNode(cid)}
            </Col>
          ))}
        </Row>
      );
    }

    // Default: vertical
    return (
      <Space direction="vertical" size={gap} style={{ width: "100%" }}>
        {childrenIds.map((cid) => (
          <React.Fragment key={cid}>{renderNode(cid)}</React.Fragment>
        ))}
      </Space>
    );
  }

  function renderNode(nodeId: string): React.ReactNode {
    const def = components[nodeId];
    if (!def) {
      return (
        <div style={{ padding: 12, border: "1px solid #f0f0f0", borderRadius: 6 }}>
          Missing component: {nodeId}
        </div>
      );
    }

    const childrenIds = layoutChildren[nodeId] ?? [];
    const hasChildren = childrenIds.length > 0;
    const type = def.type as string;

    if (hasChildren) {
      // Nodes like Container/Card/Form should render their own wrapper, then children inside.
      if (type === "Container") {
        const padding = def?.props?.padding;
        const style = mergeStyles({ padding }, def.styles);
        return (
          <div style={style} onClick={resolveOnClickHandler(def.onClick)} {...def.props}>
            {renderWithLayout(nodeId, childrenIds)}
          </div>
        );
      }
      if (type === "Card" || type === "Form") {
        // Use leaf renderer to create wrapper and recurse
        return renderLeafComponent(nodeId);
      }

      // Generic container if unknown but has children
      return <div style={def.styles}>{renderWithLayout(nodeId, childrenIds)}</div>;
    }

    return renderLeafComponent(nodeId);
  }

  const themePrimary = "#22c55e";
  const themeSecondary = "#ef4444";
  const themeFontFamily =
    "Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif";
  const themeBorderRadius = 8;

  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: themePrimary,
          colorInfo: themeSecondary,
          fontFamily: themeFontFamily,
          borderRadius: themeBorderRadius,
        },
      }}
    >
      {renderNode(layoutRoot)}
    </ConfigProvider>
  );
}
