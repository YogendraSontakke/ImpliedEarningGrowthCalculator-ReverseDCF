from flask import Flask, request, render_template, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages

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
    form_data = {
        'current_earnings': '',
        'discount_rate': '',
        'years': '',
        'terminal_multiple': '',
        'current_valuation': ''
    }

    if request.method == 'POST':
        try:
            current_earnings = float(request.form['current_earnings'])
            discount_rate = float(request.form['discount_rate']) / 100.0
            years = int(request.form['years'])
            terminal_multiple = float(request.form['terminal_multiple'])
            current_valuation = float(request.form['current_valuation'])
            
            form_data = {
                'current_earnings': current_earnings,
                'discount_rate': discount_rate * 100,
                'years': years,
                'terminal_multiple': terminal_multiple,
                'current_valuation': current_valuation
            }

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
                'future_earnings': future_earnings,
                'market_cap': market_cap,
                'absolute_return': absolute_return
            }
        except ValueError:
            error = "Please provide valid numeric inputs."
            flash(error, 'danger')

    return render_template('index.html', result=result, error=error, form_data=form_data)

if __name__ == '__main__':
    app.run(debug=False)
