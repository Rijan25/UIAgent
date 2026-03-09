# Repository Layout

## Target Structure

```text
UIAgent/
  main.py
  pyproject.toml
  uv.lock
  README.md
  Script/
    common.ps1
    generate-ir.ps1
    generate-react.ps1
    run-pipeline.ps1
  ui_generation/
    cli/
      ir_generation.py
      ir_to_react.py
      ir_structure.py
    ir_pipeline/
    generated/
      ir/
      react/
    examples/
      sample_ir.json
    logs/
      uia.log
      scripts/
  ui-compiler-poc/
    frontend/
  docs/
```

## Naming Guidance

- Application folder: `ui_generation`
- Core package: `ir_pipeline`
- CLI folder: `ui_generation/cli`
- Generated artifacts: `ui_generation/generated/ir` and `ui_generation/generated/react`

## Operational Rules

- Keep generated artifacts and logs out of git.
- Keep scripts in `Script/` and shared logic in `Script/common.ps1`.
- Keep app logs readable in terminal and detailed in file logs.
