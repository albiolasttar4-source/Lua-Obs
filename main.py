discord.py
flask        if 'file' in request.files and request.files['file'].filename:
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
    
    # XOR Encryption
    encrypted = ''.join(chr(ord(c) ^ key) for c in lua_code)
    b64 = base64.b64encode(encrypted.encode('utf-8')).decode('utf-8')

    v = {name: generate_random_var() for name in ['xor', 'b64dec', 'dec', 'vm', 'j1', 'j2', 'p']}

    # Watermark na gusto mo
    obf = f'''-- Obfuscated by: Sttar MoonSec Bot
-- Discord Server: https://discord.gg/88SfW7RvhC
-- [ Sttar MoonSec V3.1 ] Protected

local {v['xor']} = function(s, k)
    local r = {{}}
    for i = 1, #s do
        r[i] = string.char(string.byte(s, i) \~ k)
    end
    return table.concat(r)
end

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
