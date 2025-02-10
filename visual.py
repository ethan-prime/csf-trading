# just for webhooks lol
from discord_webhook import DiscordWebhook, DiscordEmbed

webhook_url = "https://discord.com/api/webhooks/1335879766540161044/8rw07Yypq9h_vEgcZtVWU9ylsxor9Vk3Dlyke8wrEK5zyFSpp4-urmIQq1LhwgZuPl9m"

def send_webhook(item_name, buy_order, market_value, expected_profit, eq_val, n_sales, vol, h_val, url, image_link):
    # Create webhook
    webhook = DiscordWebhook(url=webhook_url)

    # Create an embed
    embed = DiscordEmbed(title=item_name, color="50C878")
    embed.set_author(name="CSFloat Trader", icon_url="https://csfloat.com/assets/n-mini-logo.png")
    embed.set_thumbnail(url=image_link)
    embed.add_embed_field(name="Item", value=item_name, inline=False)
    embed.add_embed_field(name="Buy Order", value=f"${buy_order}", inline=True)
    embed.add_embed_field(name="Market Value", value=f"${market_value}", inline=True)
    embed.add_embed_field(name="# Similar Sales", value=str(n_sales))
    embed.add_embed_field(name="EV", value=f"+${expected_profit} ({round(expected_profit/buy_order*100, 2)}%)", inline=True)
    embed.add_embed_field(name="EQ Value", value=f"${eq_val}", inline=True)
    embed.add_embed_field(name="Volume (past 7 days)", value=vol, inline=True)
    embed.add_embed_field(name="Heuristic", value=f"{h_val}", inline=True)
    embed.set_url(url)

    # Add embed to webhook
    webhook.add_embed(embed)

    # Send webhook
    response = webhook.execute()
    return response

def send_webhook_msg(msg):
    webhook = DiscordWebhook(url=webhook_url)
    embed = DiscordEmbed(title="Bid Update", description=msg, color="3266a8")
    embed.set_author(name="CSFloat Trader", icon_url="https://csfloat.com/assets/n-mini-logo.png")
    webhook.add_embed(embed)
    response = webhook.execute()
    return response