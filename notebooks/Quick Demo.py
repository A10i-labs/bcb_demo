#!/usr/bin/env python3
"""
Quick Demo Script for NR Dataset Exploration
============================================

This script provides a quick overview of the sample protein dataset.
Run it from the notebooks directory to get immediate insights.

Usage:
    python quick_demo.py
"""

import pandas as pd
import numpy as np
from collections import Counter
import re
from pathlib import Path

def parse_fasta(file_path):
    """Parse a FASTA file and return sequence data."""
    sequences = []
    current_seq = {'header': '', 'sequence': ''}
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                if current_seq['header']:
                    sequences.append(current_seq.copy())
                current_seq = {'header': line[1:], 'sequence': ''}
            else:
                current_seq['sequence'] += line
        
        if current_seq['header']:
            sequences.append(current_seq)
    
    return sequences

def parse_header(header):
    """Parse FASTA header for key information."""
    match = re.match(r'^([^\s]+)\s+(.+?)\s+\[(.+?)\]$', header)
    if match:
        return {
            'accession': match.group(1),
            'protein_name': match.group(2),
            'organism': match.group(3)
        }
    return {'accession': header, 'protein_name': '', 'organism': ''}

def analyze_composition(sequence):
    """Analyze amino acid composition of a sequence."""
    amino_acids = 'ACDEFGHIKLMNPQRSTVWY'
    composition = Counter(sequence.upper())
    total = len(sequence)
    
    result = {}
    for aa in amino_acids:
        count = composition.get(aa, 0)
        result[aa] = {'count': count, 'percent': (count / total) * 100}
    
    return result

def main():
    """Main demo function."""
    print("=" * 60)
    print("🧬 NR Dataset Quick Demo")
    print("=" * 60)
    
    # Define file paths
    fasta_file = Path('../dataset/Sample 5 Proteins.fasta')
    metadata_file = Path('../dataset/Sample 5 Proteins Metadata.txt')
    
    # Check if files exist
    if not fasta_file.exists():
        print(f"❌ Error: {fasta_file} not found!")
        print("Please run this script from the notebooks/ directory.")
        return
    
    print(f"✅ Found FASTA file: {fasta_file}")
    print(f"✅ Found metadata file: {metadata_file.exists()}")
    
    # Parse FASTA file
    sequences = parse_fasta(fasta_file)
    
    print(f"\n📊 Dataset Overview:")
    print(f"   • Number of sequences: {len(sequences)}")
    
    # Analyze each sequence
    results = []
    for i, seq in enumerate(sequences):
        header_info = parse_header(seq['header'])
        composition = analyze_composition(seq['sequence'])
        
        results.append({
            'id': i + 1,
            'accession': header_info['accession'],
            'protein_name': header_info['protein_name'],
            'organism': header_info['organism'],
            'length': len(seq['sequence']),
            'unique_aa': len(set(seq['sequence'].upper())),
            'composition': composition
        })
    
    # Display results
    print(f"\n🔍 Sequence Details:")
    for result in results:
        print(f"   {result['id']}. {result['accession']}")
        print(f"      Name: {result['protein_name']}")
        print(f"      Organism: {result['organism']}")
        print(f"      Length: {result['length']} amino acids")
        print(f"      Unique amino acids: {result['unique_aa']}/20")
        print()
    
    # Summary statistics
    lengths = [r['length'] for r in results]
    unique_counts = [r['unique_aa'] for r in results]
    
    print(f"📈 Summary Statistics:")
    print(f"   • Length range: {min(lengths)} - {max(lengths)} amino acids")
    print(f"   • Average length: {np.mean(lengths):.1f} amino acids")
    print(f"   • Average unique amino acids: {np.mean(unique_counts):.1f}")
    
    # Organism distribution
    organisms = [r['organism'] for r in results]
    organism_counts = Counter(organisms)
    print(f"   • Organisms: {len(organism_counts)} unique")
    for org, count in organism_counts.items():
        print(f"     - {org}: {count} sequences")
    
    # Average amino acid composition
    print(f"\n🧪 Average Amino Acid Composition:")
    amino_acids = 'ACDEFGHIKLMNPQRSTVWY'
    avg_composition = {}
    
    for aa in amino_acids:
        percentages = [r['composition'][aa]['percent'] for r in results]
        avg_composition[aa] = np.mean(percentages)
    
    # Sort by percentage (descending)
    sorted_aa = sorted(avg_composition.items(), key=lambda x: x[1], reverse=True)
    
    print("   Top 10 most common amino acids:")
    for i, (aa, percent) in enumerate(sorted_aa[:10]):
        print(f"   {i+1:2d}. {aa}: {percent:5.1f}%")
    
    # Quality assessment
    print(f"\n✅ Quality Assessment:")
    all_perfect = True
    for result in results:
        seq = [seq['sequence'] for seq in sequences if parse_header(seq['header'])['accession'] == result['accession']][0]
        
        # Check for unusual amino acids
        standard_aa = set('ACDEFGHIKLMNPQRSTVWY')
        seq_aa = set(seq.upper())
        unusual_aa = seq_aa - standard_aa
        
        unknown_count = seq.upper().count('X')
        stop_count = seq.upper().count('*')
        
        if unusual_aa or unknown_count > 0 or stop_count > 0:
            all_perfect = False
            print(f"   ⚠️  {result['accession']}: Issues found")
            if unusual_aa:
                print(f"      - Unusual amino acids: {list(unusual_aa)}")
            if unknown_count > 0:
                print(f"      - Unknown amino acids (X): {unknown_count}")
            if stop_count > 0:
                print(f"      - Stop codons (*): {stop_count}")
    
    if all_perfect:
        print("   ✅ All sequences contain only standard amino acids")
        print("   ✅ No unknown amino acids (X) found")
        print("   ✅ No stop codons (*) found")
    
    print(f"\n🎯 Recommendations for Further Analysis:")
    print("   • Use the full Jupyter notebook for detailed visualizations")
    print("   • Apply this analysis to larger datasets (E. coli, viral proteins)")
    print("   • Implement sequence similarity analysis")
    print("   • Add phylogenetic analysis for multi-species data")
    print("   • Integrate with Boa query results for quality control")
    
    print(f"\n✨ Demo Complete!")
    print("   Run 'jupyter notebook ../jupyter_notebooks/NR_exploratory_demo.ipynb' for full analysis")
    print("=" * 60)

if __name__ == '__main__':
    main() 