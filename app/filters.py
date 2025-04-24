from babel.numbers import format_currency

def format_currency(value):
    """Formatea un número como moneda."""
    try:
        return "{:,.2f}".format(float(value))
    except (ValueError, TypeError):
        return "0.00" 