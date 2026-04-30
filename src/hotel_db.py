"""
hotel_db.py
-----------
In-memory hotel database layer: rooms, reservations, guests,
room-service orders, and housekeeping/maintenance tickets.
Backed by hotel_config.json for initial data.
"""

import json
import random
import string
from datetime import datetime, date
from pathlib import Path
from typing import Optional

# ── Load config ────────────────────────────────────────────────────────────────
_CONFIG_PATH = Path(__file__).parent.parent / "data" / "hotel_config.json"


def _load_config() -> dict:
    with open(_CONFIG_PATH) as f:
        return json.load(f)


CONFIG = _load_config()
HOTEL = CONFIG["hotel"]
ROOM_TYPES = CONFIG["room_types"]
MENU = CONFIG["room_service_menu"]
FACILITIES = CONFIG["facilities"]
LOCAL = CONFIG["local_recommendations"]


# ── In-memory state (reloaded fresh each Streamlit session via st.session_state) ──

def fresh_state() -> dict:
    """Return a clean hotel state dict loaded from config."""
    rooms = {r["number"]: dict(r) for r in CONFIG["rooms"]}
    reservations = {r["id"]: dict(r) for r in CONFIG["reservations"]}
    return {
        "rooms": rooms,
        "reservations": reservations,
        "checked_in_guests": {},   # room_number → reservation_id
        "room_service_orders": [],
        "housekeeping_tickets": [],
        "maintenance_tickets": [],
        "messages": [],            # conversation history for AI
    }


# ── Utility ────────────────────────────────────────────────────────────────────

def _random_id(prefix: str, length: int = 6) -> str:
    chars = string.ascii_uppercase + string.digits
    return f"{prefix}-{''.join(random.choices(chars, k=length))}"


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


# ── Room Lookup ────────────────────────────────────────────────────────────────

def find_available_room(state: dict, room_type: str) -> Optional[str]:
    """Return the first available room of the given type, or None."""
    for number, room in state["rooms"].items():
        if room["type"] == room_type and room["status"] == "available":
            return number
    return None


def get_room_info(state: dict, room_number: str) -> Optional[dict]:
    room = state["rooms"].get(room_number)
    if not room:
        return None
    rt = ROOM_TYPES[room["type"]]
    return {
        "number": room_number,
        "type": rt["label"],
        "rate_usd": rt["rate_usd"],
        "amenities": rt["amenities"],
        "status": room["status"],
    }


# ── Reservation Lookup ─────────────────────────────────────────────────────────

def find_reservation(state: dict, query: str) -> Optional[dict]:
    """
    Find a reservation by:
    - Reservation ID (e.g. RES-2024-001)
    - Guest last name (case-insensitive)
    - Guest email
    """
    q = query.strip().lower()
    for res_id, res in state["reservations"].items():
        if q in res_id.lower():
            return res
        last_name = res["guest_name"].split()[-1].lower()
        if q == last_name or q == res["email"].lower():
            return res
    return None


def get_active_stay(state: dict, room_number: str) -> Optional[dict]:
    """Return the reservation for a currently checked-in room."""
    res_id = state["checked_in_guests"].get(room_number)
    if res_id:
        return state["reservations"].get(res_id)
    return None


# ── Check-In ───────────────────────────────────────────────────────────────────

def process_checkin(state: dict, reservation_id: str) -> dict:
    """
    Complete check-in for a reservation:
    - Assign an available room
    - Update reservation and room status
    - Return check-in summary
    """
    res = state["reservations"].get(reservation_id)
    if not res:
        return {"success": False, "error": "Reservation not found."}

    if res["status"] == "checked_in":
        return {
            "success": False,
            "error": f"Guest already checked in to room {res.get('room_assigned', '?')}.",
        }

    room_number = find_available_room(state, res["room_type"])
    if not room_number:
        return {
            "success": False,
            "error": f"No available {ROOM_TYPES[res['room_type']]['label']} rooms right now.",
        }

    # Update state
    res["status"] = "checked_in"
    res["room_assigned"] = room_number
    res["actual_checkin"] = _now()
    state["rooms"][room_number]["status"] = "occupied"
    state["checked_in_guests"][room_number] = reservation_id

    rt = ROOM_TYPES[res["room_type"]]
    return {
        "success": True,
        "guest_name": res["guest_name"],
        "room_number": room_number,
        "room_type": rt["label"],
        "floor": room_number[:2] if len(room_number) == 4 else room_number[0],
        "rate_usd": rt["rate_usd"],
        "amenities": rt["amenities"],
        "check_out_date": res["check_out"],
        "loyalty_tier": res.get("loyalty_tier", "Member"),
        "special_requests": res.get("special_requests", ""),
        "wifi_password": "LuxStay2024",
        "checkin_time": res["actual_checkin"],
    }


# ── Check-Out ──────────────────────────────────────────────────────────────────

def process_checkout(state: dict, room_number: str) -> dict:
    """
    Complete check-out: compute bill, free room.
    """
    res = get_active_stay(state, room_number)
    if not res:
        return {"success": False, "error": f"No active stay found for room {room_number}."}

    rt = ROOM_TYPES[res["room_type"]]

    # Calculate nights
    try:
        ci = date.fromisoformat(res["check_in"])
        co = date.fromisoformat(res["check_out"])
        nights = max((co - ci).days, 1)
    except Exception:
        nights = 1

    room_charges = rt["rate_usd"] * nights

    # Sum room-service charges for this room
    rs_charges = sum(
        o["total"]
        for o in state["room_service_orders"]
        if o["room_number"] == room_number and o["status"] != "cancelled"
    )

    taxes = round((room_charges + rs_charges) * 0.15, 2)
    total = round(room_charges + rs_charges + taxes, 2)

    # Update state
    res["status"] = "checked_out"
    res["actual_checkout"] = _now()
    state["rooms"][room_number]["status"] = "available"
    del state["checked_in_guests"][room_number]

    return {
        "success": True,
        "guest_name": res["guest_name"],
        "room_number": room_number,
        "room_type": rt["label"],
        "nights": nights,
        "check_in": res["check_in"],
        "check_out": res["check_out"],
        "room_charges": room_charges,
        "room_service_charges": rs_charges,
        "taxes": taxes,
        "total_usd": total,
        "checkout_time": res["actual_checkout"],
    }


# ── Room Service ───────────────────────────────────────────────────────────────

def place_room_service_order(
    state: dict,
    room_number: str,
    items: list[dict],
) -> dict:
    """
    Place a room-service order.
    items: [{"item": str, "quantity": int, "price": float}, ...]
    """
    if room_number not in state["checked_in_guests"]:
        return {"success": False, "error": f"Room {room_number} is not currently occupied."}

    total = sum(i["price"] * i.get("quantity", 1) for i in items)
    order_id = _random_id("ORD")
    eta_minutes = random.randint(20, 45)

    order = {
        "order_id": order_id,
        "room_number": room_number,
        "items": items,
        "total": round(total, 2),
        "status": "confirmed",
        "placed_at": _now(),
        "eta_minutes": eta_minutes,
    }
    state["room_service_orders"].append(order)

    return {
        "success": True,
        "order_id": order_id,
        "room_number": room_number,
        "items": items,
        "total_usd": order["total"],
        "eta_minutes": eta_minutes,
    }


def lookup_menu_item(name: str) -> Optional[dict]:
    """Find a menu item by approximate name match across all categories."""
    name_lower = name.lower()
    for category, items in MENU.items():
        for item in items:
            if name_lower in item["item"].lower() or item["item"].lower() in name_lower:
                return {"category": category, **item}
    return None


# ── Housekeeping ───────────────────────────────────────────────────────────────

def create_housekeeping_ticket(
    state: dict,
    room_number: str,
    request: str,
    priority: str = "normal",
) -> dict:
    ticket_id = _random_id("HK")
    eta_map = {"urgent": "15–20 min", "normal": "30–45 min", "low": "2 hours"}

    ticket = {
        "ticket_id": ticket_id,
        "room_number": room_number,
        "request": request,
        "priority": priority,
        "status": "open",
        "created_at": _now(),
        "eta": eta_map.get(priority, "30–45 min"),
    }
    state["housekeeping_tickets"].append(ticket)

    return {
        "success": True,
        "ticket_id": ticket_id,
        "request": request,
        "eta": ticket["eta"],
    }


# ── Maintenance ────────────────────────────────────────────────────────────────

def create_maintenance_ticket(
    state: dict,
    room_number: str,
    issue: str,
    priority: str = "normal",
) -> dict:
    ticket_id = _random_id("MNT")
    eta_map = {"urgent": "15 min", "normal": "1 hour", "low": "4 hours"}

    ticket = {
        "ticket_id": ticket_id,
        "room_number": room_number,
        "issue": issue,
        "priority": priority,
        "status": "open",
        "created_at": _now(),
        "eta": eta_map.get(priority, "1 hour"),
    }
    state["maintenance_tickets"].append(ticket)

    return {
        "success": True,
        "ticket_id": ticket_id,
        "issue": issue,
        "eta": ticket["eta"],
    }


# ── Hotel Info ─────────────────────────────────────────────────────────────────

def get_hotel_context() -> str:
    """Build a rich context string about the hotel for the AI system prompt."""
    room_type_desc = "\n".join(
        f"  - {v['label']}: ${v['rate_usd']}/night. Amenities: {', '.join(v['amenities'])}"
        for v in ROOM_TYPES.values()
    )
    menu_desc = []
    for cat, items in MENU.items():
        lines = ", ".join(f"{i['item']} (${i['price']})" for i in items)
        menu_desc.append(f"  {cat.title()}: {lines}")

    facilities_desc = "\n".join(
        f"  - {k.replace('_', ' ').title()}: {v}" for k, v in FACILITIES.items()
    )

    rest = "\n".join(f"  - {r}" for r in LOCAL["restaurants"])
    attr = "\n".join(f"  - {a}" for a in LOCAL["attractions"])
    trans = "\n".join(f"  - {t}" for t in LOCAL["transport"])

    return f"""
HOTEL: {HOTEL['name']}
Address: {HOTEL['address']}
Phone: {HOTEL['phone']} | Email: {HOTEL['email']}
Check-in: {HOTEL['check_in_time']} | Check-out: {HOTEL['check_out_time']}

ROOM TYPES:
{room_type_desc}

ROOM SERVICE MENU:
{chr(10).join(menu_desc)}

HOTEL FACILITIES:
{facilities_desc}

LOCAL RECOMMENDATIONS:
Restaurants: {rest}
Attractions: {attr}
Transport: {trans}
""".strip()
