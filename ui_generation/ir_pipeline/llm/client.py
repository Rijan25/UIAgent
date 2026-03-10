import os

try:
    import boto3
except ModuleNotFoundError as exc:  # pragma: no cover
    raise ModuleNotFoundError(
        "Missing dependency 'boto3'. Install project dependencies and run via the project environment.\n"
        "Recommended:\n"
        "  1) uv sync\n"
        "  2) uv run python ui_generation/cli/ir_generation.py --images-dir ui_generation/uploads\n"
        "Or (PowerShell):\n"
        "  .\\.venv\\Scripts\\python ui_generation/cli/ir_generation.py --images-dir ui_generation/uploads"
    ) from exc

try:
    from dotenv import load_dotenv
except ModuleNotFoundError as exc:  # pragma: no cover
    raise ModuleNotFoundError(
        "Missing dependency 'python-dotenv'. Run `uv sync` and use `uv run ...`."
    ) from exc

try:
    from langchain_aws import ChatBedrockConverse
except ModuleNotFoundError as exc:  # pragma: no cover
    raise ModuleNotFoundError(
        "Missing dependency 'langchain-aws'. Run `uv sync` and use `uv run ...`."
    ) from exc

try:
    from botocore.config import Config
except ModuleNotFoundError:  # pragma: no cover
    Config = None  # type: ignore[assignment]

DEFAULT_CLAUDE_MODEL = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"
_MODEL_ALIASES = {
    "sonnet 4.5": DEFAULT_CLAUDE_MODEL,
    "sonnet-4.5": DEFAULT_CLAUDE_MODEL,
    "claude sonnet 4.5": DEFAULT_CLAUDE_MODEL,
    "claude-sonnet-4.5": DEFAULT_CLAUDE_MODEL,
}


def _first_non_empty(*keys: str) -> str | None:
    for key in keys:
        value = os.getenv(key)
        if value is not None:
            stripped = value.strip()
            if stripped:
                return stripped
    return None


def _resolve_model_name(model_name: str | None) -> str:
    configured_model = (
        os.getenv("BEDROCK_MODEL_ID")
        or os.getenv("ANTHROPIC_BEDROCK_MODEL")
        or ""
    ).strip()
    raw = (model_name or "").strip()

    if not raw:
        target = configured_model or DEFAULT_CLAUDE_MODEL
    elif raw == DEFAULT_CLAUDE_MODEL and configured_model:
        target = configured_model
    else:
        target = raw

    return _MODEL_ALIASES.get(target.lower(), target)


def build_chat_model(
    model_name: str = DEFAULT_CLAUDE_MODEL,
    temperature: float = 0,
) -> ChatBedrockConverse:
    load_dotenv()
    profile = _first_non_empty("AWS_PROFILE", "aws_profile")
    access_key = _first_non_empty("AWS_ACCESS_KEY_ID", "AWS_ACCESS_KEY", "aws_access_key")
    secret_key = _first_non_empty("AWS_SECRET_ACCESS_KEY", "AWS_SECRET_KEY", "aws_secret_key")
    session_token = _first_non_empty("AWS_SESSION_TOKEN", "aws_session_token")
    region = _first_non_empty(
        "BEDROCK_AWS_REGION",
        "AWS_REGION",
        "AWS_DEFAULT_REGION",
        "aws_region",
    ) or "us-east-1"
    resolved_model = _resolve_model_name(model_name)

    if access_key and secret_key:
        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            aws_session_token=session_token,
            region_name=region,
        )
    elif profile:
        session = boto3.Session(profile_name=profile, region_name=region)
    else:
        session = boto3.Session(region_name=region)

    if session.get_credentials() is None:
        raise RuntimeError(
            "AWS credentials were not found. Set AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY "
            "(or aws_access_key/aws_secret_key), plus optional AWS_SESSION_TOKEN, "
            "or configure AWS_PROFILE."
        )

    kwargs = {
        "model": resolved_model,
        "region_name": region,
        "temperature": temperature,
    }

    # Image-based prompts can take minutes. Botocore defaults are often too short.
    if Config is not None:
        connect_timeout = int(os.getenv("BEDROCK_CONNECT_TIMEOUT_SECONDS", "30"))
        read_timeout = int(os.getenv("BEDROCK_READ_TIMEOUT_SECONDS", "600"))
        max_attempts = int(os.getenv("BEDROCK_MAX_ATTEMPTS", "2"))
        kwargs["config"] = Config(
            connect_timeout=connect_timeout,
            read_timeout=read_timeout,
            retries={"max_attempts": max_attempts, "mode": "standard"},
            tcp_keepalive=True,
        )
    if access_key and secret_key:
        kwargs["aws_access_key_id"] = access_key
        kwargs["aws_secret_access_key"] = secret_key
        if session_token:
            kwargs["aws_session_token"] = session_token
    elif profile:
        kwargs["credentials_profile_name"] = profile

    return ChatBedrockConverse(**kwargs)
