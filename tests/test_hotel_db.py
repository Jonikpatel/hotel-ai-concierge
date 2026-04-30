"""
test_hotel_db.py
----------------
Unit tests for the hotel database layer.
Run with: pytest tests/ -v
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.hotel_db import (  # noqa: E402
    fresh_state,
    find_available_room,
    find_reservation,
    process_checkin,
    process_checkout,
    place_room_service_order,
    create_housekeeping_ticket,
    create_maintenance_ticket,
    get_active_stay,
    lookup_menu_item,
    get_room_info,
    get_hotel_context,
)


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture
def state():
    """Fresh hotel state for each test."""
    return fresh_state()


@pytest.fixture
def checked_in_state(state):
    """State with one guest already checked in (Torres, room 303)."""
    # Torres is pre-loaded as checked_in in the config
    res = state["reservations"]["RES-2024-003"]
    state["rooms"]["303"]["status"] = "occupied"
    state["checked_in_guests"]["303"] = "RES-2024-003"
    res["status"] = "checked_in"
    res["room_assigned"] = "303"
    return state


# ── Room Lookup Tests ──────────────────────────────────────────────────────────

class TestRoomLookup:

    def test_find_available_standard_room(self, state):
        room = find_available_room(state, "standard")
        assert room is not None
        assert state["rooms"][room]["type"] == "standard"
        assert state["rooms"][room]["status"] == "available"

    def test_find_available_penthouse(self, state):
        room = find_available_room(state, "penthouse")
        assert room is not None
        assert state["rooms"][room]["type"] == "penthouse"

    def test_no_room_of_unknown_type(self, state):
        room = find_available_room(state, "nonexistent_type")
        assert room is None

    def test_get_room_info_returns_dict(self, state):
        info = get_room_info(state, "201")
        assert info is not None
        assert "type" in info
        assert "rate_usd" in info
        assert "amenities" in info
        assert isinstance(info["amenities"], list)

    def test_get_room_info_unknown_room(self, state):
        info = get_room_info(state, "999")
        assert info is None


# ── Reservation Tests ──────────────────────────────────────────────────────────

class TestReservationLookup:

    def test_find_by_last_name(self, state):
        res = find_reservation(state, "Wilson")
        assert res is not None
        assert "Wilson" in res["guest_name"]

    def test_find_by_last_name_case_insensitive(self, state):
        res = find_reservation(state, "wilson")
        assert res is not None

    def test_find_by_reservation_id(self, state):
        res = find_reservation(state, "RES-2024-001")
        assert res is not None
        assert res["id"] == "RES-2024-001"

    def test_find_by_email(self, state):
        res = find_reservation(state, "j.wilson@email.com")
        assert res is not None
        assert res["guest_name"] == "James Wilson"

    def test_find_nonexistent_reservation(self, state):
        res = find_reservation(state, "Nonexistent Person XYZ")
        assert res is None


# ── Check-In Tests ─────────────────────────────────────────────────────────────

class TestCheckIn:

    def test_successful_checkin(self, state):
        result = process_checkin(state, "RES-2024-001")
        assert result["success"] is True
        assert "room_number" in result
        assert result["guest_name"] == "James Wilson"
        assert result["wifi_password"] == "LuxStay2024"

    def test_checkin_assigns_correct_room_type(self, state):
        result = process_checkin(state, "RES-2024-001")
        assert result["success"] is True
        room_num = result["room_number"]
        assert state["rooms"][room_num]["type"] == "deluxe"

    def test_checkin_marks_room_occupied(self, state):
        result = process_checkin(state, "RES-2024-001")
        assert result["success"] is True
        room_num = result["room_number"]
        assert state["rooms"][room_num]["status"] == "occupied"

    def test_checkin_updates_reservation_status(self, state):
        process_checkin(state, "RES-2024-001")
        assert state["reservations"]["RES-2024-001"]["status"] == "checked_in"

    def test_duplicate_checkin_fails(self, state):
        process_checkin(state, "RES-2024-001")
        result2 = process_checkin(state, "RES-2024-001")
        assert result2["success"] is False
        assert "already checked in" in result2["error"].lower()

    def test_checkin_invalid_reservation(self, state):
        result = process_checkin(state, "RES-INVALID-999")
        assert result["success"] is False
        assert "not found" in result["error"].lower()

    def test_checkin_no_available_rooms(self, state):
        # Mark all penthouse rooms as unavailable
        for room_num, room in state["rooms"].items():
            if room["type"] == "penthouse":
                room["status"] = "occupied"
        result = process_checkin(state, "RES-2024-004")  # Emma Roberts, penthouse
        assert result["success"] is False

    def test_checkin_adds_to_checked_in_guests(self, state):
        result = process_checkin(state, "RES-2024-001")
        assert result["success"] is True
        room = result["room_number"]
        assert room in state["checked_in_guests"]
        assert state["checked_in_guests"][room] == "RES-2024-001"


# ── Check-Out Tests ────────────────────────────────────────────────────────────

class TestCheckOut:

    def test_successful_checkout(self, checked_in_state):
        result = process_checkout(checked_in_state, "303")
        assert result["success"] is True
        assert result["guest_name"] == "Michael Torres"
        assert result["total_usd"] > 0

    def test_checkout_calculates_correct_nights(self, checked_in_state):
        result = process_checkout(checked_in_state, "303")
        assert result["success"] is True
        assert result["nights"] >= 1

    def test_checkout_includes_tax(self, checked_in_state):
        result = process_checkout(checked_in_state, "303")
        assert result["taxes"] > 0

    def test_checkout_total_equals_sum(self, checked_in_state):
        result = process_checkout(checked_in_state, "303")
        expected = (
            result["room_charges"]
            + result["room_service_charges"]
            + result["taxes"]
        )
        assert abs(result["total_usd"] - round(expected, 2)) < 0.01

    def test_checkout_frees_room(self, checked_in_state):
        process_checkout(checked_in_state, "303")
        assert checked_in_state["rooms"]["303"]["status"] == "available"

    def test_checkout_removes_from_checked_in(self, checked_in_state):
        process_checkout(checked_in_state, "303")
        assert "303" not in checked_in_state["checked_in_guests"]

    def test_checkout_unoccupied_room_fails(self, state):
        result = process_checkout(state, "201")  # not occupied
        assert result["success"] is False


# ── Room Service Tests ─────────────────────────────────────────────────────────

class TestRoomService:

    def test_successful_order(self, checked_in_state):
        items = [{"item": "Club Sandwich", "quantity": 1, "price": 26}]
        result = place_room_service_order(checked_in_state, "303", items)
        assert result["success"] is True
        assert result["order_id"].startswith("ORD-")
        assert result["eta_minutes"] > 0

    def test_order_unoccupied_room_fails(self, state):
        items = [{"item": "Water", "quantity": 1, "price": 7}]
        result = place_room_service_order(state, "201", items)
        assert result["success"] is False

    def test_order_total_calculated_correctly(self, checked_in_state):
        items = [
            {"item": "Club Sandwich", "quantity": 2, "price": 26},
            {"item": "Sparkling Water", "quantity": 1, "price": 7},
        ]
        result = place_room_service_order(checked_in_state, "303", items)
        assert result["success"] is True
        assert result["total_usd"] == 59.0  # 2*26 + 7

    def test_order_added_to_state(self, checked_in_state):
        items = [{"item": "Coffee", "quantity": 1, "price": 8}]
        place_room_service_order(checked_in_state, "303", items)
        assert len(checked_in_state["room_service_orders"]) == 1

    def test_lookup_menu_item(self):
        item = lookup_menu_item("club sandwich")
        assert item is not None
        assert "Club Sandwich" in item["item"]
        assert "price" in item

    def test_lookup_menu_item_case_insensitive(self):
        item = lookup_menu_item("CHAMPAGNE")
        assert item is not None

    def test_lookup_nonexistent_menu_item(self):
        item = lookup_menu_item("purple dragon soup xyz")
        assert item is None


# ── Housekeeping Tests ─────────────────────────────────────────────────────────

class TestHousekeeping:

    def test_create_ticket_returns_id(self, state):
        result = create_housekeeping_ticket(state, "201", "Extra towels please")
        assert result["success"] is True
        assert result["ticket_id"].startswith("HK-")
        assert "eta" in result

    def test_urgent_ticket_has_short_eta(self, state):
        result = create_housekeeping_ticket(state, "201", "Urgent spill", priority="urgent")
        assert "15" in result["eta"] or "20" in result["eta"]

    def test_ticket_added_to_state(self, state):
        create_housekeeping_ticket(state, "201", "Towels")
        assert len(state["housekeeping_tickets"]) == 1

    def test_multiple_tickets(self, state):
        create_housekeeping_ticket(state, "201", "Towels")
        create_housekeeping_ticket(state, "202", "Pillows")
        assert len(state["housekeeping_tickets"]) == 2


# ── Maintenance Tests ──────────────────────────────────────────────────────────

class TestMaintenance:

    def test_create_maintenance_ticket(self, state):
        result = create_maintenance_ticket(state, "201", "AC not cooling")
        assert result["success"] is True
        assert result["ticket_id"].startswith("MNT-")

    def test_ticket_added_to_state(self, state):
        create_maintenance_ticket(state, "201", "Leaky tap")
        assert len(state["maintenance_tickets"]) == 1

    def test_low_priority_has_long_eta(self, state):
        result = create_maintenance_ticket(state, "201", "Light bulb out", priority="low")
        assert "4" in result["eta"]


# ── Hotel Context Tests ────────────────────────────────────────────────────────

class TestHotelContext:

    def test_context_is_string(self):
        ctx = get_hotel_context()
        assert isinstance(ctx, str)
        assert len(ctx) > 100

    def test_context_includes_hotel_name(self):
        ctx = get_hotel_context()
        assert "LuxStay" in ctx

    def test_context_includes_room_types(self):
        ctx = get_hotel_context()
        assert "Standard" in ctx or "Deluxe" in ctx

    def test_context_includes_menu(self):
        ctx = get_hotel_context()
        assert "Club Sandwich" in ctx or "Breakfast" in ctx

    def test_fresh_state_has_rooms(self):
        s = fresh_state()
        assert len(s["rooms"]) > 0

    def test_fresh_state_has_reservations(self):
        s = fresh_state()
        assert len(s["reservations"]) > 0

    def test_get_active_stay(self, checked_in_state):
        stay = get_active_stay(checked_in_state, "303")
        assert stay is not None
        assert stay["guest_name"] == "Michael Torres"

    def test_no_active_stay_unoccupied(self, state):
        stay = get_active_stay(state, "201")
        assert stay is None
