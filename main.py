import matplotlib.pyplot as plt
import streamlit as st
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.visualization import plot_histogram
from qiskit_aer import AerSimulator
from scipy import stats


# ----------------------------
# Function to create QRNG circuit
# ----------------------------
def create_qrng_circuit(num_qubits: int) -> QuantumCircuit:
    """
    Create a quantum circuit for random number generation.
    Uses Hadamard gates to create superposition, then measures.
    """
    qc = QuantumCircuit(num_qubits, num_qubits)
    
    # Apply Hadamard gate to all qubits (creates superposition)
    for qubit in range(num_qubits):
        qc.h(qubit)
    
    # Measure all qubits
    qc.measure(range(num_qubits), range(num_qubits))
    
    return qc


# ----------------------------
# Function to generate random numbers
# ----------------------------
def generate_random_numbers(num_qubits: int, num_samples: int) -> list:
    """
    Generate random numbers using quantum circuit.
    Returns a list of decimal numbers.
    """
    qc = create_qrng_circuit(num_qubits)
    
    # Use AerSimulator
    backend = AerSimulator()
    transpiled = transpile(qc, backend)
    job = backend.run(transpiled, shots=num_samples)
    result = job.result()
    counts = result.get_counts()
    
    # Convert binary strings to decimal numbers
    random_numbers = []
    for binary_string, count in counts.items():
        decimal_value = int(binary_string, 2)
        random_numbers.extend([decimal_value] * count)
    
    return random_numbers


# ----------------------------
# Statistical Analysis Functions
# ----------------------------
def calculate_statistics(data: list, num_qubits: int) -> dict:
    """Calculate statistical properties of the generated numbers."""
    max_value = 2**num_qubits - 1
    
    stats_dict = {
        'mean': np.mean(data),
        'theoretical_mean': max_value / 2,
        'std_dev': np.std(data),
        'min': np.min(data),
        'max': np.max(data),
        'unique_values': len(set(data)),
        'total_samples': len(data)
    }
    
    return stats_dict


def chi_square_test(data: list, num_qubits: int) -> tuple:
    """
    Perform chi-square test for uniformity.
    Returns (chi_square_statistic, p_value)
    """
    max_value = 2**num_qubits
    expected_freq = len(data) / max_value
    
    # Count occurrences of each value
    observed_freq = np.bincount(data, minlength=max_value)
    expected_freq_array = np.full(max_value, expected_freq)
    
    # Chi-square test
    chi_square_stat = np.sum((observed_freq - expected_freq_array)**2 / expected_freq_array)
    degrees_of_freedom = max_value - 1
    p_value = 1 - stats.chi2.cdf(chi_square_stat, degrees_of_freedom)
    
    return chi_square_stat, p_value


# ----------------------------
# Streamlit UI - COMPLETELY REDESIGNED
# ----------------------------
st.set_page_config(
    page_title="⚛️ QRNG Lab", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern styling
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: white;
        font-size: 3rem;
        margin: 0;
    }
    .main-header p {
        color: #e0e0e0;
        font-size: 1.2rem;
    }
    .stat-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .big-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #667eea;
        margin: 0;
    }
    .label-text {
        color: #6c757d;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="main-header">
        <h1>⚛️ Quantum Random Number Generator Lab</h1>
        <p>Harnessing Quantum Superposition for True Randomness</p>
    </div>
""", unsafe_allow_html=True)

# ----------------------------
# Main Control Panel (Top Section)
# ----------------------------
st.markdown("## 🎛️ Control Panel")

# Three columns for controls
ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 2, 1])

with ctrl_col1:
    st.markdown("<p style='font-size: 1.3rem; font-weight: bold;'>Qubit Configuration</p>", unsafe_allow_html=True)
    num_qubits = st.select_slider(
        "Select Number of Qubits",
        options=[2, 3, 4, 5, 6, 7, 8],
        value=4,
        help="More qubits = larger range of random numbers"
    )
    max_possible_value = 2**num_qubits - 1
    st.info(f"📊 **Output Range:** 0 to {max_possible_value} ({2**num_qubits} possible values)")

with ctrl_col2:
    st.markdown("<p style='font-size: 1.3rem; font-weight: bold;'>Sample Size</p>", unsafe_allow_html=True)
    num_samples = st.slider(
        "Choose Sample Size",
        min_value=500,
        max_value=5000,
        value=1000,
        step=50,
        help="Number of random numbers to generate"
    )
    st.info(f"🎲 **Generating:** {num_samples:,} random numbers")

with ctrl_col3:
    st.markdown("<p style='font-size: 1.3rem; font-weight: bold;'>Action</p>", unsafe_allow_html=True)
    st.write("")  # Spacing
    st.write("")  # Spacing
    generate_button = st.button("🚀 Generate", type="primary", use_container_width=True)
    
    if st.button("🔄 Reset", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

st.divider()

# ----------------------------
# Quantum Circuit Preview (Tabs)
# ----------------------------
tab1, tab2, tab3 = st.tabs(["📈 Results", "🔬 Circuit Design", "📚 Documentation"])

with tab2:
    st.markdown("### Quantum Circuit Architecture")
    circuit_preview = create_qrng_circuit(num_qubits)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        fig_circuit = circuit_preview.draw('mpl', fold=-1)
        st.pyplot(fig_circuit)
    with col2:
        st.markdown(f"""
        **Circuit Details:**
        - **Qubits:** {num_qubits}
        - **Gates:** {num_qubits} Hadamard
        - **Measurements:** {num_qubits}
        
        **Process:**
        1. Initialize qubits in |0⟩
        2. Apply H gate (superposition)
        3. Measure each qubit
        4. Convert binary → decimal
        """)

with tab3:
    st.markdown("""
    ### 🌟 About Quantum Random Number Generation
    
    **Quantum Advantage:**
    - Classical RNGs use algorithms (pseudo-random)
    - QRNGs use quantum measurement (truly random)
    - Based on fundamental quantum uncertainty
    
    **How This Works:**
    1. **Superposition:** Hadamard gates create equal probability states
    2. **Measurement:** Quantum state collapses to 0 or 1 randomly
    3. **Aggregation:** Multiple measurements create random bit strings
    4. **Conversion:** Binary strings become decimal numbers
    
    **Statistical Tests:**
    - **Chi-Square Test:** Validates uniform distribution
    - **P-value > 0.05:** Indicates true randomness
    """)

# ----------------------------
# Results Section (Tab 1)
# ----------------------------
with tab1:
    if generate_button:
        with st.spinner("⚛️ Quantum computation in progress..."):
            random_numbers = generate_random_numbers(num_qubits, num_samples)
            st.session_state['random_numbers'] = random_numbers
            st.session_state['num_qubits'] = num_qubits
            st.session_state['num_samples'] = num_samples

    if 'random_numbers' in st.session_state:
        random_numbers = st.session_state['random_numbers']
        num_qubits_used = st.session_state['num_qubits']
        num_samples_used = st.session_state['num_samples']
        
        st.success(f"✅ Successfully generated {len(random_numbers):,} quantum random numbers!")
        
        # ----------------------------
        # Key Metrics Dashboard
        # ----------------------------
        st.markdown("## 📊 Statistical Dashboard")
        
        stats_dict = calculate_statistics(random_numbers, num_qubits_used)
        chi_stat, p_value = chi_square_test(random_numbers, num_qubits_used)
        
        # 5 columns for key metrics
        m1, m2, m3, m4, m5 = st.columns(5)
        
        with m1:
            st.markdown(f"""
            <div class="stat-card">
                <p class="label-text">Mean Value</p>
                <p class="big-number">{stats_dict['mean']:.2f}</p>
                <small>Expected: {stats_dict['theoretical_mean']:.2f}</small>
            </div>
            """, unsafe_allow_html=True)
        
        with m2:
            st.markdown(f"""
            <div class="stat-card">
                <p class="label-text">Std Deviation</p>
                <p class="big-number">{stats_dict['std_dev']:.2f}</p>
                <small>Spread measure</small>
            </div>
            """, unsafe_allow_html=True)
        
        with m3:
            st.markdown(f"""
            <div class="stat-card">
                <p class="label-text">Range</p>
                <p class="big-number">{stats_dict['min']}-{stats_dict['max']}</p>
                <small>Min to Max</small>
            </div>
            """, unsafe_allow_html=True)
        
        with m4:
            st.markdown(f"""
            <div class="stat-card">
                <p class="label-text">Unique Values</p>
                <p class="big-number">{stats_dict['unique_values']}</p>
                <small>Of {2**num_qubits_used} possible</small>
            </div>
            """, unsafe_allow_html=True)
        
        with m5:
            uniformity_status = "✅ Uniform" if p_value > 0.05 else "⚠️ Non-uniform"
            color = "#667eea" if p_value > 0.05 else "#f39c12"
            st.markdown(f"""
            <div class="stat-card">
                <p class="label-text">Chi-Square Test</p>
                <p class="big-number" style="color: {color}; font-size: 1.5rem;">{uniformity_status}</p>
                <small>p-value: {p_value:.4f}</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # ----------------------------
        # Visualization Section
        # ----------------------------
        st.markdown("## 📈 Distribution Visualizations")
        
        viz_col1, viz_col2 = st.columns(2)
        
        with viz_col1:
            st.markdown("### Frequency Distribution")
            fig1, ax1 = plt.subplots(figsize=(10, 6))
            
            counts = np.bincount(random_numbers, minlength=2**num_qubits_used)
            x_values = range(2**num_qubits_used)
            
            ax1.bar(x_values, counts, color='#667eea', alpha=0.8, edgecolor='#764ba2', linewidth=1.5)
            ax1.axhline(y=num_samples_used/(2**num_qubits_used), color='#e74c3c', 
                       linestyle='--', label='Expected Uniform', linewidth=2.5)
            ax1.set_xlabel('Decimal Value', fontsize=13, fontweight='bold')
            ax1.set_ylabel('Frequency', fontsize=13, fontweight='bold')
            ax1.set_title('Distribution of Generated Numbers', fontsize=15, fontweight='bold', pad=20)
            ax1.legend(fontsize=11)
            ax1.grid(True, alpha=0.3, linestyle='--')
            ax1.spines['top'].set_visible(False)
            ax1.spines['right'].set_visible(False)
            
            st.pyplot(fig1)
            
            # Additional stats below chart
            deviation = abs(stats_dict['mean'] - stats_dict['theoretical_mean'])
            st.metric("Mean Deviation from Expected", f"{deviation:.3f}", 
                     delta=f"{(deviation/stats_dict['theoretical_mean']*100):.2f}%",
                     delta_color="inverse")
        
        with viz_col2:
            st.markdown("### Cumulative Distribution Function")
            fig2, ax2 = plt.subplots(figsize=(10, 6))
            
            sorted_data = np.sort(random_numbers)
            cumulative = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
            
            ax2.plot(sorted_data, cumulative, linewidth=3, color='#27ae60', alpha=0.8)
            ax2.fill_between(sorted_data, cumulative, alpha=0.2, color='#27ae60')
            ax2.set_xlabel('Decimal Value', fontsize=13, fontweight='bold')
            ax2.set_ylabel('Cumulative Probability', fontsize=13, fontweight='bold')
            ax2.set_title('Cumulative Distribution', fontsize=15, fontweight='bold', pad=20)
            ax2.grid(True, alpha=0.3, linestyle='--')
            ax2.spines['top'].set_visible(False)
            ax2.spines['right'].set_visible(False)
            ax2.set_ylim([0, 1])
            
            st.pyplot(fig2)
            
            # Chi-square details
            st.metric("Chi-Square Statistic", f"{chi_stat:.4f}")
        
        st.divider()
        
        # ----------------------------
        # Data Export Section
        # ----------------------------
        st.markdown("## 💾 Export & Data Preview")
        
        export_col1, export_col2, export_col3 = st.columns([2, 2, 3])
        
        with export_col1:
            data_string = "\n".join(map(str, random_numbers))
            st.download_button(
                label="📄 Download TXT",
                data=data_string,
                file_name=f"qrng_{num_qubits_used}qubits_{num_samples_used}samples.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with export_col2:
            csv_data = "index,value\n" + "\n".join([f"{i},{val}" for i, val in enumerate(random_numbers)])
            st.download_button(
                label="📊 Download CSV",
                data=csv_data,
                file_name=f"qrng_{num_qubits_used}qubits_{num_samples_used}samples.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with export_col3:
            # Sample preview with selection
            preview_size = st.slider("Preview sample size:", 10, 200, 50, 10)
            with st.expander(f"🔍 Preview first {preview_size} values", expanded=False):
                preview_data = random_numbers[:preview_size]
                # Display as columns for better readability
                cols_per_row = 10
                for i in range(0, len(preview_data), cols_per_row):
                    st.text(" ".join(f"{val:3d}" for val in preview_data[i:i+cols_per_row]))
    
    else:
        # Empty state with call-to-action
        st.markdown("""
        <div style='text-align: center; padding: 4rem 2rem; background: #f8f9fa; border-radius: 10px;'>
            <h2>🚀 Ready to Generate Quantum Random Numbers?</h2>
            <p style='font-size: 1.2rem; color: #6c757d;'>
                Configure your parameters above and click the <strong>Generate</strong> button to start!
            </p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #6c757d; padding: 1rem;'>
    <small>⚛️ Powered by Qiskit & Quantum Mechanics | Built with Streamlit</small>
</div>
""", unsafe_allow_html=True)