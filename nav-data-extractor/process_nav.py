"""
AMFI NAV Data Processor
Processes downloaded NAV data and converts to JSON format
"""

import json
import re
from datetime import datetime

def process_nav_file(input_file='results/nav_data.txt', output_file='results/nav_results.json'):
    """Process AMFI NAV data file and extract scheme names and NAV values"""
    
    schemes = []
    current_amc = ""
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"📖 Processing {len(lines)} lines...")
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip empty lines and headers
            if not line or line.startswith('Scheme Code'):
                continue
            
            # Parse AMC names (lines that don't start with numbers)
            if not re.match(r'^\d', line):
                current_amc = line
                continue
            
            # Parse scheme data (semicolon separated)
            parts = line.split(';')
            
            if len(parts) >= 6:  # Ensure we have enough columns
                scheme_code = parts[0].strip()
                isin_div_payout = parts[1].strip()
                isin_div_reinvest = parts[2].strip()
                scheme_name = parts[3].strip()
                nav = parts[4].strip()
                date = parts[5].strip()
                
                # Only include schemes with valid NAV values
                if nav and nav != '-' and nav.replace('.', '').isdigit():
                    try:
                        nav_float = float(nav)
                        schemes.append({
                            'scheme_code': scheme_code,
                            'scheme_name': scheme_name,
                            'nav': nav,
                            'nav_numeric': nav_float,
                            'nav_date': date,
                            'amc': current_amc,
                            'isin_div_payout': isin_div_payout,
                            'isin_div_reinvest': isin_div_reinvest
                        })
                    except ValueError:
                        print(f"⚠️  Invalid NAV value on line {line_num}: {nav}")
                        continue
        
        # Sort by NAV value (highest first)
        schemes.sort(key=lambda x: x['nav_numeric'], reverse=True)
        
        # Prepare final output
        output_data = {
            'extraction_date': datetime.now().isoformat(),
            'source_file': input_file,
            'total_schemes': len(schemes),
            'schemes': schemes
        }
        
        # Save to JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Successfully processed {len(schemes)} schemes")
        print(f"💾 Results saved to: {output_file}")
        
        # Display top 5 schemes by NAV
        print("\n📊 Top 5 Schemes by NAV Value:")
        print("-" * 60)
        for i, scheme in enumerate(schemes[:5], 1):
            print(f"{i}. {scheme['scheme_name'][:50]}... - ₹{scheme['nav']}")
        
        return output_data
        
    except FileNotFoundError:
        print(f"❌ Input file not found: {input_file}")
        return None
    except Exception as e:
        print(f"❌ Error processing file: {e}")
        return None

def main():
    print("🚀 Starting NAV data processing...")
    result = process_nav_file()
    
    if result:
        print(f"\n✅ Processing completed successfully!")
        print(f"📈 Total schemes: {result['total_schemes']}")
    else:
        print("❌ Processing failed!")

if __name__ == "__main__":
    main()