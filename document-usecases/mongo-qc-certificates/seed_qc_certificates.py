#!/usr/bin/env python3
"""
Seed script for Task 2: Semi-Structured Quality Inspection Certificates (EN 10204 3.1)
Generates 100,000 polymorphic quality inspection records into MongoDB.
"""

import sys
import os
import random
import time
from datetime import datetime, timedelta
import pymongo

def generate_qc_documents(student_nr: int, total_count: int = 100000):
    random.seed(student_nr)
    
    suppliers = ["STELLENBOSCH_FORGE_LTD", "BOLAND_ALLOYS_CORP", "OVERBERG_STEEL_WORKS", "CAPE_PRECISION_CASTINGS"]
    alloy_grades = ["316L_STAINLESS", "TI_6AL_4V_TITANIUM", "INCONEL_718", "AL_7075_T6"]
    
    # Active heat numbers per supplier (shared heats across 50-100 certificates)
    current_heats = {s: f"HEAT-{random.randint(10000, 99999)}" for s in suppliers}
    heat_counts = {s: 0 for s in suppliers}
    
    start_date = datetime(2026, 1, 1)
    batch_size = 5000
    batch = []
    
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    print(f"[*] Connecting to MongoDB ({mongo_uri})...")
    client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    db = client["quality_assurance"]
    col = db["qc_certificates"]
    
    col.drop()
    print(f"[*] Generating {total_count} EN 10204 3.1 certificates (seeded by {student_nr})...")
    degraded_supplier = suppliers[student_nr % len(suppliers)]
    
    for i in range(1, total_count + 1):
        supplier = random.choice(suppliers)
        grade = random.choice(alloy_grades)
        cert_date = start_date + timedelta(minutes=i * 5)
        
        # Rotate heat number every 75 certificates per supplier to simulate shared production batches
        heat_counts[supplier] += 1
        if heat_counts[supplier] > 75:
            current_heats[supplier] = f"HEAT-{random.randint(10000, 99999)}"
            heat_counts[supplier] = 1
        heat_num = current_heats[supplier]
        
        # Plant realistic metallurgical covariate shift:
        # Degraded supplier exhibits systematic quality degradation (sub-spec tensile and elevated defects)
        if supplier == degraded_supplier:
            tensile = round(random.gauss(585.0, 40.0), 2)
            yield_str = round(random.gauss(385.0, 25.0), 2)
            elongation = round(random.gauss(15.0, 3.0), 2)
            hardness = round(random.gauss(28.0, 4.0), 1)
            defect = 1 if random.random() < 0.048 else 0
        else:
            tensile = round(random.gauss(650.0, 35.0), 2)
            yield_str = round(random.gauss(420.0, 20.0), 2)
            elongation = round(random.gauss(18.5, 2.5), 2)
            hardness = round(random.gauss(32.0, 3.0), 1)
            defect = 1 if random.random() < 0.012 else 0
        
        # Base document
        doc = {
            "cert_id": f"QC-2026-{i:07d}",
            "supplier": supplier,
            "alloy_grade": grade,
            "certified_at": cert_date,
            "heat_number": heat_num,
            "standard": "EN 10204 3.1",
            "mechanical_properties": {
                "tensile_strength_mpa": tensile,
                "yield_strength_mpa": yield_str,
                "elongation_pct": elongation,
                "hardness_rockwell_c": hardness
            },
            "inspection_metrics": {
                "tolerance_dev": round(random.gauss(0.002, 0.008), 4),
                "surface_roughness_ra": round(random.uniform(0.4, 1.6), 3),
                "defect_flag": defect
            }
        }
        
        # Polymorphic schema variations (BOM composition only present on certain alloy tests)
        if i % 3 == 0:
            doc["chemical_composition"] = {
                "carbon_pct": round(random.uniform(0.02, 0.08), 3),
                "chromium_pct": round(random.uniform(16.0, 18.5), 2),
                "nickel_pct": round(random.uniform(10.0, 14.0), 2),
                "molybdenum_pct": round(random.uniform(2.0, 3.0), 2)
            }
            
        batch.append(doc)
        if len(batch) >= batch_size:
            col.insert_many(batch)
            batch = []
            print(f"    - Ingested {i}/{total_count} documents...")
            
    if batch:
        col.insert_many(batch)
        
    total_inserted = col.count_documents({})
    print(f"[+] Successfully seeded {total_inserted} certificates into quality_assurance.qc_certificates.")

if __name__ == "__main__":
    if len(sys.argv) < 2 or not sys.argv[1].isdigit():
        sys.exit("Usage: python3 document-usecases/mongo-qc-certificates/seed_qc_certificates.py <YOUR_STUDENT_NUMBER>")
    student_nr = int(sys.argv[1])
    generate_qc_documents(student_nr)
