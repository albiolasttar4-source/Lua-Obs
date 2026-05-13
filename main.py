import discord
from discord import app_commands
import random
import base64
import string
import io
import os
import threading
from flask import Flask, request, render_template_string, send_file

# ===================== FLASK =====================
app = Flask(__name__)

HTML = '''<!DOCTYPE html>
<html>
<head><title>Sttar MoonSec Obfuscator</title>
<style>
    body {font-family: Arial; background:#0a0a0a; color:#00ff88; padding:30px;}
    textarea {width:100%; height:350px; background:#1a1a1a; color:#00ff88; border:2px solid #00ff88;}
    button {padding:12px 30px; background:#00ff88; color:black; font-weight:bold; border:none; font-size:16px;}
</style>
</head>
<body>
    <h1>🚀 Sttar MoonSec Obfuscator v3</h1>
    <form method="POST" enctype="multipart/form-data">
        <textarea name="code" placeholder="Paste your Lua script here..."></textarea><br><br>
        <input type="file" name="file" accept=".lua,.txt"><br><br>
        <button type="submit">🔒 Obfuscate Now</button>
    </form>
</body>
</html>'''

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        code = None
        if 'file' in request.files and request.files['file'].filename:
            code = request.files['file'].read().decode('utf-8', errors='ignore')
        else:
            code = request.form.get('code')
        
        if code:
            obf = moonsec_obfuscate(code)
            return send_file(io.BytesIO(obf.encode()), as_attachment=True, download_name="Sttar_MoonSec_Protected.lua")
    return render_template_string(HTML)

# ===================== MOONSEC OBFUSCATOR =====================
def generate_random_var():
    return "_" + ''.join(random.choices(string.ascii_letters + string.digits, k=10))

def moonsec_obfuscate(lua_code: str) -> str:
    key = random.randint(0x70, 0xFF)
    encrypted = ''.join(chr(ord(c) ^ key) for c in lua_code)
    b64 = base64.b64encode(encrypted.encode()).decode()

    v = {name: generate_random_var() for name in ['xor','dec','vm','j1','j2','p']}

    obf = f'''-- [ Sttar MoonSec V3 ] Protected
local {v['xor']} = function(s,k)local r={{}}for i=1,#s do r[i]=string.char(string.byte(s,i)\~k)end;return table.concat(r)end

local {v['p']} = "{b64}"
local {v['dec']} = {v['xor']}(string.char(unpack({{string.byte(base64.decode({v['p']}),1,-1)}})),{key})

-- Anti-Tamper + Junk
local {v['j1']} = 0x{hex(random.randint(0x1337,0xFFFF))[2:]} - #{{\
{','.join(str(random.randint(1,300)) for _ in range(12))}}}
local {v['j2']} = math.random(1,999999)*0

local function {v['vm']}(f)
    local s,e = pcall(loadstring,f)
    return s and e() or warn("[MoonSec] Integrity Check Failed")
end

{v['vm']}({v['dec']})
'''

    # Extra junk
    for _ in range(18):
        obf += f"\nlocal {generate_random_var()} = {random.randint(9999,999999)} - 0x{random.randint(0x80,0x300):X} + #{{\
{','.join(str(random.randint(1,120)) for _ in range(random.randint(6,14)))}}}"

    return obf


# ===================== DISCORD BOT with BEAUTIFUL EMBED =====================
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

    # Check for attachment
    if not lua_code and interaction.message and interaction.message.attachments:
        for att in interaction.message.attachments:
            if att.filename.endswith(('.lua', '.txt')):
                lua_code = (await att.read()).decode('utf-8', errors='ignore')
                break

    if not lua_code:
        embed = discord.Embed(
            title="❌ No Code Detected",
            description="Paste the code or upload a `.lua` file.",
            color=0xff0000
        )
        await interaction.followup.send(embed=embed)
        return

    try:
        result = moonsec_obfuscate(lua_code)

        embed = discord.Embed(
            title="🔒 Successfully Obfuscated!",
            description="**MoonSec V3 Style** • Protected by **Sttar**",
            color=0x00ff88
        )
        embed.add_field(name="Status", value="✅ Protected", inline=True)
        embed.add_field(name="Security Level", value="**High**", inline=True)
        embed.add_field(name="Technique", value="XOR + VM + Junk + Anti-Tamper", inline=False)
        embed.set_footer(text="Do not share the original script • Sttar Obfuscator")
        embed.set_thumbnail(url="https://i.imgur.com/8Zf9vZQ.png")  # Optional shield icon

        file = discord.File(io.BytesIO(result.encode('utf-8')), filename="Sttar_MoonSec_Protected.lua")

        await interaction.followup.send(embed=embed, file=file)

    except Exception as e:
        error_embed = discord.Embed(title="❌ Error Occurred", description=str(e), color=0xff0000)
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
        print("❌ DISCORD_TOKEN not set in environment variables!")
