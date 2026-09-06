import json
import logging
from typing import Any, Callable
from errors import ToolCallError


logger = logging.getLogger(__name__)

class Runner:
    def __init__(self, tools: dict[str, Callable]):
        self.tools = tools # mapping
        self.results = []

    def run(self, payload: list[dict[str, Any]]) -> list[dict[str, Any]]:
        for i, call in enumerate(payload):
            tool_name = call["tool"]
            raw_args = call["args"]

            try:
                args = self._resolve_placeholders(raw_args)
            except ToolCallError as e:
                entry = {"step": i, "tool": tool_name, "args": raw_args, "status": "error", "error": str(e)}
                self.results.append(entry)
                continue

            if tool_name not in self.tools:
                entry = {"step": i, "tool": tool_name, "args": args, "status": "error", "error": f"unknown tool: {tool_name}"}
                self.results.append(entry)
                continue

            try:
                result = self.tools[tool_name](**args)
                parsed = self._parse_result(result)
                status = "ok"
                error = None

                if parsed is not None:
                    raw_status = parsed.get("status")
                    if isinstance(raw_status, str) and raw_status.lower() == "error":
                        status = "error"
                        error = parsed.get("message", "tool returned error")

                entry = {"step": i, "tool": tool_name, "args": args, "status": status, "result": result}
                if error is not None:
                    entry["error"] = error
            except Exception as e:
                entry = {"step": i, "tool": tool_name, "args": args, "status": "error", "error": str(e)}

            self.results.append(entry)

        return self.results

    def _resolve_placeholders(self, args: dict[str, Any]) -> dict[str, Any]:
        """
        Replaces '<id above>' / '<id of level above>' style placeholders with the real id returned by the most recent successful call.
        """
        resolved = dict(args)
        for key, value in resolved.items():
            if isinstance(value, str) and value.startswith("<") and value.endswith(">"):
                resolved[key] = self._resolve_placeholder_value(key=key, value=value)
        return resolved

    def _resolve_placeholder_value(self, *, key: str, value: str) -> int:
        id_field = self._get_id_field(key=key, value=value)
        resolved_id = self._last_successful_id(id_field)

        if resolved_id is None:
            raise ToolCallError(f"no previous result with '{id_field}' to resolve placeholder '{value}' for {key}")

        return resolved_id

    def _get_id_field(self, *, key: str, value: str) -> str:
        placeholder = value.lower()

        if "level" in placeholder:
            return "level_id"
        if "space" in placeholder:
            return "space_id"

        if key == "level_id":
            return "level_id"
        if key == "space_id":
            return "space_id"

        raise ToolCallError(f"cannot determine placeholder type for '{value}' in field '{key}'")

    def _last_successful_id(self, id_field: str) -> int | None:
        for entry in reversed(self.results):
            if entry["status"] == "ok":
                result = entry["result"]
                parsed = self._parse_result(result)

                if parsed is None:
                    continue

                if id_field in parsed:
                    return parsed[id_field]
        return None

    def _parse_result(self, result: Any) -> dict[str, Any] | None:
        if isinstance(result, dict):
            payload = result
        elif isinstance(result, str):
            try:
                payload = json.loads(result)
            except json.JSONDecodeError:
                return None
        else:
            return None

        data = payload.get("data")
        if isinstance(data, list) and data:
            first_item = data[0]
            if isinstance(first_item, dict):
                return first_item | {"status": payload.get("status"), "message": payload.get("message")}

        return payload
