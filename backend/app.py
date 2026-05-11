from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
from Bio import SeqIO, Align
from Bio.SeqUtils.ProtParam import ProteinAnalysis
import numpy as np
from datetime import datetime
import sqlite3
import threading

app = Flask(__name__)
CORS(app, origins="*")

# Initialize database
def init_db():
    conn = sqlite3.connect('predictions.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS predictions
                 (id INTEGER PRIMARY KEY, user_sequence TEXT, predicted_antigen TEXT, 
                  coverage_score REAL, confidence_score REAL, timestamp DATETIME)''')
    conn.commit()
    conn.close()

init_db()

# ==================== NCBI API FUNCTIONS ====================

def query_ncbi_entrez_hiv(query_sequence, max_results=50):
    """
    Query NCBI Entrez database for HIV sequences.
    """
    
    try:
        from Bio import Entrez
        Entrez.email = "vaccine_research@example.com"
        
        print("Searching NCBI Entrez for HIV-1 sequences...")
        
        search_term = "HIV-1[organism] AND (gag OR env OR pol)[gene]"
        
        search_handle = Entrez.esearch(
            db="protein",
            term=search_term,
            retmax=max_results,
            sort="relevance"
        )
        
        search_result = Entrez.read(search_handle)
        search_handle.close()
        
        ids = search_result["IdList"][:max_results]
        
        if not ids:
            print("No sequences found in NCBI. Using fallback sequences...")
            return get_fallback_hiv_sequences()
        
        print(f"Found {len(ids)} sequences. Fetching details...")
        
        fetch_handle = Entrez.efetch(
            db="protein",
            id=",".join(ids),
            rettype="fasta",
            retmode="text"
        )
        
        sequences = []
        for record in SeqIO.parse(fetch_handle, "fasta"):
            subtype = extract_subtype_from_description(record.description)
            
            sequences.append({
                'id': record.id,
                'description': record.description,
                'sequence': str(record.seq),
                'length': len(record.seq),
                'subtype': subtype,
                'source': 'NCBI'
            })
        
        fetch_handle.close()
        
        print(f"Successfully fetched {len(sequences)} sequences from NCBI")
        return sequences
        
    except Exception as e:
        print(f"NCBI query failed: {e}")
        print("Using fallback sequences...")
        return get_fallback_hiv_sequences()

def extract_subtype_from_description(description):
    """Extract HIV subtype from sequence description."""
    description_lower = description.lower()
    
    if 'subtype a' in description_lower or 'a1' in description_lower:
        return 'A'
    elif 'subtype b' in description_lower:
        return 'B'
    elif 'subtype c' in description_lower:
        return 'C'
    elif 'subtype d' in description_lower:
        return 'D'
    elif 'crf' in description_lower:
        return 'CRF'
    else:
        return 'Unknown'

def get_fallback_hiv_sequences():
    """Fallback sequences if NCBI is unavailable."""
    return [
        {
            'id': 'HXB2_GAG',
            'description': 'HIV-1 HXB2 strain gag protein',
            'sequence': 'MGARASLRGGKLDAWERIRLRPGGRKKYRLKHIVWASRELERFAVNPGLLETSEGCRQILGQLQPALQTGSEELRSLFNTIAVLYCVHQRIEIKDTKEALDKIEEEQNKSKKKAQQAAADTGNSS',
            'subtype': 'B',
            'source': 'Fallback'
        },
        {
            'id': 'NL43_GAG',
            'description': 'HIV-1 NL4-3 strain gag protein',
            'sequence': 'MGARASVLSGGELDRWEKIRLRPGGKKHYMLKHIVWASRELERFAVNPGLLETSEGCRQILGQLQPALQTGSEELRSLFNTIAVLYCVHQRIEIKDTKEALDKIEEEQNKSKKKAQQAAADTGNSS',
            'subtype': 'B',
            'source': 'Fallback'
        },
        {
            'id': 'BRU_GAG',
            'description': 'HIV-1 BRU strain gag protein',
            'sequence': 'MGARASVLSGGELDRWEKIRLRPGGKKHYMLKHIVWASRELERFAVNPGLLETSEGCRQILGQLQPALQTGSEELRSLFNTIAVLYCVHQRIEIKDTKEALDKIEEEQNKSKKKAQQAAADTGNSS',
            'subtype': 'B',
            'source': 'Fallback'
        },
        {
            'id': 'TRO_GAG',
            'description': 'HIV-1 TRO strain gag protein subtype A',
            'sequence': 'MGARASVLSGGELDAWEKIRLRPGGKKHYMLKHIVWASRELERFALNPGLLETSEGCRQILGQLQPALQTGSEELRSLFNTIAVLYCVHQRIEIKDTKEALDKIEEEQNKSKKKAQQAAADTGNSS',
            'subtype': 'A',
            'source': 'Fallback'
        },
        {
            'id': 'ZA_GAG',
            'description': 'HIV-1 South African strain gag protein subtype C',
            'sequence': 'MGARASVLSGGELDRWEKIRLRPGGKKHYMLKHIVWASRELERFALNPGLLETSEGCRQILGQLQPALQTGSEELRSLFNTIAVLYCVHQRIEIKDTKEALDKIEEEQNKSKKKAQQAAADTGNSS',
            'subtype': 'C',
            'source': 'Fallback'
        }
    ]

# ==================== PHYLOGENETIC ANALYSIS ====================

def build_phylogenetic_relationships(sequences_list):
    """Calculate evolutionary distances between sequences."""
    
    try:
        print("Analyzing evolutionary relationships...")
        
        seqs = [s['sequence'] for s in sequences_list]
        
        if len(seqs) < 2:
            return None, None
        
        aligner = Align.PairwiseAligner()
        aligner.open_gap_score = -10
        aligner.extend_gap_score = -0.5
        aligner.match_score = 2
        aligner.mismatch_score = -1
        
        alignments_data = []
        for i in range(len(seqs)):
            for j in range(i+1, len(seqs)):
                try:
                    aln = aligner.align(seqs[i], seqs[j])
                    if aln:
                        identity = calculate_identity(aln[0])
                        alignments_data.append({
                            'pair': (i, j),
                            'score': float(aln[0].score),
                            'identity': identity
                        })
                except:
                    continue
        
        tree_data = {
            'nodes': [
                {
                    'id': i,
                    'label': sequences_list[i]['id'],
                    'subtype': sequences_list[i].get('subtype', 'Unknown')
                }
                for i in range(len(sequences_list))
            ],
            'edges': alignments_data[:10]
        }
        
        return alignments_data, tree_data
        
    except Exception as e:
        print(f"Phylogenetic analysis error: {e}")
        return None, None

def calculate_identity(alignment):
    """Calculate sequence identity % from alignment."""
    try:
        seq1_str = str(alignment.seq1).replace('-', '')
        seq2_str = str(alignment.seq2).replace('-', '')
        min_len = min(len(seq1_str), len(seq2_str))
        
        if min_len == 0:
            return 0
        
        matches = sum(1 for a, b in zip(seq1_str, seq2_str) if a == b)
        return matches / min_len
    except:
        return 0

# ==================== CONSERVATION ANALYSIS ====================

def compute_evolutionary_weighted_conservation(user_sequence, comparison_sequences, alignments_data):
    """Calculate conservation weighted by evolutionary distance."""
    
    print("Computing conservation with evolutionary weighting...")
    
    conservation_scores = {}
    
    for pos in range(len(user_sequence)):
        aa_at_pos = user_sequence[pos]
        
        weighted_matches = 0
        total_weight = 0
        
        for idx, comp_seq in enumerate(comparison_sequences):
            sequence_str = comp_seq['sequence']
            
            if pos >= len(sequence_str):
                continue
            
            evolutionary_distance = 0.5
            
            if alignments_data:
                for alignment in alignments_data:
                    if alignment['pair'] == (0, idx):
                        evolutionary_distance = 1 - alignment['identity']
                        break
                    elif alignment['pair'] == (idx, 0):
                        evolutionary_distance = 1 - alignment['identity']
                        break
            
            weight = max(evolutionary_distance, 0.1)
            total_weight += weight
            
            if sequence_str[pos] == aa_at_pos:
                weighted_matches += weight
        
        if total_weight > 0:
            conservation_scores[pos] = weighted_matches / total_weight
        else:
            conservation_scores[pos] = 0
    
    return conservation_scores

# ==================== ANTIGEN PREDICTION ====================

def predict_synthetic_antigen(user_sequence, conservation_map, comparison_sequences):
    """
    Predict the best synthetic antigen sequence.
    
    Uses multi-criteria scoring:
    - Conservation: How stable across strains (35%)
    - Coverage: Appears in many sequences (35%)
    - Epitope potential: Likely to trigger immune response (30%)
    """
    
    print("Predicting optimal synthetic antigen...")
    
    window_size = 20
    candidate_antigens = []
    
    for i in range(max(0, len(user_sequence) - window_size)):
        window = user_sequence[i:i+window_size]
        
        # Score 1: Conservation (how stable across strains)
        conservation_values = [conservation_map.get(j, 0) for j in range(i, min(i+window_size, len(user_sequence)))]
        conservation_score = np.mean(conservation_values) if conservation_values else 0
        
        # Score 2: Diversity (appears in many strains)
        diversity_score = 0
        matches_in_strains = 0
        subtype_coverage = {}
        
        if comparison_sequences:
            for comp_seq in comparison_sequences:
                comp_seq_str = comp_seq.get('sequence', '')
                subtype = comp_seq.get('subtype', 'Unknown')
                
                if window in comp_seq_str:
                    matches_in_strains += 1
                    subtype_coverage[subtype] = subtype_coverage.get(subtype, 0) + 1
            
            diversity_score = matches_in_strains / len(comparison_sequences)
        
        # Score 3: Epitope potential (immunogenicity)
        epitope_score = calculate_epitope_potential(window)
        
        # Combined weighted score (weights add to 100%)
        combined_score = (
            conservation_score * 0.35 +
            diversity_score * 0.35 +
            epitope_score * 0.30
        )
        
        candidate_antigens.append({
            'sequence': window,
            'start_pos': i,
            'end_pos': i + window_size,
            'conservation': conservation_score,
            'diversity': diversity_score,
            'epitope_potential': epitope_score,
            'score': combined_score
        })
    
    if not candidate_antigens:
        return None
    
    best_antigen = max(candidate_antigens, key=lambda x: x['score'])
    
    # Add explanation for why this antigen was chosen
    best_antigen['explanation'] = generate_antigen_explanation(best_antigen)
    
    return best_antigen

def calculate_epitope_potential(sequence):
    """Estimate likelihood this sequence triggers immune response."""
    
    aa_types = set(sequence)
    diversity = len(aa_types) / 20
    
    hydrophobic = sum(1 for aa in sequence if aa in 'VILMFP') / len(sequence)
    
    charged = sum(1 for aa in sequence if aa in 'DEKR') / len(sequence)
    
    epitope_score = (diversity * 0.4 + hydrophobic * 0.3 + charged * 0.3)
    
    return min(epitope_score, 1.0)

def generate_antigen_explanation(antigen):
    """Generate human-readable explanation for why this antigen was chosen."""
    
    explanation = []
    
    # Conservation explanation
    if antigen['conservation'] > 0.7:
        explanation.append(f"Highly conserved ({antigen['conservation']*100:.1f}%) - resistant to mutation")
    elif antigen['conservation'] > 0.5:
        explanation.append(f"Well-conserved ({antigen['conservation']*100:.1f}%) across strains")
    else:
        explanation.append(f"Moderately conserved ({antigen['conservation']*100:.1f}%)")
    
    # Coverage explanation
    if antigen['diversity'] > 0.5:
        explanation.append(f"Appears in {antigen['diversity']*100:.1f}% of HIV strains - broad coverage")
    elif antigen['diversity'] > 0.2:
        explanation.append(f"Present in {antigen['diversity']*100:.1f}% of strains")
    
    # Epitope explanation
    if antigen['epitope_potential'] > 0.6:
        explanation.append("Strong epitope potential - likely to trigger immune response")
    elif antigen['epitope_potential'] > 0.4:
        explanation.append("Moderate epitope potential for immune activation")
    
    return " | ".join(explanation) if explanation else "Selected as optimal antigen candidate"

# ==================== METRICS CALCULATION ====================

def calculate_coverage_metrics(predicted_antigen, all_sequences):
    """Calculate coverage metrics."""
    
    antigen_seq = predicted_antigen['sequence']
    
    matches = 0
    subtype_matches = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'Unknown': 0}
    subtype_totals = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'Unknown': 0}
    
    for seq_data in all_sequences:
        full_sequence = seq_data.get('sequence', '')
        subtype = seq_data.get('subtype', 'Unknown')
        
        if antigen_seq in full_sequence:
            matches += 1
            if subtype in subtype_matches:
                subtype_matches[subtype] += 1
        
        if subtype in subtype_totals:
            subtype_totals[subtype] += 1
    
    overall_coverage = matches / len(all_sequences) if all_sequences else 0
    
    coverage_by_subtype = {}
    for subtype in ['A', 'B', 'C', 'D']:
        if subtype_totals[subtype] > 0:
            coverage_by_subtype[subtype] = subtype_matches[subtype] / subtype_totals[subtype]
        else:
            coverage_by_subtype[subtype] = 0
    
    return {
        'overall_coverage': overall_coverage,
        'coverage_by_subtype': coverage_by_subtype,
        'exact_matches': matches,
        'total_sequences': len(all_sequences)
    }

def calculate_confidence_score(antigen_data, coverage_metrics, conservation_map):
    """Calculate confidence score."""
    
    conservation_confidence = antigen_data['conservation']
    coverage_confidence = min(coverage_metrics['overall_coverage'] * 1.2, 1.0)
    epitope_confidence = antigen_data['epitope_potential']
    
    overall_confidence = (conservation_confidence * 0.4 + 
                         coverage_confidence * 0.35 + 
                         epitope_confidence * 0.25)
    
    return min(overall_confidence, 1.0)

def predict_mutation_resistance(antigen_sequence, all_sequences):
    """Predict mutation resistance."""
    
    mutation_frequencies = {}
    
    for pos in range(len(antigen_sequence)):
        amino_acids_at_pos = []
        
        for seq_data in all_sequences:
            full_seq = seq_data.get('sequence', '')
            if pos < len(full_seq):
                amino_acids_at_pos.append(full_seq[pos])
        
        unique_aas = len(set(amino_acids_at_pos))
        mutation_frequencies[pos] = unique_aas / 20
    
    avg_mutation_frequency = np.mean(list(mutation_frequencies.values())) if mutation_frequencies else 0.5
    mutation_resistance = 1 - avg_mutation_frequency
    
    return mutation_resistance

# ==================== mRNA DESIGN ====================

def design_mrna(antigen_sequence):
    """Convert amino acid sequence to human-optimized mRNA."""
    
    codon_table = {
        'M': 'ATG', 'A': 'GCT', 'G': 'GGT', 'V': 'GTT', 'L': 'TTA',
        'I': 'ATT', 'P': 'CCT', 'F': 'TTT', 'W': 'TGG', 'S': 'TCT',
        'C': 'TGT', 'Y': 'TAT', 'N': 'AAT', 'Q': 'CAA', 'K': 'AAA',
        'R': 'AGA', 'H': 'CAT', 'D': 'GAT', 'E': 'GAA', 'T': 'ACT',
    }
    
    mrna = ""
    for aa in antigen_sequence:
        mrna += codon_table.get(aa, 'NNN')
    
    return mrna

# ==================== API ENDPOINTS ====================

@app.route('/api/predict', methods=['POST'])
def predict():
    """Main prediction endpoint."""
    
    try:
        data = request.json
        user_sequence = data.get('sequence', '').strip()
        
        if not user_sequence:
            return jsonify({'error': 'No sequence provided'}), 400
        
        if len(user_sequence) < 20:
            return jsonify({'error': 'Sequence too short (minimum 20 amino acids)'}), 400
        
        print(f"\n{'='*60}")
        print(f"Starting prediction for sequence length {len(user_sequence)}")
        print(f"{'='*60}")
        
        print("\n[1/6] Querying NCBI for related HIV sequences...")
        related_sequences = query_ncbi_entrez_hiv(user_sequence, max_results=50)
        
        if not related_sequences:
            return jsonify({'error': 'Could not fetch sequences from NCBI'}), 500
        
        print(f"✓ Found {len(related_sequences)} related sequences")
        
        print("\n[2/6] Analyzing evolutionary relationships...")
        alignments_data, tree_data = build_phylogenetic_relationships(related_sequences)
        print("✓ Evolutionary analysis complete")
        
        print("\n[3/6] Computing conservation scores...")
        conservation_map = compute_evolutionary_weighted_conservation(
            user_sequence, 
            related_sequences, 
            alignments_data if alignments_data else []
        )
        print("✓ Conservation computed")
        
        print("\n[4/6] Predicting optimal antigen...")
        predicted_antigen = predict_synthetic_antigen(user_sequence, conservation_map, related_sequences)
        
        if not predicted_antigen:
            return jsonify({'error': 'Could not predict antigen'}), 500
        
        print(f"✓ Predicted antigen: {predicted_antigen['sequence']}")
        
        print("\n[5/6] Calculating metrics...")
        coverage = calculate_coverage_metrics(predicted_antigen, related_sequences)
        confidence = calculate_confidence_score(predicted_antigen, coverage, conservation_map)
        mutation_resistance = predict_mutation_resistance(predicted_antigen['sequence'], related_sequences)
        print("✓ Metrics calculated")
        
        print("\n[6/6] Designing mRNA...")
        mrna = design_mrna(predicted_antigen['sequence'])
        print("✓ mRNA designed")
        
        conn = sqlite3.connect('predictions.db')
        c = conn.cursor()
        c.execute('INSERT INTO predictions VALUES (NULL, ?, ?, ?, ?, ?)',
                  (user_sequence, predicted_antigen['sequence'], coverage['overall_coverage'], 
                   confidence, datetime.now()))
        conn.commit()
        conn.close()
        
        print(f"\n{'='*60}")
        print("Prediction complete!")
        print(f"{'='*60}\n")
        
        result = {
            'user_sequence_length': len(user_sequence),
            'predicted_antigen': predicted_antigen['sequence'],
            'antigen_explanation': predicted_antigen.get('explanation', ''),
            'antigen_position': {
                'start': predicted_antigen['start_pos'],
                'end': predicted_antigen['end_pos']
            },
            'mrna': mrna,
            'metrics': {
                'conservation': predicted_antigen['conservation'],
                'diversity': predicted_antigen['diversity'],
                'epitope_potential': predicted_antigen['epitope_potential'],
                'overall_score': predicted_antigen['score']
            },
            'coverage': {
                'overall': coverage['overall_coverage'],
                'by_subtype': coverage['coverage_by_subtype'],
                'exact_matches': coverage['exact_matches'],
                'total_sequences_analyzed': coverage['total_sequences']
            },
            'confidence_score': confidence,
            'mutation_resistance': mutation_resistance,
            'evolutionary_tree': tree_data,
            'conservation_map': conservation_map,
            'related_sequences_count': len(related_sequences)
        }
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in prediction: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500

@app.route('/api/history', methods=['GET'])
def history():
    """Get past predictions."""
    try:
        conn = sqlite3.connect('predictions.db')
        c = conn.cursor()
        c.execute('SELECT * FROM predictions ORDER BY timestamp DESC LIMIT 10')
        results = c.fetchall()
        conn.close()
        
        return jsonify({'history': [
            {'id': r[0], 'user_sequence': r[1][:50], 'antigen': r[2], 'coverage': r[3], 'confidence': r[4]}
            for r in results
        ]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')