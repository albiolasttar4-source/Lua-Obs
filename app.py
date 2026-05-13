import os
import tempfile
import time
import requests
import platform
from datetime import datetime, timedelta
from flask import Flask
from flask_discord_interactions import (DiscordInteractions, Response, Embed,
                                        ActionRow, Button, ButtonStyles)

app = Flask(__name__)
discord = DiscordInteractions(app)

# Environment variables
app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]

# Import custom obfuscator (Moonsec V3 style)
from obfuscator import moonsec_v3_obfuscate, add_watermark

# ---------------- Simulated Storage (in-memory) ----------------
# Leaderboard: guild_id -> user_id -> count
leaderboard = {}
# Bot start time for /status uptime
start_time = time.time()

# ---------------- Helper functions ----------------
def get_guild_id(ctx):
    return ctx.guild_id

def get_user_id(ctx):
    return ctx.author.id if ctx.author else "unknown"

def track_obfuscation(guild_id, user_id):
    if guild_id not in leaderboard:
        leaderboard[guild_id] = {}
    leaderboard[guild_id][user_id] = leaderboard[guild_id].get(user_id, 0) + 1

# ---------------- Commands ----------------

@discord.command(name="obfuscate", description="Obfuscate your Lua code (Moonsec V3 style)")
def obfuscate_command(ctx, code: str = None):
    """I-obfuscate ang Lua code gamit ang advanced Moonsec V3 style."""
    source = code
    # Check for attachments
    if not source and ctx.attachments:
        for attach in ctx.attachments.values():
            if attach.filename.endswith('.lua'):
                try:
                    resp = requests.get(attach.url, timeout=5)
                    source = resp.text
                except Exception as e:
                    return Response(f"❌ Error reading file: {e}")
                break
        if not source:
            return Response("❌ Attachment must be a `.lua` file.")
    if not source:
        return Response("📎 Please attach a `.lua` file or type code after `/obfuscate code:`")

    try:
        # Apply Moonsec V3 obfuscation + watermark
        obfuscated = moonsec_v3_obfuscate(source)
        obfuscated = add_watermark(obfuscated)  # "-- Obfuscated by: Sttar Albiola"
        # Save to temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.lua', encoding='utf-8') as f:
            f.write(obfuscated)
            tmp_path = f.name
        # Track leaderboard
        guild_id = get_guild_id(ctx)
        user_id = get_user_id(ctx)
        track_obfuscation(guild_id, user_id)
        # Send file with confirmation embed
        embed = Embed(title="✅ Obfuscation Complete",
                      description="Your Lua code has been protected with **Moonsec V3 style**.",
                      color=0x00FF00)
        embed.add_field(name="Watermark", value=f"```-- Obfuscated by: Sttar Albiola```", inline=False)
        embed.set_footer(text="Drag & drop into your executor!")
        with open(tmp_path, 'rb') as f:
            ctx.send(embed=embed, file=discord.File(f, 'obfuscated.lua'))
        os.unlink(tmp_path)
        return Response()  # Empty response because file was sent
    except Exception as e:
        return Response(f"⚠️ Error: {str(e)}")


@discord.command(name="help", description="Show help for all commands")
def help_command(ctx):
    embed = Embed(title="🛠️ Lua Obfuscator Bot Help",
                  description="Protect your scripts with **Moonsec V3 style obfuscation**!",
                  color=0x3498DB)
    embed.add_field(name="/obfuscate [code] or (attach .lua file)",
                    value="Obfuscate Lua code with advanced encryption.", inline=False)
    embed.add_field(name="/leaderboard",
                    value="Show top obfuscator users in this server.", inline=False)
    embed.add_field(name="/status",
                    value="Show bot status and statistics.", inline=False)
    embed.set_footer(text="Developed by Sttar Albiola | Moonsec V3 Custom Style")
    return Response(embed=embed)


@discord.command(name="leaderboard", description="Top obfuscator users in this server")
def leaderboard_command(ctx):
    guild_id = get_guild_id(ctx)
    if guild_id not in leaderboard or not leaderboard[guild_id]:
        return Response(embed=Embed(description="No obfuscations yet in this server.", color=0xFFFF00))

    # Sort users by count
    sorted_users = sorted(leaderboard[guild_id].items(), key=lambda x: x[1], reverse=True)[:10]
    desc = ""
    for i, (uid, count) in enumerate(sorted_users, start=1):
        desc += f"**{i}.** <@{uid}> - **{count}** obfuscations\n"
    embed = Embed(title="🏆 Leaderboard - Top Obfuscators",
                  description=desc,
                  color=0xFFD700)
    embed.set_footer(text="Keep obfuscating to climb the ranks!")
    return Response(embed=embed)


@discord.command(name="status", description="Bot status and statistics")
def status_command(ctx):
    # Calculate uptime
    uptime_seconds = int(time.time() - start_time)
    uptime_str = str(timedelta(seconds=uptime_seconds)).split('.')[0]  # remove microseconds

    # Total obfuscations across all guilds
    total = sum(user counts for guild_counts in leaderboard.values() for counts in guild_counts.values())

    embed = Embed(title="📊 Bot Status",
                  color=0x7289DA)
    embed.add_field(name="⏱️ Uptime", value=uptime_str, inline=True)
    embed.add_field(name="🖥️ Platform", value=platform.system(), inline=True)
    embed.add_field(name="🐍 Python", value=platform.python_version(), inline=True)
    embed.add_field(name="📁 Servers", value=str(len(leaderboard)), inline=True)
    embed.add_field(name="🔒 Total Obfuscations", value=str(total), inline=True)
    embed.add_field(name="🌊 Watermark", value="```-- Obfuscated by: Sttar Albiola```", inline=False)
    embed.set_footer(text="Moonsec V3 Custom Obfuscator | 24/7 on Render")
    return Response(embed=embed)


# Health check
@app.route('/health')
def health():
    return "OK", 200

# Set interactions endpoint
discord.set_route("/interactions")

# Register slash commands (global or guild-specific)
# For testing, use guild_id; for global, remove guild_id and enable server members intent.
discord.update_commands(guild_id=os.environ.get("TESTING_GUILD"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    
