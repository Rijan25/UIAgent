import React, { useMemo, useState, useCallback } from "react";
import { Button, ConfigProvider, Form, InputNumber, Space, Typography } from "antd";

type StateShape = {
  num1: number;
  num2: number;
  result: number;
};

export default function GeneratedApp() {
  const [state, setState] = useState<StateShape>({
    num1: 0,
    num2: 0,
    result: 0,
  });

  const resultText = useMemo(() => "Result: " + state.result, [state.result]);

  const evt_sum = useCallback(() => {
    setState((prev) => ({
      ...prev,
      result: prev.num1 + prev.num2,
    }));
  }, []);

  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: "#22c55e",
        },
      }}
    >
      <div
        style={{
          padding: 16,
          background: "#f0fdf4",
          borderRadius: 12,
          maxWidth: 320,
        }}
      >
        <Space direction="vertical" size={12} style={{ width: "100%" }}>
          <Form layout="vertical" style={{ margin: 0 }}>
            <Form.Item label="Num 1" style={{ marginBottom: 0 }}>
              <InputNumber
                placeholder="Enter num1"
                style={{ width: "100%" }}
                value={state.num1}
                onChange={(v) => {
                  const next =
                    typeof v === "number" && !Number.isNaN(v) ? v : 0;
                  setState((prev) => ({ ...prev, num1: next }));
                }}
              />
            </Form.Item>

            <Form.Item label="Num 2" style={{ marginBottom: 0, marginTop: 12 }}>
              <InputNumber
                placeholder="Enter num2"
                style={{ width: "100%" }}
                value={state.num2}
                onChange={(v) => {
                  const next =
                    typeof v === "number" && !Number.isNaN(v) ? v : 0;
                  setState((prev) => ({ ...prev, num2: next }));
                }}
              />
            </Form.Item>
          </Form>

          <Button
            type="primary"
            onClick={evt_sum}
            style={{ background: "#1677ff", borderColor: "#1677ff" }}
          >
            Sum
          </Button>

          <Typography.Text strong style={{ fontSize: 16, color: "#16a34a" }}>
            {resultText}
          </Typography.Text>
        </Space>
      </div>
    </ConfigProvider>
  );
}