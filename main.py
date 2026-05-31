import time
import json
import hashlib
import requests

URL_FREE = "https://neriumsearch.onrender.com/api/collectibles/free"
URL_PAID = "https://neriumsearch.onrender.com/api/collectibles/paid"
URL_WEBSITE = "https://neriumsearch.onrender.com/api/collectibles/website"

WEBHOOK_FREE = "https://discord.com/api/webhooks/1509547466544906261/V2bEbaQj0prbnoe2Dm8U2cuuAIvNE8ckc-xXcIzYw9oJ-GYcWnpsVL1m9-ns8l98nQs-"
WEBHOOK_PAID = "https://discord.com/api/webhooks/1509558004918390854/SwdjBDN2iOQgufwjoEz4Es2k2MOGRLwvMbouzwq09LtCx3cao3AyQpKnKLIUNAkEmPUq"
WEBHOOK_WEB_UGC = "https://discord.com/api/webhooks/1509558078318837923/44tRzz1F1sqoRKAzIonHqpNOVVIS_funokLq8ddhpVvPE8c8jJnEJXm1R1ZvVMwACcy2"

ROLE_FREE = "1509514820913729557"
ROLE_PAID = "1509514936165076992"
ROLE_WEB_UGC = "1509533927134593105"

POLL_INTERVAL = 1
ROBLOX_API_KEY = "wF5muFy4yEeh9oBuqtDlPDnEWfReN1W1cVPybDR1/IvqRrufZXlKaGJHY2lPaUpTVXpJMU5pSXNJbXRwWkNJNkluTnBaeTB5TURJeExUQTNMVEV6VkRFNE9qVXhPalE1V2lJc0luUjVjQ0k2SWtwWFZDSjkuZXlKaGRXUWlPaUpTYjJKc2IzaEpiblJsY201aGJDSXNJbWx6Y3lJNklrTnNiM1ZrUVhWMGFHVnVkR2xqWVhScGIyNVRaWEoyYVdObElpd2lZbUZ6WlVGd2FVdGxlU0k2SW5kR05XMTFSbmswZVVWbGFEbHZRblZ4ZEVSc1VFUnVSVmRtVW1WT01WY3hZMVpRZVdKRVVqRXZTWFp4VW5KMVppSXNJbTkzYm1WeVNXUWlPaUl4TURrNE5USTJOekE1TmlJc0ltVjRjQ0k2TVRjNE1EQXhOVEV6TVN3aWFXRjBJam94Tnpnd01ERXhOVE14TENKdVltWWlPakUzT0RBd01URTFNekY5LmRJSHRSN1Vobzd6MF9yR3EzdGVqSmZ6M3Myd0JqdjJuZlhOdW15am50UXZCcUU5czN2bmhES1pnMzlVRTdMcWM2S1FHaXRkN2k3NHRoQlRpTzBJbUVsZ1BjZ1pkQjJMbC1VbDU1aE96YVd4RVhyUTdtV3FDempCT0NHelp2Vm0weXpCS1NUb1hyaVVaQWdFeC04b2dEcndXd1FiNi1TbTBFdk1xVEJtWndRLUNRdVFpYWwwQlppOHkwVXo2MU51YVBYRXF3eUxBcmhGeG1ZOFNRRUxMUE9fa1RxYnEtZHNvc1VjUzZnZEFWVTU2TEpOMFJoSGl1ZURKWWg0WG5zOC1felFYT0RlNmZJT2hHRE4xTndtYXpMcThMbnc0UURjZExMcDYyWlN1cFotcnVYbEl4a1ExQVVrVzVBVC05X1J4VnFvVEJRQXNJTU5tRV9sNkNaTTF1UQ=="

session = requests.Session()
session.headers.update({"x-api-key": ROBLOX_API_KEY})

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

    try:
        res = session.get(f"https://economy.roblox.com/v2/assets/{asset_id}/details", timeout=8)
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
                univ_res = session.get(f"https://games.roblox.com/v1/games?universeIds={target_universe}", timeout=8)
                if univ_res.ok:
                    game_data = univ_res.json().get("data", [])
                    if game_data:
                        game = game_data[0]
                        root_place = game.get("rootPlaceId")
                        game_name = game.get("name", "Target Experience")
                        if root_place:
                            game_url = f"https://www.roblox.com/games/{root_place}/"
            else:
                sale_location = "Web UGC"
    except Exception:
        pass

    thumb_session = requests.Session()
    thumb_session.headers.update({"User-Agent": "Mozilla/5.0"})

    for attempt in range(5):
        try:
            thumb_res = thumb_session.get(
                f"https://thumbnails.roblox.com/v1/assets?assetIds={asset_id}&size=420x420&format=Png&isCircular=false",
                timeout=8
            )
            if thumb_res.ok:
                thumb_data = thumb_res.json().get("data", [])
                if thumb_data:
                    state = thumb_data[0].get("state", "")
                    url = thumb_data[0].get("imageUrl")
                    if url and url.startswith("http") and state != "Blocked":
                        thumb_url = url
                        break
        except Exception:
            pass

        if not thumb_url:
            try:
                batch_res = thumb_session.post(
                    "https://thumbnails.roblox.com/v1/batch",
                    json=[{
                        "requestId": f"{asset_id}::Asset:420x420:png:regular",
                        "type": "Asset",
                        "targetId": int(asset_id),
                        "format": "png",
                        "size": "420x420"
                    }],
                    timeout=8
                )
                if batch_res.ok:
                    batch_data = batch_res.json().get("data", [])
                    if batch_data:
                        state = batch_data[0].get("state", "")
                        url = batch_data[0].get("imageUrl")
                        if url and url.startswith("http") and state != "Blocked":
                            thumb_url = url
                            break
            except Exception:
                pass

        if not thumb_url:
            try:
                collect_res = thumb_session.get(
                    f"https://thumbnails.roblox.com/v1/assets?assetIds={asset_id}&returnPolicy=PlaceHolder&size=420x420&format=Png&isCircular=false",
                    timeout=8
                )
                if collect_res.ok:
                    collect_data = collect_res.json().get("data", [])
                    if collect_data:
                        url = collect_data[0].get("imageUrl")
                        if url and url.startswith("http"):
                            thumb_url = url
                            break
            except Exception:
                pass

        if thumb_url:
            break
        time.sleep(2)

    if not thumb_url:
        thumb_url = f"https://tr.rbxcdn.com/{asset_id}/420/420/Image/Png"

    return {
        "name": item_name,
        "creator": creator_name,
        "creator_link": f"https://www.roblox.com/groups/{creator_id}/" if str(creator_type) == "Group" else f"https://www.roblox.com/users/{creator_id}/profile",
        "price": price_val,
        "quantity": total_quantity,
        "location": sale_location,
        "game_name": game_name,
        "game_url": game_url,
        "thumb": thumb_url
    }

def send_premium_webhook(asset_id, stream_type):
    info = get_detailed_roblox_info(asset_id)

    if stream_type == "paid":
        webhook_url = WEBHOOK_PAID
        role_id = ROLE_PAID
        embed_color = 15158332
        sale_emoji = "💎"
        sale_text = "Buy In Catalog"
    elif stream_type == "website":
        webhook_url = WEBHOOK_WEB_UGC
        role_id = ROLE_WEB_UGC
        embed_color = 3066993
        sale_emoji = "🧺"
        sale_text = "Go Get This Web Fast"
    else:
        webhook_url = WEBHOOK_FREE
        role_id = ROLE_FREE
        embed_color = 3447003
        sale_emoji = "🛒"
        sale_text = "Get in-game without captcha!"

    item_url = f"https://www.roblox.com/catalog/{asset_id}/"
    try_on_url = f"https://www.roblox.com/catalog/{asset_id}/#try-on-item"

    if stream_type == "free" and info["game_url"]:
        location_status = "In-Game Only"
        sale_value = f"[{info['game_name']}]({info['game_url']})"
    else:
        location_status = ""
        sale_value = f"[{sale_text}]({item_url})"

    if location_status:
        description = (
            f"🌐 **{location_status}**\n"
            f"[Roblox Page]({item_url}) | [Try On]({try_on_url})"
        )
    else:
        description = f"[Roblox Page]({item_url}) | [Try On]({try_on_url})"

    fields = [
        {"name": "Sale Location", "value": f"{sale_emoji} {sale_value}", "inline": False},
        {"name": "Price", "value": info["price"], "inline": True},
        {"name": "Quantity", "value": str(info["quantity"]), "inline": True},
        {"name": "Creator", "value": f"[{info['creator']}]({info['creator_link']})", "inline": True}
    ]

    embed = {
        "title": info["name"],
        "url": item_url,
        "description": description,
        "color": embed_color,
        "fields": fields,
        "footer": {"text": f"Asset ID: {asset_id}"}
    }

    if info["thumb"] and str(info["thumb"]).startswith("http"):
        embed["thumbnail"] = {"url": info["thumb"]}

    payload = {"embeds": [embed]}

    if role_id:
        payload["content"] = f"<@&{role_id}>"
        payload["allowed_mentions"] = {"roles": [role_id]}

    try:
        requests.post(webhook_url, json=payload, timeout=8)
    except Exception:
        pass

def fetch_data(url):
    try:
        response = session.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
        if response.ok:
            data = response.json()
            return data if isinstance(data, list) else [data]
    except Exception:
        pass
    return []

def monitor():
    processed_ids = set()
    while True:
        try:
            for item in fetch_data(URL_FREE):
                if isinstance(item, dict) and "free" in item:
                    asset_id = str(item["free"])
                    if asset_id not in processed_ids:
                        processed_ids.add(asset_id)
                        send_premium_webhook(asset_id, "free")
            for item in fetch_data(URL_PAID):
                if isinstance(item, dict) and "paid" in item:
                    asset_id = str(item["paid"])
                    if asset_id not in processed_ids:
                        processed_ids.add(asset_id)
                        send_premium_webhook(asset_id, "paid")
            for item in fetch_data(URL_WEBSITE):
                if isinstance(item, dict):
                    asset_id = item.get("website") or item.get("free") or item.get("paid")
                    if asset_id:
                        asset_id = str(asset_id)
                        if asset_id not in processed_ids:
                            processed_ids.add(asset_id)
                            send_premium_webhook(asset_id, "website")
        except Exception:
            pass
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    monitor()
