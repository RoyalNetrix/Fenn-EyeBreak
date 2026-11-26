"""Fenn eye-break reminder (20-20-20 rule). Stdlib only, no network."""
import json, math, os, sys, threading, time

WORK_OPTS = [20, 30, 45, 60]   # minutes between breaks
BREAK = 20                     # seconds
DATA = os.environ.get("FENN_DATA_DIR") or os.environ.get("NOOK_DATA_DIR") or "."   # NOOK_DATA_DIR is the older name
CFG_PATH = os.path.join(DATA, "config.json")
out_lock, lock = threading.Lock(), threading.RLock()
cfg = {"work": 20, "sound": True, "popup": True}
mode, paused, end, pause_left = "work", False, 0.0, 0.0
page_open, tile_w, popped = False, 104, False


def send(msg):
    with out_lock:
        sys.stdout.write(json.dumps(msg) + "\n")
        sys.stdout.flush()


def load_cfg():
    try:
        with open(CFG_PATH, encoding="utf-8") as f:
            cfg.update(json.load(f))
    except (OSError, ValueError):
        pass


def save_cfg():
    try:
        os.makedirs(DATA, exist_ok=True)
        with open(CFG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f)
    except OSError as e:
        print("save failed:", e, file=sys.stderr)


def txt(text, **kw):
    return {"type": "text", "text": text, **kw}


def beep():
    if cfg["sound"]:
        try:
            import winsound
            winsound.MessageBeep()
        except Exception:
            pass


def rem():
    return pause_left if paused else max(0.0, end - time.time())


def start_work():
    global mode, paused, end
    mode, paused, end = "work", False, time.time() + cfg["work"] * 60


def start_break():
    global mode, paused, end, popped
    mode, paused, end = "break", False, time.time() + BREAK
    send({"type": "badge", "badge": {"kind": "pulse"}})
    popped = bool(cfg["popup"])
    if popped:
        send({"type": "show"})
    beep()


def finish_break():
    send({"type": "badge", "badge": None})
    if popped:
        send({"type": "close_page"})
    beep()
    start_work()


def clock(s):
    s = int(math.ceil(s))
    return f"{s // 60}:{s % 60:02d}"


def render():
    r = rem()
    total = BREAK if mode == "break" else cfg["work"] * 60
    prog = max(0.0, min(1.0, 1 - r / total))
    mins = math.ceil(r / 60)
    if mode == "break":
        icon, sub, big = "eye", "Look 20 ft away", f"{math.ceil(r)}s"
    elif paused:
        icon, sub, big = "pause", "Eye break paused", "Paused"
    else:
        icon, sub, big = None, "Next break", f"{mins} min"
    lead = ({"type": "icon", "icon": icon, "size": 26, "color": "accent"} if icon else
            {"type": "ring", "value": prog, "label": f"{mins}m", "size": 32})
    if tile_w < 70:
        tile = {"type": "column", "align": "center", "justify": "center", "children": [lead]}
    else:
        tile = {"type": "row", "align": "center", "gap": 10, "children": [
            lead, {"type": "column", "gap": 0, "children": [txt(sub, size="small", color="dim"), txt(big, size="title")]}]}
    send({"type": "tile", "view": tile})

    status = ("Look at something 20 ft (6 m) away until the timer ends." if mode == "break"
              else "Paused." if paused else "Working. A break will pop up when the ring fills.")
    page = {"type": "column", "gap": 10, "children": [
        {"type": "row", "align": "center", "gap": 16, "children": [
            {"type": "ring", "value": prog, "label": clock(r), "size": 72},
            {"type": "column", "gap": 2, "children": [
                txt("Break time" if mode == "break" else "Next break in " + clock(r), size="title"),
                txt(status, size="small", color="dim", wrap=True)]},
            {"type": "spacer"},
            {"type": "button", "id": "pause", "icon": "play" if paused else "pause", "tooltip": "Resume" if paused else "Pause"},
            {"type": "button", "id": "now", "icon": "eye", "tooltip": "Break now"}]},
        {"type": "row", "align": "center", "gap": 10, "children": [
            txt("Every", size="small", color="dim"),
            {"type": "chips", "id": "work", "options": [f"{m} min" for m in WORK_OPTS],
             "selected": WORK_OPTS.index(cfg["work"]) if cfg["work"] in WORK_OPTS else 0},
            {"type": "spacer"},
            {"type": "toggle", "id": "popup", "value": bool(cfg["popup"]), "label": "Pop up"},
            {"type": "toggle", "id": "sound", "value": bool(cfg["sound"]), "label": "Sound"}]}]}
    send({"type": "page", "view": page})


def ticker():
    n = 0
    while True:
        time.sleep(1)
        n += 1
        with lock:
            if not paused and rem() <= 0:
                start_break() if mode == "work" else finish_break()
                render()
            elif mode == "break" or page_open or n % 30 == 0:
                render()


def main():
    global page_open, tile_w, paused, pause_left, end
    try:
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass
    load_cfg()
    start_work()
    render()
    threading.Thread(target=ticker, daemon=True).start()
    for line in sys.stdin:
        try:
            msg = json.loads(line)
        except ValueError:
            continue
        t = msg.get("type")
        with lock:
            if t == "event":
                i, v = msg.get("id"), msg.get("value")
                if i == "pause":
                    if paused:
                        end, paused = time.time() + pause_left, False
                    else:
                        pause_left, paused = rem(), True
                elif i == "now":
                    start_break()
                elif i == "work" and isinstance(v, dict):
                    cfg["work"] = WORK_OPTS[max(0, min(len(WORK_OPTS) - 1, int(v.get("index", 0))))]
                    save_cfg()
                    if mode == "work":
                        start_work()
                elif i == "popup":
                    cfg["popup"] = bool(v)
                    save_cfg()
                elif i == "sound":
                    cfg["sound"] = bool(v)
                    save_cfg()
                render()
            elif t == "page_open":
                page_open = True
                render()
            elif t == "page_close":
                page_open = False
            elif t == "layout" and msg.get("target") == "tile":
                tile_w = msg.get("width", tile_w)
                render()
            elif t == "shutdown":
                save_cfg()
                return


if __name__ == "__main__":
    main()
