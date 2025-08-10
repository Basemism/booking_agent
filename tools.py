import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
RESTAURANT_NAME = os.getenv("RESTAURANT_NAME")
TOKEN = os.getenv("BEARER_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/x-www-form-urlencoded"
}

def handle_response(resp):
    """
    Attempts to parse the API response as JSON and handle common HTTP status codes.

    Args:
        resp (requests.Response): The HTTP response object from an API call.

    Returns:
        dict: Parsed JSON response if valid, otherwise a dictionary with an 'error' key
              containing the status code and message.
    """
    try:
        data = resp.json()
    except Exception:
        return {"error": f"Invalid response: {resp.text}", "status_code": resp.status_code}

    if resp.status_code == 200:
        return data
    elif resp.status_code == 400:
        return {"error": "Bad Request: Invalid parameters or business rule violation", "details": data, "status_code": 400}
    elif resp.status_code == 401:
        return {"error": "Unauthorized: Missing or invalid token", "details": data, "status_code": 401}
    elif resp.status_code == 404:
        return {"error": "Not Found: Restaurant or booking not found", "details": data, "status_code": 404}
    elif resp.status_code == 422:
        return {"error": "Unprocessable Entity: Validation errors", "details": data, "status_code": 422}
    else:
        return {"error": f"Unexpected error (status {resp.status_code})", "details": data, "status_code": resp.status_code}

def check_availability(visit_date, party_size, channel_code="ONLINE"):
    """
    Checks the availability of the restaurant for a specific date and party size.

    Args:
        visit_date (str): The date of the visit (YYYY-MM-DD).
        party_size (int): The number of people in the party.
        channel_code (str): The channel code for the booking (default is "ONLINE").

    Returns:
        dict: The API response containing availability information.
    """

    url = f"{BASE_URL}/api/ConsumerApi/v1/Restaurant/{RESTAURANT_NAME}/AvailabilitySearch"
    data = {"VisitDate": visit_date, "PartySize": party_size, "ChannelCode": channel_code}
    return handle_response(requests.post(url, headers=HEADERS, data=data))

def create_booking(data):
    """
    Creates a new booking in the restaurant's booking system.

    Args:
        data (dict): Booking details including date, time, party size, customer info, etc.

    Returns:
        dict: API response containing booking confirmation details or an error.
    """

    url = f"{BASE_URL}/api/ConsumerApi/v1/Restaurant/{RESTAURANT_NAME}/BookingWithStripeToken"
    return handle_response(requests.post(url, headers=HEADERS, data=data))

def get_booking(ref):
    """
    Retrieves booking details by booking reference.

    Args:
        ref (str): The booking reference identifier.

    Returns:
        dict: API response containing booking details or an error.
    """

    url = f"{BASE_URL}/api/ConsumerApi/v1/Restaurant/{RESTAURANT_NAME}/Booking/{ref}"
    return handle_response(requests.get(url, headers=HEADERS))

def update_booking(ref, updates):
    """
    Updates an existing booking with the provided fields.

    Args:
        ref (str): The booking reference identifier.
        updates (dict): Fields to update (e.g., date, time, party size).

    Returns:
        dict: API response confirming the updates or an error.
    """

    url = f"{BASE_URL}/api/ConsumerApi/v1/Restaurant/{RESTAURANT_NAME}/Booking/{ref}"
    return handle_response(requests.patch(url, headers=HEADERS, data=updates))

def cancel_booking(ref, reason_id):
    """
    Cancels a booking with a specified cancellation reason.

    Args:
        ref (str): The booking reference identifier.
        reason_id (int): Reason code for the cancellation.

    Returns:
        dict: API response confirming the cancellation or an error.
    """

    url = f"{BASE_URL}/api/ConsumerApi/v1/Restaurant/{RESTAURANT_NAME}/Booking/{ref}/Cancel"
    data = {
        "micrositeName": RESTAURANT_NAME,
        "bookingReference": ref,
        "cancellationReasonId": reason_id
    }
    return handle_response(requests.post(url, headers=HEADERS, data=data))
