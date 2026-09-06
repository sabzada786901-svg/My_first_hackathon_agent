import json
from urllib.parse import quote
from urllib.request import urlopen
from agents import function_tool

from .models import (
    CropRecommendation,
    FertilizerPlan,
    ProfitEstimate,
)


def _crop_advisor(
    district: str,
    season: str,
    water_availability: str,
    land_size_acres: float,
) -> list[CropRecommendation]:

    if land_size_acres <= 0:
        raise ValueError("Land size must be greater than zero.")

    season = season.lower().strip()
    water = water_availability.lower().strip()

    if season == "rabi":

        if water in ["limited", "low"]:
            return [
                CropRecommendation(
                    crop="Chickpea",
                    expected_yield_per_acre=10,
                    expected_profit_per_acre=45000,
                    reason="Suitable for relatively limited-water Rabi conditions.",
                ),
                CropRecommendation(
                    crop="Lentil",
                    expected_yield_per_acre=7,
                    expected_profit_per_acre=38000,
                    reason="Can perform reasonably well with lower water requirements.",
                ),
            ]

        return [
            CropRecommendation(
                crop="Wheat",
                expected_yield_per_acre=35,
                expected_profit_per_acre=55000,
                reason="Major Rabi crop suitable for adequate irrigation.",
            ),
            CropRecommendation(
                crop="Chickpea",
                expected_yield_per_acre=10,
                expected_profit_per_acre=45000,
                reason="Strong Rabi alternative.",
            ),
        ]

    elif season == "kharif":

        if water in ["limited", "low"]:
            return [
                CropRecommendation(
                    crop="Millet",
                    expected_yield_per_acre=18,
                    expected_profit_per_acre=42000,
                    reason="Relatively suitable for lower-water conditions.",
                ),
                CropRecommendation(
                    crop="Sorghum",
                    expected_yield_per_acre=20,
                    expected_profit_per_acre=40000,
                    reason="Can tolerate relatively dry conditions.",
                ),
            ]

        return [
            CropRecommendation(
                crop="Maize",
                expected_yield_per_acre=30,
                expected_profit_per_acre=65000,
                reason="Can provide strong returns with sufficient irrigation.",
            ),
            CropRecommendation(
                crop="Cotton",
                expected_yield_per_acre=22,
                expected_profit_per_acre=70000,
                reason="Potentially profitable in suitable Kharif conditions.",
            ),
        ]

    else:
        raise ValueError("Season must be either Rabi or Kharif.")

#==================================
#crop advisor tool
#==================================
@function_tool
def crop_advisor(
    district: str,
    soil_type: str,
    season: str,
    water_availability: str,
    land_size_acres: float,
) -> list[CropRecommendation]:
    """
    Recommend suitable crops for a Pakistani farmer based on
    district, soil, season, water availability and land size.
    """
    return _crop_advisor(
        district,
        soil_type,
        season,
        water_availability,
        land_size_acres,
    )


def _fertilizer_calculator(
    crop: str,
    acres: float,
) -> FertilizerPlan:

    if acres <= 0:
        raise ValueError("Acres must be greater than zero.")

    crop = crop.lower().strip()

    fertilizer_data = {
        "wheat": {
            "urea_bags_per_acre": 2.5,
            "dap_bags_per_acre": 1.0,
        },
        "chickpea": {
            "urea_bags_per_acre": 0.5,
            "dap_bags_per_acre": 1.0,
        },
        "lentil": {
            "urea_bags_per_acre": 0.5,
            "dap_bags_per_acre": 0.75,
        },
        "maize": {
            "urea_bags_per_acre": 3.0,
            "dap_bags_per_acre": 1.5,
        },
        "cotton": {
            "urea_bags_per_acre": 2.5,
            "dap_bags_per_acre": 1.5,
        },
    }

    if crop not in fertilizer_data:
        raise ValueError(f"No fertilizer data available for '{crop}'.")

    urea_price = 5000
    dap_price = 12500

    data = fertilizer_data[crop]

    urea_bags = data["urea_bags_per_acre"] * acres
    dap_bags = data["dap_bags_per_acre"] * acres

    total_cost = (
        urea_bags * urea_price
        + dap_bags * dap_price
    )

    return FertilizerPlan(
        crop=crop.title(),
        acres=acres,
        urea_bags=round(urea_bags, 2),
        dap_bags=round(dap_bags, 2),
        total_cost_pkr=round(total_cost, 2),
    )


#==================================
#fertilizer calculator
#==================================
@function_tool
def fertilizer_calculator(
    crop: str,
    acres: float,
) -> FertilizerPlan:
    """
    Calculate approximate Urea and DAP requirements and
    total fertilizer cost.
    """
    return _fertilizer_calculator(crop, acres)


def _profit_estimator(
    crop: str,
    acres: float,
    expected_yield_per_acre: float,
    selling_price_per_unit: float,
    total_cost_per_acre: float,
) -> ProfitEstimate:

    if acres <= 0:
        raise ValueError("Acres must be greater than zero.")

    if expected_yield_per_acre <= 0:
        raise ValueError("Expected yield must be greater than zero.")

    if selling_price_per_unit <= 0:
        raise ValueError("Selling price must be greater than zero.")

    if total_cost_per_acre < 0:
        raise ValueError("Cost cannot be negative.")

    total_yield = expected_yield_per_acre * acres
    revenue = total_yield * selling_price_per_unit
    total_cost = total_cost_per_acre * acres
    net_profit = revenue - total_cost

    break_even_yield = total_cost / selling_price_per_unit

    return ProfitEstimate(
        crop=crop.title(),
        acres=acres,
        expected_revenue_pkr=round(revenue, 2),
        total_cost_pkr=round(total_cost, 2),
        net_profit_pkr=round(net_profit, 2),
        break_even_yield=round(break_even_yield, 2),
    )

#==================================
#profit estimator
#==================================
@function_tool
def profit_estimator(
    crop: str,
    acres: float,
    expected_yield_per_acre: float,
    selling_price_per_unit: float,
    total_cost_per_acre: float,
) -> ProfitEstimate:
    """
    Estimate revenue, total cost, net profit and break-even yield.
    """
    return _profit_estimator(
        crop,
        acres,
        expected_yield_per_acre,
        selling_price_per_unit,
        total_cost_per_acre,
    )


def _mandi_price_lookup(
    district: str,
    crop: str,
) -> dict:

    prices = {
        "multan": {
            "wheat": 3200,
            "chickpea": 7200,
            "cotton": 18000,
            "maize": 2800,
        },
        "faisalabad": {
            "wheat": 3250,
            "chickpea": 7300,
            "cotton": 17800,
            "maize": 2850,
        },
        "lahore": {
            "wheat": 3300,
            "chickpea": 7400,
            "cotton": 18200,
            "maize": 2900,
        },
    }

    district_key = district.lower().strip()
    crop_key = crop.lower().strip()

    district_prices = prices.get(district_key)

    if not district_prices:
        return {
            "district": district,
            "crop": crop,
            "price": None,
            "currency": "PKR",
            "message": "No modeled mandi price available.",
        }

    price = district_prices.get(crop_key)

    if price is None:
        return {
            "district": district,
            "crop": crop,
            "price": None,
            "currency": "PKR",
            "message": "No modeled price available for this crop.",
        }

    return {
        "district": district.title(),
        "crop": crop.title(),
        "price": price,
        "currency": "PKR",
        "price_basis": "Modeled wholesale mandi estimate",
    }

#==================================
#mandi price tool 
#==================================

@function_tool
def mandi_price_lookup(
    district: str,
    crop: str,
) -> dict:
    """
    Return a modeled wholesale mandi price for a crop.
    """
    return _mandi_price_lookup(district, crop)

#==================================
#pest disease doctor
#==================================
@function_tool
def pest_disease_doctor(
    crop: str,
    symptoms: str,
) -> dict:
    """
    Identify a likely crop pest or disease from farmer-described
    symptoms and provide a cautious treatment recommendation.

    Dosages are limited to predefined safe demo values.
    """

    crop_key = crop.lower().strip()
    symptoms_key = symptoms.lower().strip()

    # ---------------------------------------------------------
    # Cotton Whitefly
    # ---------------------------------------------------------

    if crop_key == "cotton" and (
        "white insect" in symptoms_key
        or "tiny white" in symptoms_key
        or "whitefly" in symptoms_key
        or "leaves curling" in symptoms_key
    ):
        return {
            "crop": "Cotton",
            "likely_problem": "Whitefly",
            "confidence": "High",
            "symptoms_match": [
                "tiny white insects",
                "leaf curling",
            ],
            "treatment": (
                "Monitor infestation and use only a locally registered "
                "whitefly-control product according to its label."
            ),
            "safe_demo_dosage": (
                "Use ONLY the pesticide label dosage. "
                "Do not exceed the label rate."
            ),
            "safety_warning": (
                "Wear appropriate protective equipment and follow "
                "the product label. Do not mix pesticides without "
                "professional guidance."
            ),
        }

    # ---------------------------------------------------------
    # Wheat Aphids
    # ---------------------------------------------------------

    if crop_key == "wheat" and (
        "aphid" in symptoms_key
        or "small green insects" in symptoms_key
        or "small insects" in symptoms_key
    ):
        return {
            "crop": "Wheat",
            "likely_problem": "Aphids",
            "confidence": "Medium",
            "symptoms_match": [
                "small insects",
                "possible aphid infestation",
            ],
            "treatment": (
                "Inspect several plants across the field before "
                "deciding on treatment. Follow a locally approved "
                "aphid-control product label if intervention is needed."
            ),
            "safe_demo_dosage": (
                "Use ONLY the pesticide label dosage."
            ),
            "safety_warning": (
                "Do not exceed the label rate. Use protective "
                "equipment and follow local agricultural guidance."
            ),
        }

    # ---------------------------------------------------------
    # Maize Fall Armyworm
    # ---------------------------------------------------------

    if crop_key == "maize" and (
        "armyworm" in symptoms_key
        or "holes in leaves" in symptoms_key
        or "leaf damage" in symptoms_key
    ):
        return {
            "crop": "Maize",
            "likely_problem": "Possible Fall Armyworm",
            "confidence": "Medium",
            "symptoms_match": [
                "holes in leaves",
                "leaf damage",
            ],
            "treatment": (
                "Inspect the whorl and affected plants carefully. "
                "Use only a locally registered treatment according "
                "to its label if intervention is necessary."
            ),
            "safe_demo_dosage": (
                "Use ONLY the pesticide label dosage."
            ),
            "safety_warning": (
                "Follow the product label and local agricultural "
                "extension guidance."
            ),
        }

    # ---------------------------------------------------------
    # Unknown
    # ---------------------------------------------------------

    return {
        "crop": crop,
        "likely_problem": "Unknown",
        "confidence": "Low",
        "symptoms_match": [],
        "treatment": (
            "The symptoms are not sufficient for a reliable diagnosis. "
            "Inspect the crop carefully or consult a local agriculture "
            "extension officer."
        ),
        "safe_demo_dosage": None,
        "safety_warning": (
            "Do not apply an unknown pesticide based only on these symptoms."
        ),
    }

#==================================
#weather irrigation advisor
#==================================
@function_tool
def weather_irrigation_advisor(
    district: str,
    crop: str,
    water_availability: str,
) -> dict:
    """
    Get current weather from Open-Meteo and provide
    a simple irrigation recommendation.
    """

    district_key = district.strip()
    crop_key = crop.lower().strip()
    water_key = water_availability.lower().strip()

    if not district_key:
        raise ValueError("District is required.")

    # ---------------------------------------------------------
    # Get coordinates from Open-Meteo Geocoding API
    # ---------------------------------------------------------

    geocode_url = (
        "https://geocoding-api.open-meteo.com/v1/search"
        f"?name={quote(district_key)}"
        "&count=1"
        "&language=en"
        "&format=json"
    )

    try:
        with urlopen(geocode_url, timeout=10) as response:
            geocode_data = json.loads(response.read().decode("utf-8"))
    except Exception as e:
        return {
            "status": "error",
            "message": f"Weather location lookup failed: {str(e)}",
        }

    results = geocode_data.get("results", [])

    if not results:
        return {
            "status": "error",
            "message": f"Could not find weather location for '{district}'.",
        }

    location = results[0]

    latitude = location["latitude"]
    longitude = location["longitude"]

    # ---------------------------------------------------------
    # Get current weather
    # ---------------------------------------------------------

    weather_url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}"
        f"&longitude={longitude}"
        "&current=temperature_2m,relative_humidity_2m,"
        "precipitation,weather_code"
        "&timezone=auto"
    )

    try:
        with urlopen(weather_url, timeout=10) as response:
            weather_data = json.loads(response.read().decode("utf-8"))
    except Exception as e:
        return {
            "status": "error",
            "message": f"Weather API request failed: {str(e)}",
        }

    current = weather_data.get("current", {})

    temperature = current.get("temperature_2m")
    humidity = current.get("relative_humidity_2m")
    precipitation = current.get("precipitation")

    # ---------------------------------------------------------
    # Irrigation logic
    # ---------------------------------------------------------

    if precipitation is not None and precipitation > 5:
        irrigation_needed = False

        recommendation = (
            "Recent precipitation is significant. "
            "Avoid unnecessary irrigation and check soil moisture first."
        )

        reason = "Rainfall is currently reducing irrigation demand."

    elif water_key in ["limited", "low"] and temperature >= 35:
        irrigation_needed = True

        recommendation = (
            "Water is limited and temperature is high. "
            "Prioritize irrigation during critical crop stages "
            "and avoid unnecessary watering."
        )

        reason = (
            "High temperature can increase crop water demand "
            "while water availability is limited."
        )

    elif temperature >= 35:
        irrigation_needed = True

        recommendation = (
            "Temperature is high. Check soil moisture and "
            "irrigate if the root zone is dry."
        )

        reason = "High temperature may increase crop water demand."

    else:
        irrigation_needed = "Check soil moisture"

        recommendation = (
            "Check soil moisture before irrigation. "
            "Avoid over-irrigation."
        )

        reason = "Current weather does not indicate an immediate need for heavy irrigation."

    # ---------------------------------------------------------
    # Final result
    # ---------------------------------------------------------

    return {
        "status": "success",
        "district": district.title(),
        "crop": crop.title(),
        "water_availability": water_availability,
        "weather": {
            "temperature_c": temperature,
            "humidity_percent": humidity,
            "precipitation_mm": precipitation,
        },
        "irrigation_needed": irrigation_needed,
        "recommendation": recommendation,
        "reason": reason,
        "source": "Open-Meteo",
    }


#==================================
# govt. support agent
#==================================
@function_tool
def govt_support_lookup(
    district: str,
    crop: str,
    season: str,
) -> dict:
    """
    Provide relevant government agriculture support
    categories for a farmer.
    """

    district = district.strip()
    crop = crop.strip().lower()
    season = season.strip().lower()

    if not district:
        return {
            "status": "error",
            "message": "District is required."
        }

    if not crop:
        return {
            "status": "error",
            "message": "Crop is required."
        }

    if not season:
        return {
            "status": "error",
            "message": "Season is required."
        }

    support = [
        {
            "category": "Subsidy Programs",
            "description": "Check current Punjab agriculture subsidy programs applicable to the crop and farmer."
        },
        {
            "category": "Seed Support",
            "description": "Check availability of approved or subsidized seed programs."
        },
        {
            "category": "Fertilizer Support",
            "description": "Check current fertilizer subsidy/support programs and eligibility."
        },
        {
            "category": "Water / Irrigation Support",
            "description": "Check government programs related to water conservation and irrigation equipment."
        },
        {
            "category": "Farmer Loans",
            "description": "Check current agricultural financing and farmer loan programs."
        }
    ]

    return {
        "status": "success",
        "district": district.title(),
        "crop": crop.title(),
        "season": season.title(),
        "available_support_categories": support,
        "note": (
            "Program availability, eligibility, deadlines and amounts "
            "must be verified from the relevant government department "
            "before applying."
        )
    }