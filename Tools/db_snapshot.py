import argparse
from pathlib import Path

from ir_pipeline.utils import ensure_external_db_snapshot


def _resolve_path(base: Path, raw: str) -> Path:
    candidate = Path(raw)
    if candidate.is_absolute():
        return candidate
    return (base / raw).resolve()


def main() -> None:
    tools_dir = Path(__file__).resolve().parent
    repo_root = tools_dir.parent

    parser = argparse.ArgumentParser(description="Generate an external DB snapshot JSON from SQLite.")
    parser.add_argument(
        "--db",
        default="db/student_data.db",
        help="Path to SQLite DB (default: db/student_data.db).",
    )
    parser.add_argument(
        "--output",
        default="db/external_db_snapshot.json",
        help="Path to snapshot JSON (default: db/external_db_snapshot.json).",
    )
    parser.add_argument(
        "--source-id",
        default="student_external",
        help="Logical source ID written into snapshot metadata.",
    )
    parser.add_argument(
        "--sample-rows",
        type=int,
        default=10,
        help="Sample rows per table (default: 10).",
    )
    args = parser.parse_args()

    db_path = _resolve_path(repo_root, args.db)
    output_path = _resolve_path(repo_root, args.output)

    snapshot = ensure_external_db_snapshot(
        db_path=db_path,
        snapshot_path=output_path,
        source_id=args.source_id,
        sample_rows_per_table=max(1, args.sample_rows),
    )
    print(f"Snapshot written to: {output_path}")
    print(f"Tables: {', '.join(sorted(snapshot.get('tables', {}).keys()))}")


if __name__ == "__main__":
    main()

