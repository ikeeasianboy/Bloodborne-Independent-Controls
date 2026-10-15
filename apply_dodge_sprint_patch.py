from pathlib import Path
from datetime import datetime
import re
import sys

ROOT = Path.cwd()
FILES = [
    "gpu/shim/input/bindings.h",
    "gpu/shim/input/bindings.cpp",
    "gpu/shim/input/input.h",
    "gpu/shim/input/input.cpp",
    "gpu/shim/engine/option_menu.cpp",
    "src/runtime_pad.c",
]

missing = [f for f in FILES if not (ROOT / f).is_file()]
if missing:
    print("ERROR: Run this script from the engine-source repository root.")
    print("Missing:", ", ".join(missing))
    sys.exit(1)

original = {f: (ROOT / f).read_text(encoding="utf-8") for f in FILES}
changed = dict(original)

def replace_once(file, old, new, expected=1):
    count = changed[file].count(old)
    if count != expected:
        raise RuntimeError(f"{file}: expected {expected} occurrence(s), found {count} for {old[:90]!r}")
    changed[file] = changed[file].replace(old, new)

def regex_once(file, pattern, repl, flags=0):
    updated, count = re.subn(pattern, repl, changed[file], count=1, flags=flags)
    if count != 1:
        raise RuntimeError(f"{file}: expected one regex match, found {count}: {pattern[:100]!r}")
    changed[file] = updated

try:
    # Public action and pad-binding API.
    replace_once(
        "gpu/shim/input/bindings.h",
        "    kBindL3, kBindDebugMenu,\n    kBindCount,",
        "    kBindL3, kBindSprint, kBindDebugMenu,\n    kBindCount,",
    )
    replace_once(
        "gpu/shim/input/bindings.h",
        "    int def_mouse;         // 1..5, or 0\n};",
        "    int def_mouse;         // 1..5, or 0\n    int def_pad;           // SDL_GamepadButton, trigger sentinel, or -1 when unbound\n};",
    )
    replace_once(
        "gpu/shim/input/bindings.h",
        "void host_bindings_mouse_held(std::uint32_t buttons, bool held[kBindCount]);",
        "void host_bindings_mouse_held(std::uint32_t buttons, bool held[kBindCount]);\nvoid host_bindings_pad_held(std::uint32_t buttons, std::uint8_t left_trigger, std::uint8_t right_trigger, bool held[kBindCount]);",
    )
    replace_once(
        "gpu/shim/input/bindings.h",
        "bool host_bind_capture_mouse(int button);  // 1..5, or 6 and 7 for the wheel up and down",
        "bool host_bind_capture_mouse(int button);  // 1..5, or 6 and 7 for the wheel up and down\nbool host_bind_capture_pad(int button);    // SDL gamepad button, or SDL_GAMEPAD_BUTTON_COUNT (+1) for triggers",
    )

    # Replace the binding table as one unit so every action has a controller default too.
    new_table = '''constexpr int kPadUnbound = -1;
constexpr int kPadLeftTrigger = SDL_GAMEPAD_BUTTON_COUNT;
constexpr int kPadRightTrigger = SDL_GAMEPAD_BUTTON_COUNT + 1;

const BindingInfo kInfo[kBindCount] = {
    {"move_forward", "Move Forward", "Left stick up.", 0, "W", 0, kPadUnbound},
    {"move_back", "Move Back", "Left stick down.", 0, "S", 0, kPadUnbound},
    {"move_left", "Move Left", "Left stick left.", 0, "A", 0, kPadUnbound},
    {"move_right", "Move Right", "Left stick right.", 0, "D", 0, kPadUnbound},
    {"walk", "Walk", "Hold with the movement keys to walk.", 0, "Left Alt", 0, kPadUnbound},
    {"roll", "Roll / Dash", "Press for a quick dodge or dash.", kCircle, "Space", 0, SDL_GAMEPAD_BUTTON_EAST},
    {"lock_on", "Lock On", "R3. Lock on to a target, or reset the camera.", kR3, "Q", 0, SDL_GAMEPAD_BUTTON_RIGHT_STICK},

    {"attack", "Attack", "R1. With the strong attack modifier held, R2.", kR1, nullptr, 1, SDL_GAMEPAD_BUTTON_RIGHT_SHOULDER},
    {"strong_attack", "Strong Attack", "R2. Hold to charge.", kR2, "V", 0, kPadRightTrigger},
    {"strong_modifier", "Strong Attack Modifier", "Held with Attack, attacks strong (R2).", 0, "Left Shift", 0, kPadUnbound},
    {"transform", "Transform", "L1. Transform the trick weapon.", kL1, "C", 3, SDL_GAMEPAD_BUTTON_LEFT_SHOULDER},
    {"firearm", "Firearm / Parry", "L2. Shoot the left-hand weapon.", kL2, "X", 2, kPadLeftTrigger},
    {"blood_vial", "Blood Vial", "Triangle. Restore HP with a Blood Vial.", kTriangle, "R", 0, SDL_GAMEPAD_BUTTON_NORTH},
    {"use_item", "Use Item", "Square. Use the selected quick item.", kSquare, "F", 0, SDL_GAMEPAD_BUTTON_WEST},

    {"interact", "Interact", "Cross. Talk, examine, pick up, open.", kCross, "E", 0, SDL_GAMEPAD_BUTTON_SOUTH},
    {"switch_item", "Switch Item", "D-pad down. Cycle the quick items.", kDown, "Down", 0, SDL_GAMEPAD_BUTTON_DPAD_DOWN},
    {"switch_right", "Switch Right Weapon", "D-pad right.", kRight, "Right", 0, SDL_GAMEPAD_BUTTON_DPAD_RIGHT},
    {"switch_left", "Switch Left Weapon", "D-pad left.", kLeft, "Left", 0, SDL_GAMEPAD_BUTTON_DPAD_LEFT},
    {"dpad_up", "D-pad Up", "D-pad up.", kUp, "Up", 0, SDL_GAMEPAD_BUTTON_DPAD_UP},
    {"gestures", "Gestures", "The touchpad's left side.", kTouchPad, "G", 0, SDL_GAMEPAD_BUTTON_BACK},
    {"personal_effects", "Personal Effects", "The touchpad's right side.", kTouchPad, "T", 0, SDL_GAMEPAD_BUTTON_TOUCHPAD},

    {"look_up", "Look Up", "Right stick up, for the camera without the mouse.", 0, "I", 0, kPadUnbound},
    {"look_down", "Look Down", "Right stick down.", 0, "K", 0, kPadUnbound},
    {"look_left", "Look Left", "Right stick left.", 0, "J", 0, kPadUnbound},
    {"look_right", "Look Right", "Right stick right.", 0, "L", 0, kPadUnbound},
    {"menu", "Menu", "Options. Open the menu.", kOptions, "Escape", 0, SDL_GAMEPAD_BUTTON_START},
    {"confirm", "Menu Confirm", "OK, in menus.", 0, "Return", 0, SDL_GAMEPAD_BUTTON_SOUTH},
    {"back", "Menu Back", "Return, in menus.", 0, "Backspace", 0, SDL_GAMEPAD_BUTTON_EAST},

    {"l3", "Left Stick Press", "L3.", kL3, "Left Ctrl", 0, kPadUnbound},
    {"sprint", "Sprint", "Hold to sprint independently from Roll / Dash.", kCircle, "Right Shift", 0, SDL_GAMEPAD_BUTTON_LEFT_STICK},
    {"debug_menu", "Debug Menu", "Opens and closes the developers' debug menu (the Debug Menu plugin).", 0, "`", 0, kPadUnbound},
};

// Text tokens saved in bind.<action>. Controller button names are deliberately
// standardized by position so they work across Xbox, PlayStation, and SDL pads.
struct PadName { const char* token; const char* label; int button; };
const PadName kPadNames[] = {
    {"PadA", "Pad A", SDL_GAMEPAD_BUTTON_SOUTH},
    {"PadB", "Pad B", SDL_GAMEPAD_BUTTON_EAST},
    {"PadX", "Pad X", SDL_GAMEPAD_BUTTON_WEST},
    {"PadY", "Pad Y", SDL_GAMEPAD_BUTTON_NORTH},
    {"PadBack", "Pad Back", SDL_GAMEPAD_BUTTON_BACK},
    {"PadGuide", "Pad Guide", SDL_GAMEPAD_BUTTON_GUIDE},
    {"PadStart", "Pad Start", SDL_GAMEPAD_BUTTON_START},
    {"PadLeftStick", "Pad L3", SDL_GAMEPAD_BUTTON_LEFT_STICK},
    {"PadRightStick", "Pad R3", SDL_GAMEPAD_BUTTON_RIGHT_STICK},
    {"PadLeftShoulder", "Pad LB", SDL_GAMEPAD_BUTTON_LEFT_SHOULDER},
    {"PadRightShoulder", "Pad RB", SDL_GAMEPAD_BUTTON_RIGHT_SHOULDER},
    {"PadDpadUp", "Pad D-Up", SDL_GAMEPAD_BUTTON_DPAD_UP},
    {"PadDpadDown", "Pad D-Down", SDL_GAMEPAD_BUTTON_DPAD_DOWN},
    {"PadDpadLeft", "Pad D-Left", SDL_GAMEPAD_BUTTON_DPAD_LEFT},
    {"PadDpadRight", "Pad D-Right", SDL_GAMEPAD_BUTTON_DPAD_RIGHT},
    {"PadMisc1", "Pad Misc", SDL_GAMEPAD_BUTTON_MISC1},
    {"PadRightPaddle1", "Pad RP1", SDL_GAMEPAD_BUTTON_RIGHT_PADDLE1},
    {"PadLeftPaddle1", "Pad LP1", SDL_GAMEPAD_BUTTON_LEFT_PADDLE1},
    {"PadRightPaddle2", "Pad RP2", SDL_GAMEPAD_BUTTON_RIGHT_PADDLE2},
    {"PadLeftPaddle2", "Pad LP2", SDL_GAMEPAD_BUTTON_LEFT_PADDLE2},
    {"PadTouchpad", "Pad Touchpad", SDL_GAMEPAD_BUTTON_TOUCHPAD},
    {"PadLeftTrigger", "Pad LT", kPadLeftTrigger},
    {"PadRightTrigger", "Pad RT", kPadRightTrigger},
};

const char* pad_token(int button) {
    for (const auto& p : kPadNames) if (p.button == button) return p.token;
    return nullptr;
}
const char* pad_label(int button) {
    for (const auto& p : kPadNames) if (p.button == button) return p.label;
    return nullptr;
}
int pad_from_token(const std::string& token) {
    for (const auto& p : kPadNames) if (token == p.token) return p.button;
    return kPadUnbound;
}
'''
    regex_once(
        "gpu/shim/input/bindings.cpp",
        r"const BindingInfo kInfo\[kBindCount\] = \{.*?\n\};\n\n// Earlier names a bbhost.toml may still use\.",
        new_table + "\n// Earlier names a bbhost.toml may still use.",
        flags=re.S,
    )

    # Bind storage.
    replace_once(
        "gpu/shim/input/bindings.cpp",
        "std::atomic<int> g_key[kBindCount];\nstd::atomic<int> g_mouse[kBindCount];",
        "std::atomic<int> g_key[kBindCount];\nstd::atomic<int> g_mouse[kBindCount];\nstd::atomic<int> g_pad[kBindCount];\nstd::atomic<bool> g_roll_prev{false};\nstd::atomic<std::int64_t> g_roll_until_ms{0};",
    )

    # Parse combined keyboard, mouse, and gamepad bindings.
    replace_once(
        "gpu/shim/input/bindings.cpp",
        "void set_from_text(int a, const std::string& text, const char* where) {\n    int key = 0, mouse = 0;",
        "void set_from_text(int a, const std::string& text, const char* where) {\n    int key = 0, mouse = 0, pad = g_pad[a].load(std::memory_order_relaxed);",
    )
    replace_once(
        "gpu/shim/input/bindings.cpp",
        "        if (tok.empty() || tok == \"none\") continue;",
        "        if (tok.empty()) continue;\n        if (tok == \"none\") { key = 0; mouse = 0; pad = kPadUnbound; continue; }\n        if (tok == \"PadNone\") { pad = kPadUnbound; continue; }",
    )
    replace_once(
        "gpu/shim/input/bindings.cpp",
        "        const int sc = scancode_from_name(tok);\n        if (!sc) {",
        "        if (tok.rfind(\"Pad\", 0) == 0) {\n            pad = pad_from_token(tok);\n            if (pad == kPadUnbound) host_log(\"keys: %s: unknown gamepad token \\\"%s\\\"\", kInfo[a].key, tok.c_str());\n            continue;\n        }\n        const int sc = scancode_from_name(tok);\n        if (!sc) {",
    )
    replace_once(
        "gpu/shim/input/bindings.cpp",
        "    g_key[a].store(key, std::memory_order_relaxed);\n    g_mouse[a].store(mouse, std::memory_order_relaxed);\n    g_serial.fetch_add(1, std::memory_order_relaxed);",
        "    g_key[a].store(key, std::memory_order_relaxed);\n    g_mouse[a].store(mouse, std::memory_order_relaxed);\n    g_pad[a].store(pad, std::memory_order_relaxed);\n    g_serial.fetch_add(1, std::memory_order_relaxed);",
    )
    replace_once(
        "gpu/shim/input/bindings.cpp",
        "        g_mouse[a].store(kInfo[a].def_mouse, std::memory_order_relaxed);\n    }",
        "        g_mouse[a].store(kInfo[a].def_mouse, std::memory_order_relaxed);\n        g_pad[a].store(kInfo[a].def_pad, std::memory_order_relaxed);\n    }",
    )

    # Save gamepad names along with keys and mouse buttons.
    replace_once(
        "gpu/shim/input/bindings.cpp",
        "        if (const int m = g_mouse[a].load(std::memory_order_relaxed)) {\n            v += v.empty() ? \"\" : \", \";\n            v += mouse_token(m);\n        }\n        std::fprintf(f, \"bind.%s=%s\\n\", kInfo[a].key, v.empty() ? \"none\" : v.c_str());",
        "        if (const int m = g_mouse[a].load(std::memory_order_relaxed)) {\n            v += v.empty() ? \"\" : \", \";\n            v += mouse_token(m);\n        }\n        if (const char* p = pad_token(g_pad[a].load(std::memory_order_relaxed))) {\n            v += v.empty() ? \"\" : \", \";\n            v += p;\n        } else if (!v.empty()) {\n            v += \", PadNone\";\n        }\n        std::fprintf(f, \"bind.%s=%s\\n\", kInfo[a].key, v.empty() ? \"none\" : v.c_str());",
    )
    replace_once(
        "gpu/shim/input/bindings.cpp",
        "    const int m=g_mouse[a].load();\n    if(m) {if(!value.empty())value+=\", \";value+=m==6?\"WheelUp\":m==7?\"WheelDown\":\"Mouse\"+std::to_string(m);}\n    return value.empty()?\"none\":value;",
        "    const int m=g_mouse[a].load();\n    if(m) {if(!value.empty())value+=\", \";value+=m==6?\"WheelUp\":m==7?\"WheelDown\":\"Mouse\"+std::to_string(m);}\n    if(const char* p=pad_token(g_pad[a].load())) {if(!value.empty())value+=\", \";value+=p;}\n    else if(!value.empty()) value+=\", PadNone\";\n    return value.empty()?\"none\":value;",
    )

    # Show the gamepad binding in the native controls list and text prompts.
    regex_once(
        "gpu/shim/input/bindings.cpp",
        r"void host_binding_describe\(int action, char\* out, std::size_t n\) \{.*?\n\}\n\nvoid host_binding_prompt",
        '''void host_binding_describe(int action, char* out, std::size_t n) {
    if (!n) return;
    const char* k = scancode_name(host_binding_key(action));
    if (k && std::strcmp(k, "`") == 0) k = "` (backtick)";
    const int m = host_binding_mouse(action);
    const char* ms = m >= 1 && m <= kMouseInputs ? kMouseNames[m] : nullptr;
    const char* p = action >= 0 && action < kBindCount ? pad_label(g_pad[action].load()) : nullptr;
    std::string value;
    if (k) value = k;
    if (ms) { if (!value.empty()) value += " / "; value += ms; }
    if (p) { if (!value.empty()) value += " / "; value += p; }
    if (value.empty()) value = "Unbound";
    std::snprintf(out, n, "%s", value.c_str());
}

void host_binding_prompt''',
        flags=re.S,
    )
    replace_once(
        "gpu/shim/input/bindings.cpp",
        "    const char* what = k ? k : m >= 1 && m <= kMouseInputs ? kMouseShort[m] : nullptr;\n    if (what) std::snprintf(out, n, \"%s\", what);",
        "    const char* p = action >= 0 && action < kBindCount ? pad_label(g_pad[action].load()) : nullptr;\n    const char* what = k ? k : m >= 1 && m <= kMouseInputs ? kMouseShort[m] : p;\n    if (what) std::snprintf(out, n, \"%s\", what);",
    )

    # Controller states are merged with key and mouse states before one apply pass.
    replace_once(
        "gpu/shim/input/bindings.cpp",
        "void host_bindings_mouse_held(std::uint32_t buttons, bool held[kBindCount]) {\n    for (int a = 0; a < kBindCount; ++a) {\n        const int m = g_mouse[a].load(std::memory_order_relaxed);\n        held[a] = m >= 1 && m <= kMouseInputs && (buttons & (1u << (m - 1)));\n    }\n    g_walk_on_mouse.store(held[kBindWalk], std::memory_order_relaxed);\n    note_debug_key(1, held[kBindDebugMenu]);\n}\n\nvoid host_bindings_apply",
        "void host_bindings_mouse_held(std::uint32_t buttons, bool held[kBindCount]) {\n    for (int a = 0; a < kBindCount; ++a) {\n        const int m = g_mouse[a].load(std::memory_order_relaxed);\n        held[a] = m >= 1 && m <= kMouseInputs && (buttons & (1u << (m - 1)));\n    }\n    g_walk_on_mouse.store(held[kBindWalk], std::memory_order_relaxed);\n    note_debug_key(1, held[kBindDebugMenu]);\n}\n\nvoid host_bindings_pad_held(std::uint32_t buttons, std::uint8_t left_trigger, std::uint8_t right_trigger, bool held[kBindCount]) {\n    for (int a = 0; a < kBindCount; ++a) {\n        const int p = g_pad[a].load(std::memory_order_relaxed);\n        bool down = p >= 0 && p < SDL_GAMEPAD_BUTTON_COUNT && p < 32 && (buttons & (1u << p));\n        if (p == kPadLeftTrigger) down = left_trigger > 30;\n        if (p == kPadRightTrigger) down = right_trigger > 30;\n        held[a] = held[a] || down;\n    }\n}\n\nvoid host_bindings_apply",
    )

    # Roll becomes a timed press pulse; Sprint holds Circle until released.
    replace_once(
        "gpu/shim/input/bindings.cpp",
        "void host_bindings_apply(const bool held[kBindCount], bool strong, PadState& p) {\n    bool any = false;\n    for (int a = 0; a < kBindCount; ++a) {",
        "void host_bindings_apply(const bool held[kBindCount], bool strong, PadState& p) {\n    bool any = false;\n    const bool roll_held = held[kBindRoll];\n    const bool roll_was_held = g_roll_prev.exchange(roll_held, std::memory_order_relaxed);\n    const std::int64_t now = now_ms();\n    if (roll_held && !roll_was_held) g_roll_until_ms.store(now + 70, std::memory_order_relaxed);\n    const bool roll_pulse = now < g_roll_until_ms.load(std::memory_order_relaxed);\n    for (int a = 0; a < kBindCount; ++a) {\n        if (a == kBindRoll) {\n            if (roll_pulse) { p.buttons |= kCircle; any = true; }\n            continue;\n        }",
    )

    # New controller capture function.
    marker = "int host_bind_capture_take_done() { return g_capture_done.exchange(-1); }"
    pad_capture = '''bool host_bind_capture_pad(int button) {
    const int a = g_capture.load(std::memory_order_relaxed);
    if (a < 0) return false;
    if (!((button >= 0 && button < SDL_GAMEPAD_BUTTON_COUNT) || button == kPadLeftTrigger || button == kPadRightTrigger)) return false;
    g_pad[a].store(button, std::memory_order_relaxed);
    finish(a, "rebound");
    return true;
}

'''
    replace_once("gpu/shim/input/bindings.cpp", marker, pad_capture + marker)
    replace_once(
        "gpu/shim/input/bindings.cpp",
        "    g_key[action].store(0, std::memory_order_relaxed);\n    g_mouse[action].store(0, std::memory_order_relaxed);\n    g_serial.fetch_add(1, std::memory_order_relaxed);",
        "    g_key[action].store(0, std::memory_order_relaxed);\n    g_mouse[action].store(0, std::memory_order_relaxed);\n    g_pad[action].store(kPadUnbound, std::memory_order_relaxed);\n    g_serial.fetch_add(1, std::memory_order_relaxed);",
    )
    replace_once(
        "gpu/shim/input/bindings.cpp",
        "        g_key[a].store(0, std::memory_order_relaxed);\n        g_mouse[a].store(0, std::memory_order_relaxed);\n        finish(a, \"unbound\");",
        "        g_key[a].store(0, std::memory_order_relaxed);\n        g_mouse[a].store(0, std::memory_order_relaxed);\n        g_pad[a].store(kPadUnbound, std::memory_order_relaxed);\n        finish(a, \"unbound\");",
    )

    # Input bridge signature: carry physical SDL pad state into the binding system.
    h = "gpu/shim/input/input.h"
    if "#include <stdint.h>" not in changed[h]:
        first = changed[h].splitlines()[0]
        changed[h] = changed[h].replace(first, first + "\n#include <stdint.h>", 1)
    regex_once(h, r"int bbgpu_pc_input\(BbPcPad\*[^;]*;", "int bbgpu_pc_input(BbPcPad*, const bool* keys, int nkeys, int gamepad_present, uint32_t pad_buttons, uint8_t pad_l2, uint8_t pad_r2);", flags=0)
    if "bbgpu_pc_input_enabled" not in changed[h]:
        regex_once(h, r"(int bbgpu_pc_input\([^;]*;)", r"\1\nint bbgpu_pc_input_enabled(void);", flags=0)

    # Teach SDL events to capture controller buttons and triggers.
    replace_once(
        "gpu/shim/input/input.cpp",
        "    if(e.type==SDL_EVENT_GAMEPAD_BUTTON_DOWN || (e.type==SDL_EVENT_GAMEPAD_AXIS_MOTION && std::abs(e.gaxis.value)>8000))device=InputDevice::Pad;\n    if(blocked)return;",
        "    if(e.type==SDL_EVENT_GAMEPAD_BUTTON_DOWN || (e.type==SDL_EVENT_GAMEPAD_AXIS_MOTION && std::abs(e.gaxis.value)>8000))device=InputDevice::Pad;\n    if(blocked)return;\n    if(e.type==SDL_EVENT_GAMEPAD_BUTTON_DOWN) host_bind_capture_pad(static_cast<int>(e.gbutton.button));\n    if(e.type==SDL_EVENT_GAMEPAD_AXIS_MOTION && e.gaxis.value>8000) {\n        if(e.gaxis.axis==SDL_GAMEPAD_AXIS_LEFT_TRIGGER) host_bind_capture_pad(SDL_GAMEPAD_BUTTON_COUNT);\n        if(e.gaxis.axis==SDL_GAMEPAD_AXIS_RIGHT_TRIGGER) host_bind_capture_pad(SDL_GAMEPAD_BUTTON_COUNT+1);\n    }",
    )
    replace_once(
        "gpu/shim/input/input.cpp",
        "extern \"C\" int bbgpu_pc_input(BbPcPad* d,const bool* keys,int nkeys,int gamepad_present) {\n    if(!active || !BbSettings::Get().pc_controls){wanted_relative=false;return 0;}\n    auto& s=BbSettings::Get();\n    PadState p;p.buttons=d->buttons;\n    p.lx=d->lx;p.ly=d->ly;p.rx=d->rx;p.ry=d->ry;p.l2=d->l2;p.r2=d->r2;",
        "extern \"C\" int bbgpu_pc_input_enabled(void) { return active && BbSettings::Get().pc_controls; }\n\nextern \"C\" int bbgpu_pc_input(BbPcPad* d,const bool* keys,int nkeys,int gamepad_present,std::uint32_t pad_buttons,std::uint8_t pad_l2,std::uint8_t pad_r2) {\n    if(!active || !BbSettings::Get().pc_controls){wanted_relative=false;return 0;}\n    auto& s=BbSettings::Get();\n    PadState p;p.buttons=0;\n    p.lx=d->lx;p.ly=d->ly;p.rx=d->rx;p.ry=d->ry;p.l2=0;p.r2=0;",
    )
    replace_once(
        "gpu/shim/input/input.cpp",
        "    bool any=buttons!=0;for(int i=0;keys&&i<nkeys;i++)any|=keys[i];\n    host_bind_capture_note_held(any);",
        "    bool any=buttons!=0 || pad_buttons!=0 || pad_l2>30 || pad_r2>30;for(int i=0;keys&&i<nkeys;i++)any|=keys[i];\n    host_bind_capture_note_held(any);",
    )
    replace_once(
        "gpu/shim/input/input.cpp",
        "        host_bindings_apply(held,held[kBindStrongMod],p);\n        if(menu) {",
        "        if(!menu) {\n            bool mh[kBindCount]={};host_bindings_mouse_held(buttons|edges|(scroll>0?32:scroll<0?64:0),mh);\n            for(int i=0;i<kBindCount;i++) held[i]=held[i]||mh[i];\n        }\n        host_bindings_pad_held(pad_buttons,pad_l2,pad_r2,held);\n        if(menu) { held[kBindRoll]=false; held[kBindSprint]=false; held[kBindInteract]=false; }\n        else { held[kBindConfirm]=false; held[kBindBack]=false; }\n        host_bindings_apply(held,held[kBindStrongMod],p);\n        if(menu) {",
    )
    replace_once(
        "gpu/shim/input/input.cpp",
        "        }else {\n            bool mh[kBindCount]={};host_bindings_mouse_held(buttons|edges|(scroll>0?32:scroll<0?64:0),mh);\n            host_bindings_apply(mh,held[kBindStrongMod]||mh[kBindStrongMod],p);\n            float x,y;if(camera && mouse_camera_flick(x,y)){",
        "        }else {\n            float x,y;if(camera && mouse_camera_flick(x,y)){",
    )

    # Keep existing controller touch surface data, but generate click gestures from the new binds.
    replace_once(
        "src/runtime_pad.c",
        "        // Back/Select on pads without a touch surface is a left-side click.\n        if ((d->buttons & BTN_TOUCHPAD) && !d->touch_count) touch_click(d,0);\n        if (touch_right) touch_click(d,1);",
        "        // With PC Controls active, the host action bindings synthesize these clicks.\n        // Keep the legacy mapping for the original controller path.\n        if (!bbgpu_pc_input_enabled()) {\n            if ((d->buttons & BTN_TOUCHPAD) && !d->touch_count) touch_click(d,0);\n            if (touch_right) touch_click(d,1);\n        }",
    )
    replace_once(
        "src/runtime_pad.c",
        "    if(bbgpu_pc_input(&pc,k,nk,g!=NULL)) {",
        "    uint32_t pad_buttons=0;\n    uint8_t pad_l2=0,pad_r2=0;\n    if(g) {\n        for(int b=0;b<SDL_GAMEPAD_BUTTON_COUNT && b<32;++b)\n            if(SDL_GetGamepadButton(g,(SDL_GamepadButton)b)) pad_buttons|=((uint32_t)1u<<b);\n        pad_l2=trigger(SDL_GetGamepadAxis(g,SDL_GAMEPAD_AXIS_LEFT_TRIGGER));\n        pad_r2=trigger(SDL_GetGamepadAxis(g,SDL_GAMEPAD_AXIS_RIGHT_TRIGGER));\n    }\n    if(bbgpu_pc_input(&pc,k,nk,g!=NULL,pad_buttons,pad_l2,pad_r2)) {",
    )

    # Keep existing pages intact; Sprint is displayed alongside the other final-page action.
    replace_once(
        "gpu/shim/engine/option_menu.cpp",
        '"Camera and Menus",\n                                               "Other"};',
        '"Camera and Menus",\n                                               "Other / Sprint"};',
    )
    replace_once(
        "gpu/shim/engine/option_menu.cpp",
        'std::snprintf(help, sizeof(help), "%s Enter or click to rebind, Delete to clear.", b.help);',
        'std::snprintf(help, sizeof(help), "%s Enter, click, or press a controller button to rebind. Delete clears.", b.help);',
    )
    replace_once(
        "gpu/shim/engine/option_menu.cpp",
        'to_utf16(g_keys_text[row], "Press a key...");',
        'to_utf16(g_keys_text[row], "Press an input...");',
    )

except Exception as exc:
    print("ERROR: Patch not applied. No source files were written.")
    print(exc)
    sys.exit(2)

# The edits have all passed the exact-match checks. Back up the originals, then commit them.
backup_dir = ROOT / ("dodge_sprint_backup_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
backup_dir.mkdir()
for f in FILES:
    dst = backup_dir / f
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(original[f], encoding="utf-8", newline="")
for f in FILES:
    (ROOT / f).write_text(changed[f], encoding="utf-8", newline="")

print("Dodge/Sprint source changes applied.")
print(f"Original files backed up to: {backup_dir}")
print("Next: inspect git diff, build, then test keyboard, mouse, and controller inputs.")
