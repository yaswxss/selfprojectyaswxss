import copy
from flask import Flask, request, jsonify, render_template

from Project_data_loader import load_all
from Project_segment_tree import SegmentTree
from Project_hash_table import HashTable


app = Flask(__name__)

dates, values, seller_stats, graph, states = load_all()

st = SegmentTree(values)
ht = HashTable()
for sid, stats in seller_stats.items():
    ht.put(sid, stats)


@app.route("/")
def index():
    return render_template("index.html", states=states, n_days=len(dates))


@app.route("/api/revenue")
def revenue():
    try:
        a = int(request.args.get("start", 0))
        b = int(request.args.get("end", len(values)))
    except ValueError:
        return jsonify({"error": "start/end должны быть числами"}), 400
    if a < 0 or b > len(values) or a >= b:
        return jsonify({"error": "некорректный диапазон"}), 400
    return jsonify({
        "total": round(st.query(a, b), 2),
        "from": str(dates[a]),
        "to": str(dates[b - 1]),
    })


@app.route("/api/seller/<seller_id>")
def seller(seller_id):
    data = ht.get(seller_id)
    if data is None:
        return jsonify({"error": "не найден"}), 404
    return jsonify({"seller_id": seller_id, **data})




if __name__ == "__main__":
    app.run(debug=True)