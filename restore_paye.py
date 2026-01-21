
def calculate_paye(income):
    """
    Calculate Zambian PAYE (Monthly) - 2024/2025 Bands
    0 - 5,100      : 0%
    5,101 - 7,100  : 20%
    7,101 - 9,200  : 30%
    Over 9,200     : 37%
    """
    tax = 0
    income = float(income)
    
    # Band 1: 0 - 5100
    if income <= 5100:
        return 0
    
    # Band 2: 5101 - 7100 (Max Tax: 2000 * 0.20 = 400)
    taxable_band_2 = min(income - 5100, 2000)
    tax += taxable_band_2 * 0.20
    
    if income <= 7100:
        return tax
        
    # Band 3: 7101 - 9200 (Max Tax: 2100 * 0.30 = 630)
    taxable_band_3 = min(income - 7100, 2100)
    tax += taxable_band_3 * 0.30
    
    if income <= 9200:
        return tax
        
    # Band 4: Over 9200
    taxable_band_4 = income - 9200
    tax += taxable_band_4 * 0.37
    
    return tax

with open('d:/CHAU/DevOps/church/hr/views.py', 'a') as f:
    f.write('\n')
    f.write(calculate_paye.__code__.co_consts[0] if False else "") # Just easier to read the file ? No. 
    # Actually I can just write the source code from this file to the other.
    import inspect
    f.write(inspect.getsource(calculate_paye))
