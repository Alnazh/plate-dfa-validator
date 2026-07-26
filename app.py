from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Transition table of the DFA, states map symbol type to next state
TRANSITIONS = {
    "q0": {"L": "q1"},
    "q1": {"L": "q2", "S": "q3"},
    "q2": {"S": "q3"},
    "q3": {"D": "q4"},
    "q4": {"D": "q5", "S": "q8"},
    "q5": {"D": "q6", "S": "q8"},
    "q6": {"D": "q7", "S": "q8"},
    "q7": {"S": "q8"},
    "q8": {"L": "q9"},
    "q9": {"L": "q10"},
    "q10": {"L": "q11"},
    "q11": {},
}

# States where the DFA accepts the input if reached at the end of the string
ACCEPTING_STATES = {"q9", "q10", "q11"}

# Human readable description of every state, shown in the trace table
STATE_LABELS = {
    "q0": "Awal",
    "q1": "1 huruf kode wilayah",
    "q2": "2 huruf kode wilayah",
    "q3": "Menunggu nomor urut",
    "q4": "1 digit nomor urut",
    "q5": "2 digit nomor urut",
    "q6": "3 digit nomor urut",
    "q7": "4 digit nomor urut",
    "q8": "Menunggu huruf seri",
    "q9": "1 huruf seri (diterima)",
    "q10": "2 huruf seri (diterima)",
    "q11": "3 huruf seri (diterima)",
    "qtrap": "Ditolak",
}

# What symbol the DFA is waiting for when it stands on a given state
EXPECTED_LABELS = {
    "q0": "huruf kode wilayah",
    "q1": "huruf kedua kode wilayah, atau langsung spasi",
    "q2": "spasi sebelum nomor urut",
    "q3": "digit nomor urut",
    "q4": "digit lanjutan, atau spasi",
    "q5": "digit lanjutan, atau spasi",
    "q6": "digit lanjutan, atau spasi",
    "q7": "spasi sebelum huruf seri",
    "q8": "huruf seri",
    "q9": "huruf seri lanjutan",
    "q10": "huruf seri lanjutan",
}

# x, y coordinates of every state used to draw the DFA diagram
NODE_POSITIONS = {
    "q0": (60, 190), "q1": (170, 190), "q2": (280, 90), "q3": (390, 190),
    "q4": (500, 190), "q5": (610, 190), "q6": (720, 190), "q7": (830, 190),
    "q8": (940, 190), "q9": (1050, 190), "q10": (1150, 190), "q11": (1250, 190),
    "qtrap": (655, 330),
}

# Every legal edge of the diagram: source, target, symbol, drawing style
EDGE_DEFS = [
    ("q0", "q1", "L", "straight"),
    ("q1", "q2", "L", "diag"),
    ("q1", "q3", "S", "straight"),
    ("q2", "q3", "S", "diag"),
    ("q3", "q4", "D", "straight"),
    ("q4", "q5", "D", "straight"),
    ("q4", "q8", "S", "dip1"),
    ("q5", "q6", "D", "straight"),
    ("q5", "q8", "S", "dip2"),
    ("q6", "q7", "D", "straight"),
    ("q6", "q8", "S", "dip3"),
    ("q7", "q8", "S", "straight"),
    ("q8", "q9", "L", "straight"),
    ("q9", "q10", "L", "straight"),
    ("q10", "q11", "L", "straight"),
]


# Daftar kode huruf wilayah, dikelompokkan per pulau untuk halaman info
KODE_WILAYAH = {
    "Sumatera": [
        ("BL", "Aceh"),
        ("BB", "Sumatera Utara bagian Tapanuli"),
        ("BK", "Sumatera Utara bagian Medan dan sekitarnya"),
        ("BA", "Sumatera Barat"),
        ("BM", "Riau"),
        ("BP", "Kepulauan Riau"),
        ("BG", "Sumatera Selatan"),
        ("BN", "Kepulauan Bangka Belitung"),
        ("BE", "Lampung"),
        ("BD", "Bengkulu"),
        ("BH", "Jambi"),
    ],
    "Jawa": [
        ("A", "Banten"),
        ("B", "DKI Jakarta, Depok, Bekasi"),
        ("D", "Bandung dan sekitarnya"),
        ("E", "Cirebon, Kuningan, Majalengka, Indramayu"),
        ("F", "Bogor, Sukabumi, Cianjur"),
        ("T", "Purwakarta, Karawang, Subang"),
        ("Z", "Garut, Tasikmalaya, Sumedang, Ciamis, Banjar"),
        ("G", "Pekalongan, Tegal, Brebes, Batang, Pemalang"),
        ("H", "Semarang, Kendal, Salatiga, Demak"),
        ("K", "Pati, Kudus, Jepara, Rembang, Blora, Grobogan"),
        ("R", "Banyumas, Cilacap, Purbalingga, Banjarnegara"),
        ("AA", "Magelang, Purworejo, Kebumen, Temanggung, Wonosobo"),
        ("AD", "Surakarta, Sukoharjo, Boyolali, Klaten, Sragen"),
        ("AB", "Daerah Istimewa Yogyakarta"),
        ("L", "Kota Surabaya"),
        ("M", "Madura"),
        ("N", "Malang, Pasuruan, Probolinggo"),
        ("P", "Jember, Banyuwangi, dan wilayah eks Karesidenan Besuki"),
        ("S", "Bojonegoro, Tuban, Lamongan, Mojokerto"),
        ("W", "Sidoarjo, Gresik"),
        ("AE", "Madiun dan sekitarnya"),
        ("AG", "Kediri dan sekitarnya"),
    ],
    "Bali dan Nusa Tenggara": [
        ("DK", "Bali"),
        ("DR", "Nusa Tenggara Barat bagian Lombok"),
        ("EA", "Nusa Tenggara Barat bagian Sumbawa"),
        ("EB", "Nusa Tenggara Timur bagian Flores dan Timor"),
    ],
    "Kalimantan": [
        ("KB", "Kalimantan Barat"),
        ("DA", "Kalimantan Selatan"),
        ("KH", "Kalimantan Tengah"),
        ("KT", "Kalimantan Timur"),
        ("KU", "Kalimantan Utara"),
    ],
    "Sulawesi": [
        ("DB", "Sulawesi Utara bagian daratan"),
        ("DL", "Sulawesi Utara bagian kepulauan Sangihe, Talaud, Sitaro"),
        ("DM", "Gorontalo"),
        ("DN", "Sulawesi Tengah"),
        ("DC", "Sulawesi Barat"),
        ("DD", "Sulawesi Selatan"),
        ("DT", "Sulawesi Tenggara"),
    ],
    "Maluku dan Papua": [
        ("DE", "Maluku"),
        ("DG", "Maluku Utara"),
        ("PA", "Papua"),
        ("PB", "Papua Barat"),
    ],
}


def classify(char):
    # Map a raw character to the DFA alphabet: L, D, S, or None if invalid
    if char.isalpha():
        return "L"
    if char.isdigit():
        return "D"
    if char == " ":
        return "S"
    return None


def run_dfa(plate):
    # Simulate the DFA character by character and record every transition
    state = "q0"
    trace = []
    for char in plate:
        symbol = classify(char)
        next_state = TRANSITIONS.get(state, {}).get(symbol, "qtrap")
        trace.append({
            "char": char,
            "from_state": state,
            "from_label": STATE_LABELS[state],
            "to_state": next_state,
            "to_label": STATE_LABELS[next_state],
        })
        state = next_state
    accepted = state in ACCEPTING_STATES and len(plate) > 0
    return accepted, state, trace


def build_reason(plate, accepted, final_state, trace):
    # Build a human readable explanation of why the plate was rejected
    if accepted or not plate:
        return None
    for index, step in enumerate(trace):
        if step["to_state"] == "qtrap":
            expected = EXPECTED_LABELS.get(step["from_state"], "karakter lain")
            return {
                "position": index + 1,
                "char": step["char"],
                "expected": expected,
            }
    expected = EXPECTED_LABELS.get(final_state, "karakter tambahan")
    return {
        "position": len(plate),
        "char": None,
        "expected": expected,
    }


def build_breakdown(plate, accepted):
    # Split an accepted plate into region code, serial number, and series letters
    if not accepted:
        return None
    parts = plate.split(" ")
    return {"wilayah": parts[0], "nomor": parts[1], "seri": parts[2]}


def build_diagram(trace):
    # Compute which nodes and edges of the DFA diagram were actually visited
    visited_states = {"q0"}
    visited_edges = set()
    trap_from = None
    for step in trace:
        visited_states.add(step["from_state"])
        visited_states.add(step["to_state"])
        if step["to_state"] == "qtrap":
            if trap_from is None:
                trap_from = step["from_state"]
        else:
            visited_edges.add(f'{step["from_state"]}>{step["to_state"]}')
    return build_diagram_from(visited_states, visited_edges, trap_from)


def build_static_diagram():
    # Build the same diagram with nothing highlighted, used on the about page
    return build_diagram_from(set(), set(), None)


def build_diagram_from(visited_states, visited_edges, trap_from):
    # Shared diagram builder, used both for a live trace and for the plain structure
    nodes = []
    for state_id, (x, y) in NODE_POSITIONS.items():
        nodes.append({
            "id": state_id,
            "x": x,
            "y": y,
            "accepting": state_id in ACCEPTING_STATES,
            "is_trap": state_id == "qtrap",
            "active": state_id in visited_states,
        })

    edges = []
    for src, dst, symbol, kind in EDGE_DEFS:
        x1, y1 = NODE_POSITIONS[src]
        x2, y2 = NODE_POSITIONS[dst]
        edge_id = f"{src}>{dst}"
        if kind == "straight":
            path = f"M{x1 + 28},{y1} L{x2 - 28},{y2}"
            lx, ly = (x1 + x2) / 2, y1 - 12
        elif kind == "diag":
            if y1 > y2:
                path = f"M{x1 + 18},{y1 - 18} L{x2 - 16},{y2 + 18}"
            else:
                path = f"M{x1 + 16},{y1 + 18} L{x2 - 18},{y2 - 18}"
            lx, ly = (x1 + x2) / 2 + 16, (y1 + y2) / 2
        else:
            dip_y = {"dip1": 300, "dip2": 270, "dip3": 240}[kind]
            cx = (x1 + x2) / 2
            path = f"M{x1},{y1 + 22} Q{cx},{dip_y} {x2},{y2 + 22}"
            lx, ly = cx, dip_y + 16
        edges.append({
            "d": path,
            "symbol": symbol,
            "lx": lx,
            "ly": ly,
            "active": edge_id in visited_edges,
        })

    trap_edge = None
    if trap_from:
        x1, y1 = NODE_POSITIONS[trap_from]
        x2, y2 = NODE_POSITIONS["qtrap"]
        trap_edge = {"d": f"M{x1},{y1 + 24} L{x2},{y2 - 26}", "from": trap_from}

    return {"nodes": nodes, "edges": edges, "trap_edge": trap_edge}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/hasil", methods=["POST"])
def hasil():
    plate_input = request.form.get("plate", "").strip().upper()
    if not plate_input:
        return redirect(url_for("index"))
    accepted, final_state, trace = run_dfa(plate_input)
    result = {
        "plate": plate_input,
        "accepted": accepted,
        "final_state": final_state,
        "final_label": STATE_LABELS[final_state],
        "trace": trace,
        "reason": build_reason(plate_input, accepted, final_state, trace),
        "breakdown": build_breakdown(plate_input, accepted),
        "diagram": build_diagram(trace),
    }
    return render_template("hasil.html", result=result)


@app.route("/tentang")
def tentang():
    return render_template("about.html", diagram=build_static_diagram())


@app.route("/kode-wilayah")
def kode_wilayah():
    # Halaman referensi kode huruf wilayah dan informasi tambahan seputar pelat
    return render_template("wilayah.html", kode_wilayah=KODE_WILAYAH)


if __name__ == "__main__":
    app.run(debug=True)
