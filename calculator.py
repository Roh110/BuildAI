# calculator.py
"""
Construction calculation engine
Handles workers, materials, cost, and timeline estimation
"""

def calculate_workers(area_sqyd, floors, duration_days):
    total_area = area_sqyd * floors
    base_workers = total_area / 50

    return {
        "masons": int(base_workers * 0.25),
        "helpers": int(base_workers * 0.40),
        "steel_workers": int(base_workers * 0.15),
        "carpenters": int(base_workers * 0.10),
        "supervisors": max(1, int(base_workers * 0.05))
    }


def calculate_materials(area_sqyd, floors):
    total_area = area_sqyd * floors

    return {
        "cement_bags": int(total_area * 0.4),
        "steel_tons": round(total_area * 0.004, 2),
        "sand_cft": int(total_area * 8),
        "aggregate_cft": int(total_area * 6),
        "water_liters": int(total_area * 120)
    }


def calculate_cost(area_sqyd, floors):
    total_area = area_sqyd * floors

    material_cost = total_area * 1800
    labour_cost = total_area * 900
    overhead_cost = total_area * 300
    contingency_cost = total_area * 200

    return {
        "material_cost": material_cost,
        "labour_cost": labour_cost,
        "overhead": overhead_cost,
        "contingency": contingency_cost,
        "total_cost": material_cost + labour_cost + overhead_cost + contingency_cost
    }


def calculate_timeline(duration_days):
    return {
        "days": duration_days,
        "weeks": round(duration_days / 7, 1),
        "months": round(duration_days / 30, 1)
    }
