from datetime import datetime, timedelta

# Zone classification for Indian locations
METRO_CITIES = [
    'mumbai', 'delhi', 'new delhi', 'bengaluru', 'bangalore', 
    'chennai', 'kolkata', 'hyderabad', 'pune', 'ahmedabad', 'gurugram', 'noida', 'thane'
]

REMOTE_STATES_AND_REGIONS = [
    'jammu and kashmir', 'j&k', 'ladakh', 'assam', 'meghalaya', 'sikkim', 
    'nagaland', 'manipur', 'mizoram', 'tripura', 'arunachal pradesh', 
    'andaman', 'nicobar', 'lakshadweep'
]

DELIVERY_STAGES = [
    {"step": 1, "title": "Order Placed & Confirmed", "desc": "Art specifications verified & raw cotton canvas prepped."},
    {"step": 2, "title": "Hand-Painting & Drying", "desc": "Brushwork active. Protective coating applied to canvas art."},
    {"step": 3, "title": "Wooden Easel Fitting (Faceless)", "desc": "Faceless canvas mounted onto handcrafted wooden easel display stand."},
    {"step": 4, "title": "Reinforced Packaging", "desc": "Corner guards added & enclosed in protective shipping box."},
    {"step": 5, "title": "Out for Delivery", "desc": "Handed to courier express partner. Dispatched to destination address."}
]

def calculate_delivery_estimate(city="", state="", pincode="", total_amount=0.0):
    """
    Location-dependent shipping fee calculator:
    - Metro Cities: ₹80 (Free above ₹1,500) | 3-5 Business Days
    - Rest of India: ₹120 (Free above ₹1,500) | 4-6 Business Days
    - Remote/North-East/J&K: ₹180 (Free above ₹2,500) | 6-9 Business Days
    """
    city_clean = city.strip().lower()
    state_clean = state.strip().lower()
    pincode_clean = pincode.strip()

    today = datetime.now()
    
    # Determine location tier
    is_remote = any(r in state_clean for r in REMOTE_STATES_AND_REGIONS) or any(r in city_clean for r in REMOTE_STATES_AND_REGIONS)
    is_metro = any(m in city_clean for m in METRO_CITIES)

    if is_remote:
        zone_name = "Remote / Special Region"
        min_days, max_days = 6, 9
        base_fee = 180
        free_threshold = 2500
    elif is_metro:
        zone_name = "Metro City Express"
        min_days, max_days = 3, 5
        base_fee = 80
        free_threshold = 1500
    else:
        zone_name = "Standard Regional Delivery"
        min_days, max_days = 4, 6
        base_fee = 120
        free_threshold = 1500

    is_free = total_amount >= free_threshold
    shipping_fee = 0 if is_free else base_fee

    est_start = today + timedelta(days=min_days)
    est_end = today + timedelta(days=max_days)

    return {
        "zone_name": zone_name,
        "estimated_start": est_start.strftime("%b %d, %Y"),
        "estimated_end": est_end.strftime("%b %d, %Y"),
        "delivery_window": f"{min_days}-{max_days} Business Days",
        "shipping_fee": shipping_fee,
        "base_fee": base_fee,
        "is_free_shipping": is_free,
        "free_threshold": free_threshold,
        "packaging_type": "Reinforced Box with Protective Corner Guards"
    }

def get_order_tracking_info(order_data):
    if not order_data:
        return None

    current_step = order_data["current_step"]
    stages_response = []

    for stage in DELIVERY_STAGES:
        status = "completed" if stage["step"] < current_step else ("active" if stage["step"] == current_step else "pending")
        stages_response.append({
            "step": stage["step"],
            "title": stage["title"],
            "desc": stage["desc"],
            "status": status
        })

    return {
        "order_id": order_data["order_id"],
        "customer_name": order_data["customer_name"],
        "city": order_data["city"],
        "total_amount": order_data["total_amount"],
        "items": order_data["items_json"],
        "carrier": order_data["carrier"],
        "tracking_number": order_data["tracking_number"],
        "created_at": order_data["created_at"],
        "current_step": current_step,
        "step_status": order_data["step_status"],
        "stages": stages_response
    }
