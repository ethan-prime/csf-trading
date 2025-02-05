# just for webhooks lol
from discord_webhook import DiscordWebhook, DiscordEmbed

webhook_url = "https://discord.com/api/webhooks/1335879766540161044/8rw07Yypq9h_vEgcZtVWU9ylsxor9Vk3Dlyke8wrEK5zyFSpp4-urmIQq1LhwgZuPl9m"

def send_webhook(item_name, price, expected_profit, n_sales, image_link):
    # Create webhook
    webhook = DiscordWebhook(url=webhook_url)

    # Create an embed
    embed = DiscordEmbed(title="Money Located", color="03b2f8")
    embed.set_author(name="MaliciousCode63", icon_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTMWAC3rB5qirxxZbkWNRsCC02x24aDD-_V2g&s")
    embed.set_thumbnail(url=image_link)
    embed.add_embed_field(name="Item", value=item_name, inline=False)
    embed.add_embed_field(name="Price", value=f"${price}", inline=True)
    embed.add_embed_field(name="EV", value=f"+${expected_profit}", inline=True)
    embed.add_embed_field(name="# Similar Sales", value=str(n_sales))

    # Add embed to webhook
    webhook.add_embed(embed)

    # Send webhook
    response = webhook.execute()
    return response