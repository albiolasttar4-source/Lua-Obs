import os
import re
import random
import threading
import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask, jsonify

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
MAX_LEN = 50000

# ------------------ OBFUSCATOR ------------------
class Obfuscator:
    def __init__(self):
        self.vocab = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"

    def rand_str(self, n=8):
        return "".join(random.choices(self.vocab, k=n))

    def obf_num(self, n):
        if abs(n) < 10:
            return str(n)
        r = random.choice([1,2,3])
        if r == 1:
            return str(n)
        elif r == 2:
            return f"({random.randint(1,99)}+{n - random.randint(1,99)})"
        else:
            return f"(0x{int(n):x})"

    def obf_str(self, s):
        if len(s) < 3:
            return f'"{s}"'
        bytes_vals = ",".join(str(ord(c)) for c in s)
        return f'loadstring(table.concat({{{bytes_vals}}},""))()'

    def obfuscate(self, code):
        # Obfuscate strings: find "..." or '...'
        def repl_str(match):
            quote = match.group(1)
            content = match.group(2)
            return self.obf_str(content)
        # Pattern: (["'])(.*?)\1
        pattern = r'(["\'])(.*?)\1'
        code = re.sub(pattern, repl_str, code, flags=re.DOTALL)

        # Obfuscate numbers
        def repl_num(match):
            num_str = match.group(0)
            if '.' in num_str:
                n = float(num_str)
            else:
                n = int(num_str)
            return self.obf_num(n)
        code = re.sub(r'\b\d+(?:\.\d+)?\b', repl_num, code)

        # Inject dead code 3 times
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

        # Anti-debug header
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

    # Block dangerous functions
    dangerous = re.compile(r'(getfenv|setfenv|loadstring|dofile|loadfile)', re.I)
    if dangerous.search(script):
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
    discord_thread = threading.Thread(target=run_discord)
    discord_thread.start()
    run_flask()
