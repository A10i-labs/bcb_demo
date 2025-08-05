#!/usr/bin/env python3
"""
phylogenetic_utils.py

Phylogenetic analysis utilities for protein sequences.
This module contains the PhylogeneticAnalyzer class and helper functions.

Usage:
    from phylogenetic_utils import PhylogeneticAnalyzer, run_quick_analysis
    
    # Quick analysis
    analyzer, results = run_quick_analysis('../dataset/Sample 5 Proteins.fasta')
    
    # Custom analysis
    analyzer = PhylogeneticAnalyzer('your_fasta_file.fasta')
    analyzer.run_complete_analysis()
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from Bio import SeqIO, Phylo
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor
from Bio.Align import MultipleSeqAlignment, PairwiseAligner
import networkx as nx
from scipy.cluster.hierarchy import linkage, dendrogram, to_tree
from scipy.spatial.distance import squareform, pdist
from collections import defaultdict
import re
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set up plotting style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class PhylogeneticAnalyzer:
    """Phylogenetic analysis class for protein sequences."""
    
    def __init__(self, fasta_file_path, metadata_file_path=None):
        """Initialize with FASTA file."""
        self.fasta_file = fasta_file_path
        self.metadata_file = metadata_file_path
        self.sequences = []
        self.seq_names = []
        self.distance_matrix = None
        self.tree = None
        self.load_sequences()
    
    def load_sequences(self):
        """Load sequences from FASTA file."""
        print("Loading sequences...")
        
        for seq_record in SeqIO.parse(self.fasta_file, "fasta"):
            self.sequences.append(str(seq_record.seq))
            self.seq_names.append(seq_record.id)
        
        print(f"Loaded {len(self.sequences)} sequences")
        for i, name in enumerate(self.seq_names):
            print(f"  {i+1}. {name} ({len(self.sequences[i])} aa)")
    
    def calculate_pairwise_distances(self, method='kmer'):
        """Calculate pairwise distances between sequences."""
        print(f"\nCalculating pairwise distances using {method} method...")
        
        n_seqs = len(self.sequences)
        distance_matrix = np.zeros((n_seqs, n_seqs))
        
        if method == 'kmer':
            # K-mer based distance
            k = 3
            for i in range(n_seqs):
                for j in range(i, n_seqs):
                    if i == j:
                        distance_matrix[i][j] = 0
                    else:
                        dist = self._kmer_distance(self.sequences[i], self.sequences[j], k)
                        distance_matrix[i][j] = dist
                        distance_matrix[j][i] = dist
        
        elif method == 'alignment':
            # Pairwise alignment based distance
            aligner = PairwiseAligner()
            aligner.match_score = 2
            aligner.mismatch_score = -1
            aligner.open_gap_score = -2
            aligner.extend_gap_score = -0.5
            
            for i in range(n_seqs):
                for j in range(i, n_seqs):
                    if i == j:
                        distance_matrix[i][j] = 0
                    else:
                        alignment = aligner.align(self.sequences[i], self.sequences[j])
                        score = alignment.score
                        max_len = max(len(self.sequences[i]), len(self.sequences[j]))
                        # Convert score to distance (0 = identical, 1 = completely different)
                        dist = 1 - (score / (max_len * aligner.match_score))
                        dist = max(0, min(1, dist))  # Clamp between 0 and 1
                        distance_matrix[i][j] = dist
                        distance_matrix[j][i] = dist
        
        elif method == 'hamming':
            # Simple character-based distance
            for i in range(n_seqs):
                for j in range(i, n_seqs):
                    if i == j:
                        distance_matrix[i][j] = 0
                    else:
                        dist = self._hamming_distance(self.sequences[i], self.sequences[j])
                        distance_matrix[i][j] = dist
                        distance_matrix[j][i] = dist
        
        self.distance_matrix = distance_matrix
        
        # Create DataFrame for easy viewing
        self.distance_df = pd.DataFrame(
            distance_matrix, 
            index=self.seq_names, 
            columns=self.seq_names
        )
        
        print("Distance Matrix:")
        print(self.distance_df.round(3))
        
        return self.distance_df
    
    def _kmer_distance(self, seq1, seq2, k):
        """Calculate k-mer based distance."""
        def get_kmer_counts(seq, k):
            kmers = defaultdict(int)
            for i in range(len(seq) - k + 1):
                kmer = seq[i:i+k]
                kmers[kmer] += 1
            return kmers
        
        kmers1 = get_kmer_counts(seq1, k)
        kmers2 = get_kmer_counts(seq2, k)
        
        all_kmers = set(list(kmers1.keys()) + list(kmers2.keys()))
        
        # Calculate cosine distance
        dot_product = 0
        norm1 = 0
        norm2 = 0
        
        for kmer in all_kmers:
            count1 = kmers1[kmer]
            count2 = kmers2[kmer]
            dot_product += count1 * count2
            norm1 += count1 * count1
            norm2 += count2 * count2
        
        if norm1 == 0 or norm2 == 0:
            return 1.0
        
        cosine_similarity = dot_product / (np.sqrt(norm1) * np.sqrt(norm2))
        return 1 - cosine_similarity
    
    def _hamming_distance(self, seq1, seq2):
        """Calculate normalized Hamming distance."""
        max_len = max(len(seq1), len(seq2))
        min_len = min(len(seq1), len(seq2))
        
        # Count differences in overlapping region
        differences = sum(c1 != c2 for c1, c2 in zip(seq1, seq2))
        
        # Add length difference
        differences += abs(len(seq1) - len(seq2))
        
        return differences / max_len if max_len > 0 else 0
    
    def build_upgma_tree(self):
        """Build UPGMA tree using hierarchical clustering."""
        print("\nBuilding UPGMA tree...")
        
        if self.distance_matrix is None:
            self.calculate_pairwise_distances()
        
        # Convert to condensed distance matrix for scipy
        condensed_distances = squareform(self.distance_matrix)
        
        # Perform UPGMA clustering
        linkage_matrix = linkage(condensed_distances, method='average')
        
        # Create tree structure
        self.tree = to_tree(linkage_matrix, rd=False)
        
        print("UPGMA tree constructed successfully!")
        return self.tree
    
    def build_neighbor_joining_tree(self):
        """Build Neighbor-Joining tree using Biopython."""
        print("\nBuilding Neighbor-Joining tree...")
        
        if self.distance_matrix is None:
            self.calculate_pairwise_distances()
        
        # Create custom distance matrix in the correct format for Biopython
        from Bio.Phylo.TreeConstruction import _DistanceMatrix
        
        # Convert our distance matrix to Biopython lower triangular format
        names = self.seq_names
        matrix = []
        
        for i in range(len(names)):
            row = []
            for j in range(i):
                row.append(self.distance_matrix[i][j])
            matrix.append(row)
        
        # Create the distance matrix object
        try:
            dm = _DistanceMatrix(names, matrix)
        except ValueError:
            # If there's still an issue with the format, let's create it differently
            print("Trying alternative distance matrix format...")
            
            # Create a full symmetric matrix first
            n = len(names)
            full_matrix = [[0.0 for _ in range(n)] for _ in range(n)]
            
            for i in range(n):
                for j in range(n):
                    full_matrix[i][j] = self.distance_matrix[i][j]
            
            # Now create proper lower triangular matrix
            matrix = []
            for i in range(n):
                row = []
                for j in range(i):
                    row.append(full_matrix[i][j])
                matrix.append(row)
            
            dm = _DistanceMatrix(names, matrix)
        
        # Build NJ tree
        constructor = DistanceTreeConstructor()
        nj_tree = constructor.nj(dm)
        
        self.nj_tree = nj_tree
        print("Neighbor-Joining tree constructed successfully!")
        return nj_tree
    
    def plot_dendrogram(self, figsize=(12, 8)):
        """Plot hierarchical clustering dendrogram."""
        print("\nPlotting dendrogram...")
        
        if self.distance_matrix is None:
            self.calculate_pairwise_distances()
        
        plt.figure(figsize=figsize)
        
        # Convert to condensed distance matrix
        condensed_distances = squareform(self.distance_matrix)
        
        # Perform hierarchical clustering
        linkage_matrix = linkage(condensed_distances, method='average')
        
        # Create dendrogram
        dendrogram(
            linkage_matrix,
            labels=self.seq_names,
            leaf_rotation=45,
            leaf_font_size=10,
            color_threshold=0.3
        )
        
        plt.title('Hierarchical Clustering Dendrogram (UPGMA)', fontsize=14, fontweight='bold')
        plt.xlabel('Sequence ID', fontsize=12)
        plt.ylabel('Distance', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    def plot_distance_heatmap(self, figsize=(10, 8)):
        """Plot distance matrix as heatmap."""
        print("\nPlotting distance heatmap...")
        
        if self.distance_matrix is None:
            self.calculate_pairwise_distances()
        
        plt.figure(figsize=figsize)
        
        # Create heatmap
        mask = np.triu(np.ones_like(self.distance_matrix, dtype=bool), k=1)
        
        sns.heatmap(
            self.distance_df,
            annot=True,
            fmt='.3f',
            cmap='viridis_r',
            square=True,
            linewidths=0.5,
            cbar_kws={'label': 'Distance'},
            mask=mask
        )
        
        plt.title('Pairwise Distance Matrix', fontsize=14, fontweight='bold')
        plt.xlabel('Sequence ID', fontsize=12)
        plt.ylabel('Sequence ID', fontsize=12)
        plt.tight_layout()
        plt.show()
    
    def plot_network_tree(self, figsize=(12, 10)):
        """Plot tree as network using NetworkX."""
        print("\nPlotting network tree...")
        
        if self.distance_matrix is None:
            self.calculate_pairwise_distances()
        
        # Create minimum spanning tree
        G = nx.Graph()
        
        # Add nodes
        for name in self.seq_names:
            G.add_node(name)
        
        # Add edges with weights (distances)
        for i in range(len(self.seq_names)):
            for j in range(i+1, len(self.seq_names)):
                weight = self.distance_matrix[i][j]
                G.add_edge(self.seq_names[i], self.seq_names[j], weight=weight)
        
        # Create minimum spanning tree
        mst = nx.minimum_spanning_tree(G)
        
        plt.figure(figsize=figsize)
        
        # Use spring layout for better visualization
        pos = nx.spring_layout(mst, k=3, iterations=50)
        
        # Draw nodes
        nx.draw_networkx_nodes(mst, pos, node_color='lightblue', 
                              node_size=2000, alpha=0.8)
        
        # Draw edges with varying thickness based on distance
        edges = mst.edges()
        weights = [mst[u][v]['weight'] for u, v in edges]
        max_weight = max(weights) if weights else 1
        edge_widths = [5 * (1 - w/max_weight) + 0.5 for w in weights]
        
        nx.draw_networkx_edges(mst, pos, width=edge_widths, alpha=0.6, edge_color='gray')
        
        # Draw labels
        nx.draw_networkx_labels(mst, pos, font_size=10, font_weight='bold')
        
        # Add edge labels with distances
        edge_labels = {(u, v): f'{d["weight"]:.3f}' for u, v, d in mst.edges(data=True)}
        nx.draw_networkx_edge_labels(mst, pos, edge_labels, font_size=8)
        
        plt.title('Minimum Spanning Tree (Phylogenetic Network)', 
                 fontsize=14, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        plt.show()
        
        return mst
    
    def plot_biopython_tree(self):
        """Plot tree using Biopython's visualization."""
        if not hasattr(self, 'nj_tree'):
            self.build_neighbor_joining_tree()
        
        print("\nPlotting Biopython NJ tree...")
        
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        
        # Draw the tree
        Phylo.draw(self.nj_tree, axes=ax, do_show=False)
        ax.set_title('Neighbor-Joining Phylogenetic Tree', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.show()
    
    def compare_methods(self):
        """Compare different distance calculation methods."""
        print("\nComparing different distance methods...")
        
        methods = ['kmer', 'hamming']
        if len(self.sequences) <= 10:  # Only run alignment for small datasets
            methods.append('alignment')
        
        fig, axes = plt.subplots(1, len(methods), figsize=(6*len(methods), 5))
        if len(methods) == 1:
            axes = [axes]
        
        for i, method in enumerate(methods):
            print(f"\nCalculating distances using {method} method...")
            self.calculate_pairwise_distances(method=method)
            
            # Plot heatmap
            mask = np.triu(np.ones_like(self.distance_matrix, dtype=bool), k=1)
            sns.heatmap(
                self.distance_df,
                annot=True,
                fmt='.3f',
                cmap='viridis_r',
                square=True,
                ax=axes[i],
                mask=mask,
                cbar_kws={'label': 'Distance'}
            )
            axes[i].set_title(f'{method.capitalize()} Distance')
        
        plt.tight_layout()
        plt.show()
    
    def export_tree_newick(self, filename='phylogenetic_tree.nwk'):
        """Export tree in Newick format."""
        if not hasattr(self, 'nj_tree'):
            self.build_neighbor_joining_tree()
        
        Phylo.write(self.nj_tree, filename, 'newick')
        print(f"Tree exported to {filename}")
    
    def run_complete_analysis(self):
        """Run complete phylogenetic analysis."""
        print("=" * 60)
        print("COMPLETE PHYLOGENETIC ANALYSIS")
        print("=" * 60)
        
        # 1. Calculate distances and plot heatmap
        self.calculate_pairwise_distances(method='kmer')
        self.plot_distance_heatmap()
        
        # 2. Plot dendrogram
        self.plot_dendrogram()
        
        # 3. Plot network tree
        self.plot_network_tree()
        
        # 4. Build and plot NJ tree (with error handling)
        nj_success = True
        try:
            self.build_neighbor_joining_tree()
            self.plot_biopython_tree()
        except Exception as e:
            print(f"Neighbor-Joining tree construction failed: {e}")
            print("Continuing with other analyses...")
            nj_success = False
        
        # 5. Compare methods (if dataset is small enough)
        if len(self.sequences) <= 5:
            self.compare_methods()
        
        # 6. Export tree (only if NJ tree was successful)
        if nj_success and hasattr(self, 'nj_tree'):
            try:
                self.export_tree_newick()
            except Exception as e:
                print(f"Tree export failed: {e}")
        
        print("\n" + "=" * 60)
        print("ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"Number of sequences: {len(self.sequences)}")
        print(f"Average pairwise distance: {np.mean(self.distance_matrix[np.triu_indices_from(self.distance_matrix, k=1)]):.3f}")
        print(f"Most similar pair: {np.min(self.distance_matrix[np.triu_indices_from(self.distance_matrix, k=1)]):.3f}")
        print(f"Most distant pair: {np.max(self.distance_matrix[np.triu_indices_from(self.distance_matrix, k=1)]):.3f}")
        
        results = {
            'distance_matrix': self.distance_df,
            'upgma_tree': self.tree
        }
        
        if nj_success and hasattr(self, 'nj_tree'):
            results['nj_tree'] = self.nj_tree
        
        return results

# Convenience functions for quick analysis
def run_quick_analysis(fasta_file, metadata_file=None):
    """Run a quick phylogenetic analysis with default settings."""
    analyzer = PhylogeneticAnalyzer(fasta_file, metadata_file)
    results = analyzer.run_complete_analysis()
    return analyzer, results

def plot_just_dendrogram(fasta_file):
    """Just plot a dendrogram quickly."""
    analyzer = PhylogeneticAnalyzer(fasta_file)
    analyzer.calculate_pairwise_distances()
    analyzer.plot_dendrogram()
    return analyzer

def plot_just_heatmap(fasta_file):
    """Just plot a distance heatmap quickly."""
    analyzer = PhylogeneticAnalyzer(fasta_file)
    analyzer.calculate_pairwise_distances()
    analyzer.plot_distance_heatmap()
    return analyzer

def plot_just_network(fasta_file):
    """Just plot a network tree quickly."""
    analyzer = PhylogeneticAnalyzer(fasta_file)
    analyzer.calculate_pairwise_distances()
    analyzer.plot_network_tree()
    return analyzer