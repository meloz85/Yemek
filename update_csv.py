#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to update yemeklistesivirgüllü.csv:
1. Populate allergen columns (GLUTEN, MILK, EGG, FISH) based on Turkish keywords
2. Improve translations in EN, DE, and RU columns
"""

import csv
import re

# Define allergen keywords (all lowercase for case-insensitive matching)
GLUTEN_KEYWORDS = [
    'ekmek', 'pide', 'börek', 'böreğ', 'makarna', 'spagetti', 'bulgur', 'un', 
    'şehriye', 'mantı', 'simit', 'galeta', 'pane', 'bisküvi', 'kraker', 
    'tarhana', 'yulaf', 'çavdar', 'erişte', 'lazanya', 'canneloni', 
    'ravioli', 'fusilli', 'farfalle', 'tagliatelle', 'şehriy', 'canaloni'
]

MILK_KEYWORDS = [
    'süt', 'yoğurt', 'peynir', 'peynır', 'kaşar', 'kasar', 'krema', 
    'tereyağ', 'muhallebi', 'cacık', 'ayran', 'beşamel', 'labne', 'lor', 
    'parmesan', 'mozarella', 'mascarpone', 'kremali', 'sütlü', 'graten', 
    'beğendi'
]

EGG_KEYWORDS = [
    'yumurta', 'omlet', 'menemen', 'mayonez'
]

FISH_KEYWORDS = [
    'balık', 'balik', 'somon', 'ton', 'levrek', 'çipura', 'cipura', 
    'kalamar', 'karides', 'karıdes', 'ahtapot', 'hamsi', 'palamut', 
    'uskumru', 'mezgit', 'sardalya', 'çinekop', 'cinekop', 'barbun', 
    'barb', 'kılıç', 'kiliç', 'kolyos', 'orkinos', 'lüfer', 'lufer', 
    'alabalık', 'alabalik', 'dil balığı', 'sübye', 'subye', 'yengeç', 
    'yengec', 'paella', 'deniz mahsülleri', 'denizmahsülleri', 
    'deniz ürünleri', 'çupra', 'çipura', 'cipura', 'istavrit', 'istravit'
]

def normalize_turkish(text):
    """Normalize Turkish text for case-insensitive comparison"""
    if not text:
        return ''
    # Handle Turkish İ/i and I/ı characters
    text = text.replace('İ', 'i').replace('I', 'ı')
    text = text.lower()
    return text

def check_allergen(text, keywords):
    """Check if any keyword is present in the text (case-insensitive)"""
    if not text:
        return 0
    text_normalized = normalize_turkish(text)
    for keyword in keywords:
        keyword_normalized = normalize_turkish(keyword)
        # Use word boundary check for short keywords to avoid false positives
        if len(keyword_normalized) <= 2:
            # For very short keywords, require word boundaries
            pattern = r'\b' + re.escape(keyword_normalized) + r'\b'
            if re.search(pattern, text_normalized):
                return 1
        else:
            # For longer keywords, check if it's present
            if keyword_normalized in text_normalized:
                return 1
    return 0

def improve_english(text):
    """Improve English translations"""
    if not text:
        return text
    
    # Specific fixes for known issues
    text = text.replace('SAUTEED OF SHRIMP', 'Sauteed Shrimp')
    text = text.replace('ADANA STYLE KEBAP', 'Adana Style Kebab')
    text = text.replace('ADANA STIL KEBAP', 'Adana Style Kebab')
    
    # Fix "STIL" and "USULÜ" to "Style"
    text = re.sub(r'\b(STIL|Stil|USULÜ|USULU)\b', 'Style', text, flags=re.IGNORECASE)
    
    # Fix "KEBAP" to "Kebab"
    text = re.sub(r'\bKEBAP\b', 'Kebab', text, flags=re.IGNORECASE)
    
    return text

def improve_german(text):
    """Improve German translations"""
    if not text:
        return text
    
    # Fix "Stil" usage in German - remove it or fix compound words
    # Handle compound words first
    text = re.sub(r'STILSUPPE', 'SUPPE', text)
    text = re.sub(r'STILFILET', 'FILET', text)
    text = re.sub(r'STILFRIKADELLE', 'FRIKADELLE', text)
    
    # Then handle standalone "STIL"
    text = re.sub(r'\bSTIL\b', '', text)
    text = re.sub(r'\bStil\b', '', text)
    
    # Clean up extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def improve_russian(text):
    """Improve Russian translations"""
    if not text:
        return text
    
    # Basic cleanup - remove extra spaces
    result = re.sub(r'\s+', ' ', text)
    result = result.strip()
    
    return result

def process_csv(input_file, output_file):
    """Process the CSV file"""
    rows_processed = 0
    allergens_updated = 0
    translations_improved = 0
    
    with open(input_file, 'r', encoding='utf-8-sig', newline='') as infile:
        reader = csv.reader(infile)
        rows = list(reader)
    
    # Process rows
    output_rows = []
    for i, row in enumerate(rows):
        if i == 0:
            # Header line
            output_rows.append(row)
            continue
        
        if len(row) < 9:
            output_rows.append(row)
            continue
        
        try:
            # Extract fields
            id_num = row[0]
            tr = row[1]
            en = row[2]
            de = row[3]
            ru = row[4]
            gluten = row[5]
            milk = row[6]
            egg = row[7]
            fish = row[8]
            
            # Check allergens based on Turkish name
            new_gluten = str(check_allergen(tr, GLUTEN_KEYWORDS))
            new_milk = str(check_allergen(tr, MILK_KEYWORDS))
            new_egg = str(check_allergen(tr, EGG_KEYWORDS))
            new_fish = str(check_allergen(tr, FISH_KEYWORDS))
            
            if new_gluten != gluten or new_milk != milk or new_egg != egg or new_fish != fish:
                allergens_updated += 1
            
            # Improve translations
            new_en = improve_english(en)
            new_de = improve_german(de)
            new_ru = improve_russian(ru)
            
            if new_en != en or new_de != de or new_ru != ru:
                translations_improved += 1
            
            # Create new row
            new_row = [id_num, tr, new_en, new_de, new_ru, new_gluten, new_milk, new_egg, new_fish]
            output_rows.append(new_row)
            
            rows_processed += 1
            
        except Exception as e:
            print(f"Error processing row {i}: {e}")
            print(f"Row: {row}")
            output_rows.append(row)
    
    # Write output
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(output_rows)
    
    print(f"Processed {rows_processed} rows")
    print(f"Updated allergen data for {allergens_updated} items")
    print(f"Improved translations for {translations_improved} items")

if __name__ == '__main__':
    input_file = '/home/runner/work/Yemek/Yemek/yemeklistesivirgüllü.csv'
    output_file = '/home/runner/work/Yemek/Yemek/yemeklistesivirgüllü.csv'
    process_csv(input_file, output_file)
