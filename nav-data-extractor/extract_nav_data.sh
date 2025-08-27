#!/bin/bash

# AMFI NAV Data Extractor
# Extracts Scheme Names and NAV values from AMFI official data

set -e  # Exit on any error

echo "🚀 Starting AMFI NAV Data Extraction..."

# Create results directory
mkdir -p results

# Download NAV data
echo "📥 Downloading NAV data from AMFI..."
curl -s -o results/nav_data.txt "https://www.amfiindia.com/spages/NAVAll.txt"

if [ ! -f results/nav_data.txt ]; then
    echo "❌ Failed to download NAV data"
    exit 1
fi

echo "✅ Downloaded NAV data successfully"

# Check file size
file_size=$(wc -c < results/nav_data.txt)
echo "📊 File size: $file_size bytes"

if [ $file_size -eq 0 ]; then
    echo "❌ Downloaded file is empty"
    exit 1
fi

# Process the data using Python script
echo "🔄 Processing NAV data..."
python3 process_nav.py

echo "✅ NAV data extraction completed!"
echo "📄 Results saved to: results/nav_results.json"

# Display summary
if [ -f results/nav_results.json ]; then
    record_count=$(grep -c "scheme_name" results/nav_results.json)
    echo "📈 Total schemes processed: $record_count"
fi