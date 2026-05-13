import discord
from discord import app_commands
import random
import base64
import string
import io
import os
import threading
from flask import Flask, request, render_template_string, send_file

# --- WEB UI CONFIG ---
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        code = request.form.get('code')
        if code:
            protected = moonsec_obfuscate(code)
            return send_file(io.BytesIO(protected.encode()), as_attachment=True, download_name="Protected.lua")
    return render_template_string("<h1>Bot is Online!</h1>")

# --- OBFUSCATOR LOGIC ---
def generate_var():
    return "_" + ''.join(random.choices(string.ascii_letters, k=12))

def moonsec_obfuscate(code: str) -> str:
    key = random.randint(50, 200)
    # Byte-based Rolling XOR
    bytes_data = [(ord(c) ^ (key + i)) % 256 for i, c in enumerate(code)]
    byte_str = "{" + ",".join(map(str, bytes_data)) + "}"
    
    v = {n: generate_var() for n in ['t', 'k', 'r', 'i', 'v', 's', 'f', 'b']}
    
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
if {v['f']} then {v['f']}() else warn("Error!") end
'''

# --- DISCORD BOT ---
class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)
    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()

@bot.tree.command(name="obfuscate", description="Secure your Lua script")
async def obf_cmd(interaction: discord.Interaction, file: discord.Attachment):
    await interaction.response.defer(ephemeral=True)
    if not file.filename.endswith(('.lua', '.txt')):
        return await interaction.followup.send("Lua/Txt files only!")
    
    content = (await file.read()).decode('utf-8', errors='ignore')
    result = moonsec_obfuscate(content)
    await interaction.followup.send(file=discord.File(io.BytesIO(result.encode()), "Protected.lua"))

# --- RUN ---
if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000))), daemon=True).start()
    token = os.getenv("DISCORD_TOKEN")
    if token:
        bot.run(token)
    else:
        print("MISSING DISCORD_TOKEN!")</html>'''

# --- OBFUSCATION CORE ---
def generate_random_var():
    return "_" + ''.join(random.choices(string.ascii_letters, k=random.randint(10, 15)))

def moonsec_obfuscate(lua_code: str) -> str:
    # 1. Rolling XOR Encryption
    seed = random.randint(60, 200)
    encoded_bytes = []
    for i, char in enumerate(lua_code):
        # Ang bawat character ay may kakaibang transformation base sa index
        transformed = (ord(char) ^ (seed + i)) % 256
        encoded_bytes.append(transformed)
    
    byte_table = "{" + ",".join(map(str, encoded_bytes)) + "}"
    
    # 2. Variable Randomization
    v = {n: generate_random_var() for n in ['table', 'key', 'res', 'i', 'v', 'step', 'func', 'junk', 'bit']}
    
    # 3. Lua Loader Construction (Using bit32 for Roblox compatibility)
    obf_script = f'''--[[ 
    STTAR MOONSEC V3.5 PREMIUM
    Protected for Delta Executor
    ]]
    local {v['table']} = {byte_table}
    local {v['key']} = {seed}
    local {v['res']} = ""
    local {v['bit']} = bit32 or bit

    local function {v['junk']}(...)
        local d = {{...}}
        local r = 0
        for i=1, #d do r = r + i end
        return r
    end

    for {v['i']}, {v['v']} in ipairs({v['table']}) do
        -- Rolling Decryption Logic
        local {v['step']} = {v['bit']}.bxor({v['v']}, ({v['key']} + ({v['i']} - 1))) % 256
        {v['res']} = {v['res']} .. string.char({v['step']})
        if {v['i']} % 100 == 0 then {v['junk']}({v['i']}) end
    end

    local {v['func']}, {v['junk']} = loadstring({v['res']})
    if {v['func']} then
        {v['func']}()
    else
        warn("TAMPERING DETECTED: CODE CORRUPTED")
    end
    '''
    
    # 4. Bloating (Mass Junk Variables to confuse AI)
    bloat = ""
    for _ in range(20):
        bloat += f"local {generate_random_var()} = {random.randint(1000, 99999)}; "
        
    return bloat + "\n" + obf_script

# --- FLASK ROUTES ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        code = request.form.get('code')
        if code:
            protected = moonsec_obfuscate(code)
            return send_file(
                io.BytesIO(protected.encode()), 
                as_attachment=True, 
                download_name="Protected_MoonSec.lua"
            )
    return render_template_string(HTML)

# --- DISCORD BOT ---
class MoonSecBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Slash Commands Synced for {self.user}")

client = MoonSecBot()

@client.tree.command(name="obfuscate", description="Encrypt your Lua script (AI-Proof)")
@app_commands.describe(file="I-upload ang .lua o .txt file na i-oobfuscate")
async def obfuscate(interaction: discord.Interaction, file: discord.Attachment):
    await interaction.response.defer(ephemeral=True)
    
    if not file.filename.endswith(('.lua', '.txt')):
        await interaction.followup.send("❌ Error: Valid .lua or .txt files only!")
        return

    try:
        raw_code = (await file.read()).decode('utf-8', errors='ignore')
        protected_code = moonsec_obfuscate(raw_code)
        
        output = io.BytesIO(protected_code.encode())
        discord_file = discord.File(output, filename=f"Protected_{file.filename}")
        
        embed = discord.Embed(title="🔒 MoonSec V3.5 Protected", color=0x00ff88)
        embed.add_field(name="Status", value="✅ Encrypted", inline=True)
        embed.add_field(name="Target", value="Delta / Roblox", inline=True)
        embed.set_footer(text="Anti-AI & Anti-Deobfuscation Enabled")
        
        await interaction.followup.send(embed=embed, file=discord_file)
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {str(e)}")

# --- RUNTIME ---
def run_web():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Start Web Server in Background
    threading.Thread(target=run_web, daemon=True).start()
    
    # Start Discord Bot
    token = os.getenv("DISCORD_TOKEN")
    if token:
        client.run(token)
    else:
        print("CRITICAL: DISCORD_TOKEN is not set in Environment Variables!")
-- Self-contained Base64 Decoder
local {v['b64dec']} = function(data)
    local b = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
    data = data:gsub('[^'..b..'=]', '')
    return (data:gsub('.', function(x)
        if x == '=' then return '' end
        local r,f='',(b:find(x)-1)
        for i=6,1,-1 do r=r..(f%2^i-f%2^(i-1)>0 and '1' or '0') end
        return r
    end):gsub('%d%d%d?%d?%d?%d?%d?%d?', function(x)
        if #x \~= 8 then return '' end
        local c=0
        for i=1,8 do c=c+(x:sub(i,i)=='1' and 2^(8-i) or 0) end
        return string.char(c)
    end))
end

local {v['p']} = "{b64}"
local {v['dec']} = {v['xor']}({v['b64dec']}({v['p']}), {key})

-- Junk + Anti-Tamper
local {v['j1']} = 0x{hex(random.randint(0x1337,0xFFFF))[2:]} - #{{\
{','.join(str(random.randint(1,250)) for _ in range(10))}}}
local {v['j2']} = 0

local function {v['vm']}(code)
    local success, result = pcall(loadstring, code)
    if success then
        return result()
    else
        return warn("[MoonSec] Integrity Check Failed")
    end
end

{v['vm']}({v['dec']})
'''

    # Extra Junk Lines (MoonSec Style)
    for _ in range(16):
        obf += f"\nlocal {generate_random_var()} = {random.randint(10000,999999)} - 0x{random.randint(0x100,0x400):X} + #{{\
{','.join(str(random.randint(1,99)) for _ in range(random.randint(5,13)))}}}"

    return obf


# ===================== DISCORD BOT =====================
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync()
    print(f"✅ Sttar MoonSec Bot + Web is Online → {client.user}")

@tree.command(name="obfuscate", description="Obfuscate Lua script with MoonSec V3 Style")
@app_commands.describe(code="Paste your Lua code here (optional)")
async def obfuscate(interaction: discord.Interaction, code: str = None):
    await interaction.response.defer()

    lua_code = code

    if not lua_code and interaction.message and interaction.message.attachments:
        for att in interaction.message.attachments:
            if att.filename.endswith(('.lua', '.txt')):
                lua_code = (await att.read()).decode('utf-8', errors='ignore')
                break

    if not lua_code:
        embed = discord.Embed(title="❌ No Code Detected", description="Paste code or upload `.lua` file.", color=0xff0000)
        await interaction.followup.send(embed=embed)
        return

    try:
        result = moonsec_obfuscate(lua_code)

        embed = discord.Embed(
            title="🔒 Successfully Obfuscated!",
            description="**MoonSec V3.1 Style** • Protected by **Sttar**",
            color=0x00ff88
        )
        embed.add_field(name="Status", value="✅ Protected", inline=True)
        embed.add_field(name="Security Level", value="**High**", inline=True)
        embed.add_field(name="Technique", value="XOR + Custom Base64 + Junk + VM", inline=False)
        embed.set_footer(text="Sttar MoonSec Obfuscator • Do not share original script")
        
        file = discord.File(io.BytesIO(result.encode('utf-8')), filename="Sttar_MoonSec_Protected.lua")
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
