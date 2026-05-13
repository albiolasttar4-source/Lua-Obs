import os
import re
import random
import threading
import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask, jsonify

# ------------------ CONFIG ------------------
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
MAX_LEN = 50000

# ------------------ OBFUSCATOR ENGINE ------------------
class Obfuscator:
    def __init__(self):
        self.vocab = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"

    def rand_str(self, n=8):
        return "".join(random.choices(self.vocab, k=n))

    def obf_num(self, n):
        if abs(n) < 10:
            return str(n)
        opts = [
            str(n),
            f"({random.randint(1,99)}+{n - random.randint(1,99)})",
            f"(0x{int(n):x})"
        ]
        return random.choice(opts)

    def obf_str(self, s):
        if len(s) < 3:
            return f'"{s}"'
        bytes_vals = ",".join(str(ord(c)) for c in s)
        return f'loadstring(table.concat({{{bytes_vals}}},""))()'

    def obfuscate(self, code):
        # obf strings
        def repl_str(m):
            q = m.group(1)
            content = m.group(2)
            return self.obf_str(content)
        code = re.sub(r'(["'])(.*?)\1', repl_str, code)

        # obf numbers
        def repl_num(m):
            num = m.group(0)
            if "." in num:
                n = float(num)
            else:
                n = int(num)
            return self.obf_num(n)
        code = re.sub(r'\b\d+(?:\.\d+)?\b', repl_num, code)

        # dead code injection (3 times)
        for _ in range(3):
            dead = f"""
if ({random.choice(["true==false","1==2","false"])}) then
    local _ = {random.randint(100,9999)}
end
"""
            lines = code.split("\n")
            pos = random.randint(0, len(lines))
            lines.insert(pos, dead)
            code = "\n".join(lines)

        # anti-debug header
        anti = """
local function _s()
    if debug and debug.getinfo then error("debug blocked") end
end
_s()
"""
        return anti + "\n" + code

# ------------------ DISCORD BOT ------------------
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
ob = Obfuscator()

@bot.event
async def on_ready():
    print(f"✅ Discord bot online: {bot.user}")
    await bot.tree.sync()

@bot.tree.command(name="obfuscate", description="Obfuscate Lua script for Delta executor")
async def slash_obf(interaction: discord.Interaction, script: str, public: bool = False):
    await interaction.response.defer(ephemeral=not public)

    if len(script) > MAX_LEN:
        await interaction.followup.send(f"❌ Max {MAX_LEN} chars")
        return

    if re.search(r"(getfenv|setfenv|loadstring|dofile|loadfile)", script, re.I):
        await interaction.followup.send("❌ Contains blocked functions")
        return

    try:
        result = ob.obfuscate(script)
        if len(result) > 1990:
            result = result[:1990] + "\n... [TRUNCATED]"
        embed = discord.Embed(
            title="🔒 Obfuscated Lua",
            description=f"```lua\n{result}\n```",
            color=0x2b2d31
        )
        embed.set_footer(text="Delta Executor Ready")
        await interaction.followup.send(embed=embed)
    except Exception as e:
        print(e)
        await interaction.followup.send("❌ Obfuscation failed")

def run_discord():
    bot.run(TOKEN)

# ------------------ FLASK WEB SERVER ------------------
app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "alive", "bot": "Lua Obfuscator for Delta"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ------------------ MAIN ------------------
if __name__ == "__main__":
    # Start Discord bot in background thread
    discord_thread = threading.Thread(target=run_discord)
    discord_thread.start()
    # Run Flask in main thread (for Render)
    run_flask()
