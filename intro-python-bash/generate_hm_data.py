#!/usr/bin/env python3
"""
Synthetic H&M Retail Transactions Data Generator
Course: Big Data Technologies (Day 1 Lab)

Generates 3 relational CSV files (customers.csv, articles.csv, transactions_train.csv)
mimicking the H&M Personalized Fashion dataset schema.

The data is deterministically seeded by the student's student ID (--student_id).
Scale: ~50,000 customers, ~10,000 articles, ~17,000,000 transactions (~1.65 GB).
"""

import argparse
import gc
import hashlib
import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def parse_args():
    parser = argparse.ArgumentParser(description="Generate student-seeded H&M retail dataset.")
    parser.add_argument("--student_id", type=int, required=True, help="Student ID used as random seed")
    parser.add_argument("--output_dir", type=str, default=".", help="Directory to save CSV files (default: current directory)")
    parser.add_argument("--n_customers", type=int, default=50000, help="Number of customers (default: 50,000)")
    parser.add_argument("--n_articles", type=int, default=None, help="Number of articles (default: student-seeded ~10,000)")
    parser.add_argument("--n_transactions", type=int, default=None, help="Number of transactions (default: student-seeded ~17,000,000)")
    return parser.parse_args()

def generate_data(student_id: int, output_dir: str, n_customers: int = 50000, n_articles: int = None, n_transactions: int = None):
    if n_articles is None:
        n_articles = 10000 + int((student_id // 10) % 200)
    if n_transactions is None:
        n_transactions = 17000000 + int(student_id % 50000)

    os.makedirs(output_dir, exist_ok=True)
    rng = np.random.default_rng(student_id)
    rng_cust = np.random.default_rng(student_id)
    print(f"[*] Initializing H&M Data Generator with Seed: {student_id}")
    print("[*] Generating synthetic retail dataset...")

    # -------------------------------------------------------------
    # 1. Generate customers.csv
    # -------------------------------------------------------------
    print("[*] Generating customers.csv...")
    raw_seeds = rng_cust.integers(0, 2**63 - 1, size=n_customers, dtype=np.int64)
    customer_ids = [hashlib.sha256(f"{student_id}_{s}".encode()).hexdigest() for s in raw_seeds]
    customer_ids_np = np.array(customer_ids, dtype='U64')

    ages = rng_cust.normal(loc=36.0, scale=14.0, size=n_customers).astype(int)
    ages = np.clip(ages, 16, 85).astype(float)
    age_null_mask = rng_cust.random(size=n_customers) < 0.05
    ages[age_null_mask] = np.nan

    fn_vals = np.where(rng_cust.random(size=n_customers) < 0.35, 1.0, np.nan)
    active_vals = np.where(rng_cust.random(size=n_customers) < 0.30, 1.0, np.nan)

    cms_choices = ['ACTIVE', 'PRE-CREATE', None]
    cms_probs = [0.90, 0.09, 0.01]
    cms_vals = rng_cust.choice(cms_choices, p=cms_probs, size=n_customers)

    fnf_choices = ['NONE', 'Regularly', None]
    fnf_probs = [0.65, 0.34, 0.01]
    fnf_vals = rng_cust.choice(fnf_choices, p=fnf_probs, size=n_customers)

    customers_df = pd.DataFrame({
        'customer_id': customer_ids,
        'FN': fn_vals,
        'Active': active_vals,
        'club_member_status': cms_vals,
        'fashion_news_frequency': fnf_vals,
        'age': ages
    })

    customers_path = os.path.join(output_dir, "customers.csv")
    customers_df.to_csv(customers_path, index=False)
    print(f"    [+] Saved: {customers_path}")

    # -------------------------------------------------------------
    # 2. Generate articles.csv
    # -------------------------------------------------------------
    print("[*] Generating articles.csv...")
    product_codes = rng.integers(100000, 999999, size=n_articles)
    variant_ids = rng.integers(1, 99, size=n_articles)
    article_ids = [f"0{pc}{v:03d}"[:10] for pc, v in zip(product_codes, variant_ids)]
    article_ids_np = np.array(article_ids, dtype='U10')

    product_groups = [
        "Garment Upper body", "Garment Lower body", "Garment Full body",
        "Accessories", "Underwear", "Shoes", "Swimwear", "Bags"
    ]
    index_groups = ["Ladieswear", "Baby/Children", "Menswear", "Sport", "Divided"]
    sample_adjectives = ["Classic", "Slim", "Relaxed", "Vintage", "Oversized", "Cozy", "Ribbed", "Cotton"]
    sample_nouns = ["Tee", "Trousers", "Hoodie", "Dress", "Sweater", "Jacket", "Skirt", "Shorts"]

    prod_names = [
        f"{rng.choice(sample_adjectives)} {rng.choice(sample_nouns)}"
        for _ in range(n_articles)
    ]
    prod_groups = rng.choice(product_groups, size=n_articles)
    idx_groups = rng.choice(index_groups, size=n_articles)

    articles_df = pd.DataFrame({
        'article_id': article_ids,
        'product_code': product_codes,
        'prod_name': prod_names,
        'product_group_name': prod_groups,
        'index_group_name': idx_groups
    })

    articles_path = os.path.join(output_dir, "articles.csv")
    articles_df.to_csv(articles_path, index=False)
    print(f"    [+] Saved: {articles_path}")

    # -------------------------------------------------------------
    # 3. Generate transactions_train.csv (Vectorized Streaming)
    # -------------------------------------------------------------
    print("[*] Generating transactions_train.csv (Vectorized Streaming)...")
    pareto_weights = rng.pareto(a=1.3, size=n_customers) + 1e-5
    pareto_probs = pareto_weights / pareto_weights.sum()

    article_weights = rng.pareto(a=1.5, size=n_articles) + 1e-5
    article_probs = article_weights / article_weights.sum()

    start_date = datetime(2020, 1, 1)
    unique_dates = np.array([(start_date + timedelta(days=int(d))).strftime('%Y-%m-%d') for d in range(244)], dtype='U10')

    transactions_path = os.path.join(output_dir, "transactions_train.csv")
    chunk_size = 2000000
    n_chunks = (n_transactions + chunk_size - 1) // chunk_size

    first_chunk = True
    for chunk_idx in range(n_chunks):
        current_chunk_size = min(chunk_size, n_transactions - chunk_idx * chunk_size)
        
        cust_idx = rng.choice(n_customers, size=current_chunk_size, p=pareto_probs)
        art_idx = rng.choice(n_articles, size=current_chunk_size, p=article_probs)
        date_idx = rng.integers(0, 244, size=current_chunk_size)
        prices = np.round(rng.uniform(0.005, 0.150, size=current_chunk_size), 5)
        channels = rng.choice([1, 2], p=[0.35, 0.65], size=current_chunk_size)

        chunk_df = pd.DataFrame({
            't_dat': unique_dates[date_idx],
            'customer_id': customer_ids_np[cust_idx],
            'article_id': article_ids_np[art_idx],
            'price': prices,
            'sales_channel_id': channels
        })

        chunk_df.to_csv(transactions_path, mode='w' if first_chunk else 'a', index=False, header=first_chunk)
        first_chunk = False
        print(f"    [+] Processing chunk {chunk_idx + 1}/{n_chunks}...")
        del chunk_df, cust_idx, art_idx, date_idx, prices, channels
        gc.collect()

    print(f"    [+] Finished: {transactions_path}")
    print("[✓] Dataset generation complete! All files ready for analysis.\n")

if __name__ == "__main__":
    args = parse_args()
    generate_data(
        student_id=args.student_id,
        output_dir=args.output_dir,
        n_customers=args.n_customers,
        n_articles=args.n_articles,
        n_transactions=args.n_transactions
    )
