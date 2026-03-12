import functions
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "drugflashcards"

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/results", methods=["GET", "POST"])
def results():
    if request.method == "POST":
        drug_name = request.form["drug_name"]
        info = functions.get_all_drug_info(drug_name)

        if info is None:
            return render_template("index.html", error="Could not find any results for: " + drug_name)

        return render_template("results.html", info=info, drug_name=drug_name)

    else:
        return "Wrong HTTP method", 400


@app.route("/save", methods=["POST"])
def save():
    if "saved" not in session:
        session["saved"] = []

    drug_name = request.form["drug_name"]
    rxcui = request.form["rxcui"]
    name = request.form["name"]
    synonym = request.form["synonym"]
    drug_class = request.form["drug_class"]
    related = request.form["related"]

    card = {
        "drug_name": drug_name,
        "rxcui": rxcui,
        "name": name,
        "synonym": synonym,
        "drug_class": drug_class,
        "related": related
    }

    saved_names = [c["drug_name"] for c in session["saved"]]
    if drug_name not in saved_names:
        session["saved"].append(card)
        session.modified = True

    return redirect("/saved")


@app.route("/saved")
def saved():
    saved_cards = session.get("saved", [])
    return render_template("saved.html", saved_cards=saved_cards)


@app.route("/delete", methods=["POST"])
def delete():
    drug_name = request.form["drug_name"]
    if "saved" in session:
        session["saved"] = [c for c in session["saved"] if c["drug_name"] != drug_name]
        session.modified = True
    return redirect("/saved")


if __name__ == "__main__":
    app.run(debug=True)
