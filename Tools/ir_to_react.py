import argparse
import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from ir_structure import IRBundle


def _extract_code_block(text: str) -> str:
    match = re.search(r"```(?:tsx|jsx|typescript|javascript)?\s*(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def _load_ir_bundle(path: Path) -> IRBundle:
    data = json.loads(path.read_text(encoding="utf-8"))
    return IRBundle.model_validate(data)


def _build_prompt(ir_json: str) -> str:
    return f""" 
You are a senior React engineer.
Convert the provided IRBundle JSON into a complete React component file in TypeScript.

Output requirements:
- Return TSX code only. No markdown and no extra text.
- Export default function GeneratedApp().
- Use Ant Design components for UI (antd).
- Do not import any UI library other than antd (and React).

Implementation requirements:
- Build React state from data_ir.state:
  - Create one useState per key in data_ir.state.
  - Initialize from the field's initial value.
- Build derived values from data_ir.derived:
  - Use useMemo for each derived field.
  - Evaluate expressions in a safe, minimal way (simple arithmetic / boolean / string ops).
  - If an expression cannot be safely evaluated, keep it as a placeholder string and do not crash.
- Implement behaviour_ir.events:
  - Create one handler function per eventId.
  - For each MutationUpdate:
    - target uses dot paths like "state.someKey" OR plain "someKey" (treat plain as state).
    - expr can reference state keys and derived keys.
    - Apply updates in order.
- Implement behaviour_ir.actions (if present):
  - Create one handler per actionId.
  - For now, map actions to:
    - operation == "open_modal": set state.is_modal_open = true (if present)
    - operation == "close_modal": set state.is_modal_open = false (if present)
    - otherwise: run its updates, then (optionally) run a same-id feedback ui_updates if you support it.
- Respect component_ir.components:
  - label: show as text where relevant (Button text, Typography text, Card title, Modal title, Form.Item label).
  - bind: if bind is a state key, wire value/onChange.
  - onClick: wire to matching eventId or actionId handler.
  - props: spread into the antd component props (after your controlled props so controlled wins).
  - styles: apply via style prop where possible.
- Respect layout_ir:
  - Use the layout tree from layout_ir.root and layout_ir.children.
  - Use layout_ir.layout hints:
    - vertical: render children in antd Space direction="vertical"
    - horizontal: Space direction="horizontal"
    - grid: use Row/Col with a reasonable default gutter derived from gap
- Respect layout_ir.layout_zones (if present):
  - base zones render in normal flow.
  - overlay zones render with antd Modal/Drawer depending on the component type; otherwise render in a fixed positioned div.

Theming requirements:
- Apply component_ir.theme.primaryColor using Ant Design ConfigProvider theme token (token.colorPrimary).
- Also apply secondaryColor/fontFamily/borderRadius if present (token.colorInfo or colorPrimaryHover; fontFamily; borderRadius).

Robustness requirements:
- Do not crash if unknown component types appear:
  - Render a fallback <div>Unsupported component: {type}</div>
- Ensure all referenced ids exist before rendering; if missing, render a fallback block.

IRBundle JSON:
{ir_json}
""".strip()



def main() -> None:
    parser = argparse.ArgumentParser(description="Convert IRBundle JSON to React TSX using an LLM.")
    parser.add_argument(
        "--input",
        default="generated_ir.json",
        help="Path to input IR JSON file (default: generated_ir.json).",
    )
    parser.add_argument(
        "--output",
        default="generated_app.tsx",
        help="Path to output TSX file (default: generated_app.tsx).",
    )
    parser.add_argument("--model", default="gpt-5.2", help="LLM model name.")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing. Add it to your environment or .env file.")

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    try:
        irbundle = _load_ir_bundle(input_path)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {input_path}: {exc}") from exc
    except ValidationError as exc:
        raise ValueError(f"JSON does not match IRBundle schema: {exc}") from exc

    model = ChatOpenAI(
        model=args.model,
        temperature=0,
        api_key=api_key,
    )

    ir_json = irbundle.model_dump_json(indent=2)
    response = model.invoke(_build_prompt(ir_json))
    raw_text = response.content if isinstance(response.content, str) else str(response.content)
    tsx_code = _extract_code_block(raw_text)

    output_path = Path(args.output)
    output_path.write_text(tsx_code + "\n", encoding="utf-8")
    print(f"React code written to: {output_path.resolve()}")


if __name__ == "__main__":
    main()
