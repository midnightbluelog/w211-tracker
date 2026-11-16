"""
Decode the publicly known parts of an older Mercedes-Benz VIN.

A Mercedes VIN like  WDB2110061A123456  breaks down as:
  WDB     who made it (Mercedes-Benz passenger car)
  211     the model series (W211 = E-Class 2002-2009)
  006     the variant (211.006 = E 220 CDI saloon)
  rest    plant and serial number

Full factory build data (options, colours) is NOT public, so we only decode this part.
"""

MAKERS = {
    "WDB": "Mercedes-Benz",
    "WDD": "Mercedes-Benz",
    "WDC": "Mercedes-Benz (SUV)",
    "WDF": "Mercedes-Benz (van)",
}

SERIES = {
    "124": "E-Class W124 (1984-1997)",
    "210": "E-Class W210 (1995-2002)",
    "211": "E-Class W211 (2002-2009)",
    "202": "C-Class W202 (1993-2000)",
    "203": "C-Class W203 (2000-2007)",
    "140": "S-Class W140 (1991-1998)",
    "220": "S-Class W220 (1998-2005)",
    "208": "CLK C208 (1997-2003)",
    "209": "CLK C209 (2002-2010)",
    "129": "SL R129 (1989-2001)",
    "230": "SL R230 (2001-2012)",
    "163": "M-Class W163 (1997-2005)",
}

# Exact variants we're sure about. Grow this list carefully, one verified entry at a time.
VARIANTS = {
    "211006": {"model": "E 220 CDI", "engine": "OM646 2.2 diesel", "body": "Saloon"},
    "211206": {"model": "E 220 CDI", "engine": "OM646 2.2 diesel", "body": "Estate (S211)"},
}


def decode_vin(vin):
    """Return what we can tell from the VIN, and say clearly what we can't."""
    vin = str(vin).strip().upper().replace(" ", "")
    result = {"vin": vin, "valid": False, "notes": []}

    if len(vin) != 17:
        result["notes"].append("A VIN has exactly 17 characters.")
        return result
    if any(c in vin for c in "IOQ"):
        result["notes"].append("VINs never contain the letters I, O or Q. Check for a typo (1 vs I, 0 vs O).")
        return result

    result["valid"] = True
    maker = MAKERS.get(vin[:3])
    if not maker:
        result["notes"].append(f"'{vin[:3]}' isn't a Mercedes-Benz maker code we know.")
        return result
    result["make"] = maker

    series_code, variant_code = vin[3:6], vin[3:9]
    result["model_code"] = f"{series_code}.{vin[6:9]}"
    if series_code in SERIES:
        result["series"] = SERIES[series_code]
    else:
        result["notes"].append(f"Model series {series_code} isn't in our list yet.")

    if variant_code in VARIANTS:
        result.update(VARIANTS[variant_code])
    else:
        result["notes"].append(f"Exact variant {result['model_code']} not in our list yet, so fill in the model by hand.")

    result["notes"].append("European Mercedes VINs don't reliably encode the model year, so enter it yourself.")
    return result


if __name__ == "__main__":
    for test in ["WDB2110061A123456", "WDB2112061A123456", "WDB2030071A123456", "ABC", "WDB21100O1A123456"]:
        print(test, "->", decode_vin(test))
