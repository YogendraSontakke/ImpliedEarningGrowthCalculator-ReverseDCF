from flask import Flask, request, render_template, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages

def calculate_implied_growth_rate(net_profit, discount_rate, terminal_multiple, market_capitalization, years=5):
    def calculate_dcf(growth_rate):
        cash_flows = [net_profit * ((1 + growth_rate) ** t) for t in range(1, years + 1)]
        terminal_value = cash_flows[-1] * terminal_multiple
        
        dcf = sum(cf / ((1 + discount_rate) ** t) for t, cf in enumerate(cash_flows, start=1))
        dcf += terminal_value / ((1 + discount_rate) ** years)
        
        return dcf

    low, high = 0.0, 1.0
    tolerance = 1e-6

    while high - low > tolerance:
        mid = (low + high) / 2
        dcf = calculate_dcf(mid)
        
        if dcf < market_capitalization:
            low = mid
        else:
            high = mid
    
    return (low + high) / 2

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None
    form_data = {
        'net_profit': '',
        'discount_rate': '',
        'years': '',
        'terminal_multiple': '',
        'market_capitalization': ''
    }

    if request.method == 'POST':
        try:
            net_profit = float(request.form['net_profit'])
            discount_rate = float(request.form['discount_rate']) / 100.0
            years = int(request.form['years'])
            terminal_multiple = float(request.form['terminal_multiple'])
            market_capitalization = float(request.form['market_capitalization'])
            
            form_data = {
                'net_profit': net_profit,
                'discount_rate': discount_rate * 100,
                'years': years,
                'terminal_multiple': terminal_multiple,
                'market_capitalization': market_capitalization
            }

            implied_growth_rate = calculate_implied_growth_rate(net_profit, discount_rate, terminal_multiple, market_capitalization, years)
            
            future_earnings = net_profit * ((1 + implied_growth_rate) ** years)
            market_cap = future_earnings * terminal_multiple
            absolute_return = 100 * ((market_cap - market_capitalization) / market_capitalization)
            
            result = {
                'net_profit': net_profit,
                'discount_rate': discount_rate,
                'years': years,
                'terminal_multiple': terminal_multiple,
                'market_capitalization': market_capitalization,
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
