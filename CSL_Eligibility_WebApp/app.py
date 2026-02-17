from flask import Flask, render_template, request

app = Flask(__name__)

def calculate_emi(principal, annual_rate, years):
    r = annual_rate / 12
    n = years * 12
    if r == 0:
        return principal / n
    emi = principal * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)
    return emi

def max_loan_from_emi(max_emi, annual_rate, years):
    r = annual_rate / 12
    n = years * 12
    if r == 0:
        return max_emi * n
    pv = max_emi * (((1 + r) ** n) - 1) / (r * ((1 + r) ** n))
    return pv

@app.route("/", methods=["GET", "POST"])
def index():
    result = {}

    if request.method == "POST":
        income = float(request.form["income"])
        existing_emi = float(request.form["existing_emi"])
        loan_amount = float(request.form["loan_amount"])
        roi = float(request.form["roi"]) / 100
        tenure = int(request.form["tenure"])
        property_value = float(request.form["property_value"])
        foir = float(request.form["foir"]) / 100
        max_ltv = float(request.form["max_ltv"]) / 100
        cibil = int(request.form["cibil"])

        foir_allowed_emi = (income * foir) - existing_emi
        proposed_emi = calculate_emi(loan_amount, roi, tenure)
        surplus = foir_allowed_emi - proposed_emi
        ltv = (loan_amount / property_value) if property_value > 0 else 0

        max_loan_foir = max_loan_from_emi(foir_allowed_emi, roi, tenure)
        max_loan_ltv = property_value * max_ltv
        final_max_loan = min(max_loan_foir, max_loan_ltv)

        eligible = (proposed_emi <= foir_allowed_emi) and (ltv <= max_ltv) and (cibil >= 650)

        result = {
            "foir_allowed_emi": round(foir_allowed_emi, 2),
            "proposed_emi": round(proposed_emi, 2),
            "surplus": round(surplus, 2),
            "ltv": round(ltv * 100, 2),
            "max_loan_foir": round(max_loan_foir, 2),
            "max_loan_ltv": round(max_loan_ltv, 2),
            "final_max_loan": round(final_max_loan, 2),
            "status": "ELIGIBLE" if eligible else "NOT ELIGIBLE"
        }

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)