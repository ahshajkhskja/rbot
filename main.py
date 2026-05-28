import time
import json
import hashlib
import requests

URL_FREE = "https://neriumsearch.onrender.com/api/collectibles/free"
URL_PAID = "https://neriumsearch.onrender.com/api/collectibles/paid"
URL_WEBSITE = "https://neriumsearch.onrender.com/api/collectibles/website"

WEBHOOK_PAID = "https://discord.com/api/webhooks/1509547466544906261/V2bEbaQj0prbnoe2Dm8U2cuuAIvNE8ckc-xXcIzYw9oJ-GYcWnpsVL1m9-ns8l98nQs-"
WEBHOOK_REGULAR = "https://discord.com/api/webhooks/1509547466544906261/V2bEbaQj0prbnoe2Dm8U2cuuAIvNE8ckc-xXcIzYw9oJ-GYcWnpsVL1m9-ns8l98nQs-"
WEBHOOK_WEB_UGC = "https://discord.com/api/webhooks/1509547466544906261/V2bEbaQj0prbnoe2Dm8U2cuuAIvNE8ckc-xXcIzYw9oJ-GYcWnpsVL1m9-ns8l98nQs-"

ROLE_REGULAR = "1509514820913729557"
ROLE_WEB_UGC = "1509514936165076992"
ROLE_PAID = "1509514936165076992"

POLL_INTERVAL = 3

session = requests.Session()

def get_detailed_roblox_info(asset_id):
    item_name = "Unknown UGC Item"
    creator_name = "Unknown Creator"
    creator_id = ""
    creator_type = "User"
    price_val = "FREE"
    total_quantity = "N/A"
    sale_location = "Catalog Website"
    game_url = None
    game_name = "N/A"
    thumb_url = None
    item_type_desc = "UGC Item Went Limited"

    try:
        res = session.get(
            f"https://economy.roblox.com/v2/assets/{asset_id}/details",
            timeout=8
        )

        if res.ok:
            det = res.json()

            item_name = det.get("Name", item_name)

            creator = det.get("Creator", {})
            creator_name = creator.get("Name", creator_name)
            creator_id = creator.get("CreatorTargetId", "")
            creator_type = creator.get("CreatorType", "User")

            price = det.get("PriceInRobux", 0)

            if price and price > 0:
                price_val = f"{price} Robux"
            else:
                price_val = "FREE"

            collectible_details = det.get("CollectiblesItemDetails", {})

            total_qty = collectible_details.get("TotalQuantity")

            if total_qty is not None:
                total_quantity = str(total_qty)

            sale_location_data = det.get("SaleLocation", {})
            universe_ids = sale_location_data.get("UniverseIds", [])

            if universe_ids:
                sale_location = "In-Game Only"

                target_universe = universe_ids[0]

                univ_res = session.get(
                    f"https://games.roblox.com/v1/games?universeIds={target_universe}",
                    timeout=8
                )

                if univ_res.ok:
                    game_data = univ_res.json().get("data", [])

                    if game_data:
                        game = game_data[0]

                        root_place = game.get("rootPlaceId")
                        game_name = game.get("name", "Target Experience")

                        if root_place:
                            game_url = f"https://www.roblox.com/games/{root_place}/"

            is_limited = collectible_details.get("IsLimited")

            if is_limited:
                item_type_desc = "UGC Limited Detected"

    except Exception:
        pass

    try:
        thumb_res = session.get(
            f"https://thumbnails.roblox.com/v1/assets?assetIds={asset_id}&size=420x420&format=Png&isCircular=false",
            timeout=8
        )

        if thumb_res.ok:
            thumb_data = thumb_res.json().get("data", [])

            if thumb_data:
                thumb_url = thumb_data[0].get("imageUrl")

    except Exception:
        pass

    return {
        "name": item_name,
        "creator": creator_name,
        "creator_link": f"https://www.roblox.com/groups/{creator_id}/" if str(creator_type) == "Group" else f"https://www.roblox.com/users/{creator_id}/profile",
        "price": price_val,
        "quantity": total_quantity,
        "location": sale_location,
        "game_name": game_name,
        "game_url": game_url,
        "thumb": thumb_url,
        "type_desc": item_type_desc
    }

def send_premium_webhook(asset_id, stream_type):
    info = get_detailed_roblox_info(asset_id)

    if stream_type == "paid":
        webhook_url = WEBHOOK_PAID
        role_id = ROLE_PAID
        embed_color = 15158332
        location_status = "In-Game Only" if info["game_url"] else "Web UGC"

    elif stream_type == "website":
        webhook_url = WEBHOOK_WEB_UGC
        role_id = ROLE_WEB_UGC
        embed_color = 3066993
        location_status = "Web UGC"

    else:
        webhook_url = WEBHOOK_REGULAR
        role_id = ROLE_REGULAR
        embed_color = 3447003
        location_status = "In-Game Only" if info["game_url"] else "Web UGC"

    item_url = f"https://www.roblox.com/catalog/{asset_id}/"
    try_on_url = f"https://www.roblox.com/catalog/{asset_id}/#try-on-item"

    description = (
        f"✨ **{info['type_desc']}**\n"
        f"🎮 **{location_status}**\n"
        f"🌐 [Roblox Page]({item_url}) │ 👕 [Try On]({try_on_url})"
    )

    location_value = f"[{info['game_name']}]({info['game_url']})" if info["game_url"] else "Catalog Website"

    fields = [
        {"name": "Sale Location", "value": location_value, "inline": False},
        {"name": "Price", "value": "FREE" if stream_type in ["free", "website"] else str(info["price"]), "inline": True},
        {"name": "Quantity", "value": str(info["quantity"]), "inline": True},
        {"name": "Creator", "value": f"[{info['creator']}]({info['creator_link']})", "inline": True}
    ]

    embed = {
        "author": {
            "name": "Rolimon's"
        },
        "title": info["name"],
        "url": item_url,
        "description": description,
        "color": embed_color,
        "fields": fields,
        "footer": {
            "text": f"Nerium Engine • Asset ID: {asset_id}"
        }
    }

    if info["thumb"] and str(info["thumb"]).startswith("http"):
        embed["thumbnail"] = {"url": info["thumb"]}

    payload = {
        "embeds": [embed]
    }

    if role_id:
        payload["content"] = f"<@&{role_id}>"
        payload["allowed_mentions"] = {"roles": [role_id]}
    else:
        payload["allowed_mentions"] = {"parse": []}

    try:
        session.post(webhook_url, json=payload, timeout=8)
    except Exception:
        pass

def fetch_data(url):
    try:
        response = session.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=8
        )

        if response.ok:
            data = response.json()
            return data if isinstance(data, list) else [data]

    except Exception:
        pass

    return []

def monitor():
    processed_hashes = set()

    while True:
        try:
            for item in fetch_data(URL_FREE):
                if isinstance(item, dict) and "free" in item:
                    h = hashlib.md5(json.dumps(item, sort_keys=True).encode()).hexdigest()

                    if h not in processed_hashes:
                        processed_hashes.add(h)
                        send_premium_webhook(str(item["free"]), "free")

            for item in fetch_data(URL_PAID):
                if isinstance(item, dict) and "paid" in item:
                    h = hashlib.md5(json.dumps(item, sort_keys=True).encode()).hexdigest()

                    if h not in processed_hashes:
                        processed_hashes.add(h)
                        send_premium_webhook(str(item["paid"]), "paid")

            for item in fetch_data(URL_WEBSITE):
                if isinstance(item, dict):
                    asset_id = item.get("website") or item.get("free") or item.get("paid")

                    if asset_id:
                        h = hashlib.md5(json.dumps(item, sort_keys=True).encode()).hexdigest()

                        if h not in processed_hashes:
                            processed_hashes.add(h)
                            send_premium_webhook(str(asset_id), "website")

        except Exception:
            pass

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    monitor()
