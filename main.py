import discord
from discord import app_commands
import random
import string
import io
import os
import threading
from flask import Flask, request, render_template_string, send_file

# --- SIMPLE WEB SERVER ---
app = Flask(__name__)

@app.route('/')
def home():
    return "MoonSec Bot is Running!"

@app.route('/web', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        code = request.form.get('code')
        if code:
            protected = moonsec_obfuscate(code)
            return send_file(io.BytesIO(protected.encode()), as_attachment=True, download_name="Protected.lua")
    return render_template_string('<form method="post"><textarea name="code" style="width:100%;height:300px;"></textarea><br><button type="submit">Protect</button></form>')

# --- OBFUSCATION LOGIC ---
def gen_v():
    return "_" + ''.join(random.choices(string.ascii_letters, k=10))

def moonsec_obfuscate(lua_code: str) -> str:
    key = random.randint(50, 250)
    # Byte Table Encryption
    bytes_arr = [(ord(c) ^ (key + i)) % 256 for i, c in enumerate(lua_code)]
    byte_str = "{" + ",".join(map(str, bytes_arr)) + "}"
    
    v = {n: gen_v() for n in ['t', 'k', 'r', 'i', 'v', 's', 'f', 'b']}
    
    return f'''
local {v['t']} = {byte_str}
local {v['k']} = {key}
local {v['r']} = ""
local {v['b']} = bit32 or bit

for {v['i']}, {v['v']} in ipairs({v['t']}) do
    local {v['s']} = {v['b']}.bxor({v['v']}, ({v['k']} + ({v['i']} - 1))) % 256
    {v['r']} = {v['r']} .. string.char({v['s']})
end

local {v['f']} = loadstring({v['r']})
if {v['f']} then {v['f']}() else warn("Obfuscation Error") end
'''

# --- DISCORD BOT ---
class SttarBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)
    async def setup_hook(self):
        await self.tree.sync()

client = SttarBot()

@client.tree.command(name="obfuscate", description="MoonSec V3.5 Protection")
async def obf(interaction: discord.Interaction, file: discord.Attachment):
    await interaction.response.defer(ephemeral=True)
    if not file.filename.endswith(('.lua', '.txt')):
        return await interaction.followup.send("❌ .lua o .txt lang dapat!")
    
    content = (await file.read()).decode('utf-8', errors='ignore')
    result = moonsec_obfuscate(content)
    await interaction.followup.send("✅ Done!", file=discord.File(io.BytesIO(result.encode()), "Protected.lua"))

# --- RUN EVERYTHING ---
if __name__ == "__main__":
    # Start Flask
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000))), daemon=True).start()
    
    # Start Bot
    token = os.getenv("DISCORD_TOKEN")
    if token:
        client.run(token)
    else:
        print("MISSING DISCORD_TOKEN!")ult.encode('utf-8')), filename="Sttar_MoonSec_Protected.lua")
        await interaction.followup.send(embed=embed, file=file)

    except Exception as e:
        error_embed = discord.Embed(title="❌ Error", description=str(e), color=0xff0000)
        await interaction.followup.send(embed=error_embed)


# ===================== RUN BOTH =====================
def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    token = os.getenv("DISCORD_TOKEN")
    if token:
        client.run(token)
    else:
        print("❌ DISCORD_TOKEN not set!")
