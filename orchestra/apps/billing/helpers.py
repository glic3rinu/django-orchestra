def calculate_bases(lines):
    bases = {}
    for line in lines:
        try: bases[line.tax] = bases[line.tax] + line.price
        except KeyError: bases[line.tax] = line.price

    for key in bases:
        bases[key]=round(bases[key],2)
        
    return bases


def calculate_taxes(lines, bases):
    taxes = {}
    for tax in bases:
        taxes[tax] = round(((bases[tax] * float(tax)) / 100), 2)
    return taxes


def calculate_total(bases, taxes):
    total = 0
    for tax in bases:
        total += bases[tax] + taxes[tax]
    return total


def calculate_total_bases_and_taxes(lines):
    bases = calculate_bases(lines)
    taxes = calculate_taxes(lines, bases)
    total = calculate_total(bases, taxes)
    return total, bases, taxes
