import random
import string
import base64

def add_watermark(script: str) -> str:
    """Insert watermark after the opening comment line."""
    lines = script.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("--[["):
            lines.insert(i+1, "-- Obfuscated by: Sttar Albiola")
            break
    return "\n".join(lines)

def moonsec_v3_obfuscate(source_code: str) -> str:
    """
    Moonsec V3 style obfuscation:
    1. XOR encrypt source with random key.
    2. Base64 encode.
    3. Embed a pure-Lua Base64 decoder and XOR decoder.
    4. Loadstring the decoded result.
    """
    xor_key = random.randint(1, 255)
    encrypted_bytes = bytes([b ^ xor_key for b in source_code.encode('utf-8')])
    encrypted_b64 = base64.b64encode(encrypted_bytes).decode('ascii')

    # Random variable names for added confusion
    r1 = random_string(12)
    r2 = random_string(16)
    r3 = random_string(8)

    script = f'''--[[ Protected with MoonSec V3 (custom) ]]
local {r1} = (function()
    local {r2} = [[{encrypted_b64}]]
    local {r3} = {xor_key}
    return (function(enc64, key)
        -- Lua Base64 decoder (pure, no external libs)
        local b='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
        local dec = {{}}
        for i=1,64 do local c=b:sub(i,i) dec[c]=i-1 end
        local function decode(data)
            data = string.gsub(data,'[^'..b..'=]','')
            return (data:gsub('.', function(x)
                if (x == '=') then return '' end
                local r,f='',(dec[x]<<2)
                for i=4,6 do r=r..(dec[x:sub(2,2)]or 0)..(f>>(i-2)&1) end
                return string.char(((f>>4)&15)*4+(dec[x:sub(3,3)]or 0))..string.char((((f>>2)&3)*16+(dec[x:sub(3,3)]or 0)))
            end))
        end
        -- XOR decode
        local raw = ""
        for i=1,#data do
            raw = raw .. string.char(string.byte(data,i) ~ key)
        end
        return raw
    end)({r2}, {r3})
end)()
local s = {r1}()
if s then
    local f, e = loadstring(s)
    if f then f() else print("Error: "..e) end
end'''
    return script

def random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
  
