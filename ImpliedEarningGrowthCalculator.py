from flask import Flask, request, render_template_string, redirect, url_for

app = Flask(__name__)

def calculate_implied_growth_rate(current_earnings, discount_rate, terminal_multiple, current_valuation, years=5):
    def calculate_dcf(growth_rate):
        cash_flows = [current_earnings * ((1 + growth_rate) ** t) for t in range(1, years + 1)]
        terminal_value = cash_flows[-1] * terminal_multiple
        
        dcf = sum(cf / ((1 + discount_rate) ** t) for t, cf in enumerate(cash_flows, start=1))
        dcf += terminal_value / ((1 + discount_rate) ** years)
        
        return dcf

    low, high = 0.0, 1.0
    tolerance = 1e-6

    while high - low > tolerance:
        mid = (low + high) / 2
        dcf = calculate_dcf(mid)
        
        if dcf < current_valuation:
            low = mid
        else:
            high = mid
    
    return (low + high) / 2

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None
    if request.method == 'POST':
        try:
            current_earnings = float(request.form['current_earnings'])
            discount_rate = float(request.form['discount_rate'])
            if discount_rate is None:
                return jsonify({"error": "Discount rate is required"}), 400     
            discount_rate /= 100.0
            years = int(request.form['years'])
            terminal_multiple = float(request.form['terminal_multiple'])
            current_valuation = float(request.form['current_valuation'])
            
            implied_growth_rate = calculate_implied_growth_rate(current_earnings, discount_rate, terminal_multiple, current_valuation, years)
            
            future_earnings = current_earnings * ((1 + implied_growth_rate) ** years)
            market_cap = future_earnings * terminal_multiple
            absolute_return = 100 * ((market_cap - current_valuation) / current_valuation)
            
            result = {
                'current_earnings': current_earnings,
                'discount_rate': discount_rate,
                'years': years,
                'terminal_multiple': terminal_multiple,
                'current_valuation': current_valuation,
                'implied_growth_rate': implied_growth_rate,
                'market_cap': market_cap,
                'absolute_return': absolute_return
            }
        except ValueError:
            error = "Please provide valid numeric inputs."
    else:
        # Retrieve parameters from URL
        current_earnings = request.args.get('current_earnings', type=float)
        discount_rate = request.args.get('discount_rate', type=float) / 100.0
        years = request.args.get('years', type=int)
        terminal_multiple = request.args.get('terminal_multiple', type=float)
        current_valuation = request.args.get('current_valuation', type=float)

        if all(v is not None for v in [current_earnings, discount_rate, years, terminal_multiple, current_valuation]):
            implied_growth_rate = calculate_implied_growth_rate(current_earnings, discount_rate, terminal_multiple, current_valuation, years)
            
            future_earnings = current_earnings * ((1 + implied_growth_rate) ** years)
            market_cap = future_earnings * terminal_multiple
            absolute_return = 100 * ((market_cap - current_valuation) / current_valuation)

            result = {
                'current_earnings': current_earnings,
                'discount_rate': discount_rate,
                'years': years,
                'terminal_multiple': terminal_multiple,
                'current_valuation': current_valuation,
                'implied_growth_rate': implied_growth_rate,
                'market_cap': market_cap,
                'absolute_return': absolute_return
            }
    
    return render_template_string(TEMPLATE, result=result, error=error)

TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>Implied Earning Growth Calculator - Reverse DCF</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
    <style>
        body {
            background-color: #f8f9fa;
        }
        h1, h2 {
            color: #007bff;
        }
        .bright-section, .history-section {
            background-color: #e9ecef;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container mt-5">
        <h1 class="text-center mb-4">Implied Earning Growth Calculator - Reverse DCF</h1>
        
        <div class="bright-section">
            <h2>Features</h2>
            <ul>
                <li>Intuitive interface for easy input.</li>
                <li>Real-time calculations to assist investment decisions.</li>
                <li>Comprehensive results with detailed summaries.</li>
            </ul>
        </div>
        
        <form method="post" class="mb-4">
            <div class="form-group">
                <label for="current_earnings">Current Earnings (₹):</label>
                <input type="text" class="form-control" id="current_earnings" name="current_earnings" required>
            </div>
            <div class="form-group">
                <label for="discount_rate">Discount Rate / Expected Rate of Return (%):</label>
                <input type="text" class="form-control" id="discount_rate" name="discount_rate" required>
            </div>
            <div class="form-group">
                <label for="years">Years:</label>
                <input type="text" class="form-control" id="years" name="years" required>
            </div>
            <div class="form-group">
                <label for="terminal_multiple">Terminal P/E Multiple:</label>
                <input type="text" class="form-control" id="terminal_multiple" name="terminal_multiple" required>
            </div>
            <div class="form-group">
                <label for="current_valuation">Current Valuation (₹):</label>
                <input type="text" class="form-control" id="current_valuation" name="current_valuation" required>
            </div>
            <button type="submit" name="calculate" class="btn btn-primary btn-block">Calculate</button>
            <button type="reset" class="btn btn-secondary btn-block">Reset</button>
        </form>
        
        {% if error %}
        <div class="alert alert-danger" role="alert">
            {{ error }}
        </div>
        {% endif %}
        
        {% if result %}
        <h2>Input:</h2>
        <ul class="list-group">
            <li class="list-group-item">Current Earnings: ₹{{ result.current_earnings }}</li>
            <li class="list-group-item">Discount Rate / Expected Rate of Return: {{ result.discount_rate * 100 }}%</li>
            <li class="list-group-item">Years: {{ result.years }}</li>
            <li class="list-group-item">Terminal P/E Multiple: {{ result.terminal_multiple }}</li>
            <li class="list-group-item">Current Valuation: ₹{{ result.current_valuation }}</li>
        </ul>
        
        <h2 class="mt-4">Result:</h2>
        <ul class="list-group">
            <li class="list-group-item">The implied earning growth rate is {{ (result.implied_growth_rate * 100) | round(2) }}%</li>
            <li class="list-group-item">Market Capitalization after {{ result.years }} years: ₹{{ result.market_cap | round(0) }}</li>
            <li class="list-group-item">Absolute Returns after {{ result.years }} years: {{ result.absolute_return | round(2) }}%</li>
        </ul>
        
        <h2 class="mt-4">Summary:</h2>
        <ul class="list-group">
            <li class="list-group-item">If you purchase the company with a market capitalization of ₹{{ result.current_valuation | round(0)}} crore and earnings of ₹{{ result.current_earnings | round(0)}} crore, expecting a {{ result.discount_rate * 100 }}% annual return over the next {{ result.years }} years, you assume a terminal price-to-earnings multiple of {{ result.terminal_multiple | round(0) }}. This implies that the company’s earnings must grow at an annual rate of {{ (result.implied_growth_rate * 100) | round(2) }}% during this period. Under these conditions, the company's market capitalization would reach approximately ₹{{ result.market_cap | round(0) }} crore, resulting in an absolute return of {{ result.absolute_return | round(2)}}%.</li>
        </ul>

        <h2 class="mt-4">Share This Link:</h2>
        <input type="text" class="form-control" readonly value="{{ request.url }}">
        {% endif %}
        
        <div class="history-section">
            <h2>History</h2>
            <p>This calculator is designed to empower investors with insights into implied earning growth, making it easier to evaluate potential investments.</p>
        </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"></script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True)
