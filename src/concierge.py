# concierge.py -- AI concierge engine powered by Groq llama-3.3-70b
import os
import json
import re
from typing import Optional

from groq import Groq

from src.hotel_db import (
    get_hotel_context,
    find_reservation,
    process_checkin,
    process_checkout,
    place_room_service_order,
    lookup_menu_item,
    create_housekeeping_ticket,
    create_maintenance_ticket,
    get_active_stay,
)

GROQ_MODEL = "llama-3.3-70b-versatile"

_SYSTEM_PROMPT_LINES = [
    "You are Aria, the AI concierge at {hotel_name}, a luxury 5-star Manhattan hotel.",
    "You are warm, elegant, professional. Keep replies concise: 2-3 sentences.",
    "",
    "{hotel_context}",
    "",
    "INSTRUCTIONS:",
    "At the end of EVERY reply, append an action block in this EXACT format:",
    "##ACTION##",
    '{"action":"NAME","params":{...}}',
    "##END##",
    "",
    "Action names and params:",
    'CHECK_IN      {"reservation_query":"<last name or ID>"}',
    'CHECK_OUT     {"room_number":"<room>"}',
    'ROOM_SERVICE  {"room_number":"<room>","items":[{"item":"<name>","quantity":1}]}',
    'HOUSEKEEPING  {"room_number":"<room>","request":"<what>","priority":"normal"}',
    'MAINTENANCE   {"room_number":"<room>","issue":"<desc>","priority":"normal"}',
    'NONE          {}',
    "",
    "Rules:",
    "- Use NONE for greetings, questions, info, recommendations.",
    "- NEVER wrap the action block in markdown code fences.",
    "- ALWAYS include ##ACTION## and ##END## markers.",
    "- For check-in without a name, ask for last name or reservation ID.",
]


def _build_system(hotel_name: str, hotel_context: str) -> str:
    lines = [
        ln.replace("{hotel_name}", hotel_name).replace("{hotel_context}", hotel_context)
        for ln in _SYSTEM_PROMPT_LINES
    ]
    return "\n".join(lines)


def _get_client() -> Groq:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets.get("GROQ_API_KEY")
        except Exception:
            pass
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found. "
            "Paste your key from console.groq.com into the sidebar."
        )
    return Groq(api_key=api_key)


def _parse_action(text: str) -> Optional[dict]:
    # Primary: ##ACTION## marker
    m = re.search(r"##ACTION##\s*(\{.*?\})\s*##END##", text, re.DOTALL)
    if m:
        try:
            data = json.loads(m.group(1))
            if isinstance(data, dict) and "action" in data:
                return data
        except (json.JSONDecodeError, ValueError):
            pass

    # Fallback: any bare JSON with "action" key
    for m in re.finditer(r"\{[^{}]{0,300}\}", text, re.DOTALL):
        try:
            data = json.loads(m.group(0))
            if isinstance(data, dict) and "action" in data:
                return data
        except (json.JSONDecodeError, ValueError):
            continue

    return None


def _clean_response(text: str) -> str:
    cleaned = re.sub(r"##ACTION##.*?##END##", "", text, flags=re.DOTALL)
    cleaned = re.sub(r'\{"action"\s*:.*?\}', "", cleaned, flags=re.DOTALL)
    return cleaned.strip()


def _execute_action(action_block: dict, state: dict) -> Optional[dict]:
    try:
        action = str(action_block.get("action", "NONE")).upper().strip()
        params = action_block.get("params", {})
        if not isinstance(params, dict):
            params = {}

        if action == "CHECK_IN":
            query = str(params.get("reservation_query", "")).strip()
            res = find_reservation(state, query)
            if not res:
                return {
                    "action": "CHECK_IN", "success": False,
                    "error": "No reservation found. Please check the name or ID.",
                }
            result = process_checkin(state, res["id"])
            result["action"] = "CHECK_IN"
            return result

        if action == "CHECK_OUT":
            room = str(params.get("room_number", "")).strip()
            result = process_checkout(state, room)
            result["action"] = "CHECK_OUT"
            return result

        if action == "ROOM_SERVICE":
            room = str(params.get("room_number", "")).strip()
            requested = params.get("items", [])
            if not isinstance(requested, list):
                requested = []
            resolved, unresolved = [], []
            for req in requested:
                if not isinstance(req, dict):
                    continue
                item_name = str(req.get("item", ""))
                qty = max(int(req.get("quantity", 1)), 1)
                found = lookup_menu_item(item_name)
                if found:
                    resolved.append({
                        "item": found["item"],
                        "quantity": qty,
                        "price": found["price"],
                    })
                else:
                    unresolved.append(item_name)
            if not resolved:
                return {
                    "action": "ROOM_SERVICE", "success": False,
                    "error": f"Could not match these items: {unresolved}",
                }
            result = place_room_service_order(state, room, resolved)
            result["action"] = "ROOM_SERVICE"
            result["unresolved_items"] = unresolved
            return result

        if action == "HOUSEKEEPING":
            result = create_housekeeping_ticket(
                state,
                room_number=str(params.get("room_number", "")),
                request=str(params.get("request", "")),
                priority=str(params.get("priority", "normal")),
            )
            result["action"] = "HOUSEKEEPING"
            return result

        if action == "MAINTENANCE":
            issue = str(params.get("issue", ""))
            priority = str(params.get("priority", "normal"))
            if any(w in issue.lower() for w in ["fire", "flood", "smoke", "gas"]):
                priority = "urgent"
            result = create_maintenance_ticket(
                state,
                room_number=str(params.get("room_number", "")),
                issue=issue,
                priority=priority,
            )
            result["action"] = "MAINTENANCE"
            return result

        return None  # NONE action

    except Exception as exc:
        return {"action": "ERROR", "success": False, "error": str(exc)}


def chat(user_message: str, state: dict, current_room: Optional[str] = None) -> tuple:
    from src.hotel_db import HOTEL
    try:
        system = _build_system(HOTEL["name"], get_hotel_context())

        context_prefix = ""
        if current_room:
            stay = get_active_stay(state, current_room)
            if stay:
                context_prefix = f"[Context: {stay['guest_name']}, Room {current_room}] "

        messages = list(state.get("messages", []))
        full_input = context_prefix + user_message
        messages.append({"role": "user", "content": full_input})

        client = _get_client()
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "system", "content": system}] + messages,
            max_tokens=800,
            temperature=0.5,
        )

        raw_text = response.choices[0].message.content or ""
        action_block = _parse_action(raw_text)
        action_result = _execute_action(action_block, state) if action_block else None
        display_text = _clean_response(raw_text) or "How may I assist you?"

        state["messages"].append({"role": "user", "content": full_input})
        state["messages"].append({"role": "assistant", "content": display_text})
        if len(state["messages"]) > 40:
            state["messages"] = state["messages"][-40:]

        return display_text, action_result

    except ValueError as exc:
        return str(exc), None
    except Exception as exc:
        return f"I apologise -- a brief issue occurred: {str(exc)[:100]}", None
