import re
from json import JSONDecodeError


def extract_json_object(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or start >= end:
        raise JSONDecodeError("No JSON object found in model response.", text, 0)
    return text[start : end + 1]


def extract_code_block(text: str) -> str:
    match = re.search(r"```(?:tsx|jsx|typescript|javascript)?\s*(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def coerce_message_content_to_text(content: object) -> str:
    """
    ChatBedrockConverse can return either a plain string or a list of content blocks.
    We only care about text blocks for downstream JSON/code parsing.
    """
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict):
                text = block.get("text")
                if isinstance(text, str):
                    parts.append(text)
        if parts:
            return "".join(parts)

    return str(content)
