#
# A Python-Based Venus Global Reference Atmospheric Model (Venus-GRAM) Toolkit
#
# This script provides a reference implementation based on the technical guide.
# It demonstrates the "High-Level Orchestration" strategy (Section 3.1) for
# running Venus-GRAM, parsing its output, and visualizing the results.
#
# Author: Gemini
# Date: 18 July 2025
#

import os
import subprocess
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import f90nml # pip install f90nml
import spiceypy # pip install spiceypy
from ctypes import CDLL, c_double, c_int, byref # For FFI demonstration

# --- Section 2: Environment Configuration ---
# NOTE: The user must configure these paths before running the script.

# Path to the compiled Venus-GRAM executable (Section 2.1)
# Example for Windows: 'C:/path/to/VenusGRAM/bin/VenusGRAM.exe'
# Example for Linux/macOS: '/path/to/VenusGRAM/bin/venusgram'
VENUS_GRAM_EXECUTABLE = './venusgram' # <-- MUST BE CONFIGURED BY USER

# Path to the directory containing NAIF SPICE kernels (Section 2.2)
SPICE_KERNEL_DIR = './spice_kernels/' # <-- MUST BE CONFIGURED BY USER

# Directory to store simulation inputs and outputs
OUTPUT_DIR = './venus_gram_runs/'

# --- Section 3.1: Strategy 1: High-Level Orchestration ---

def create_venus_gram_input(config: dict, input_path: str):
    """
    Generates a Fortran NAMELIST file (INPUT.nml) from a Python dictionary.
    As described in Section 3.1, using the f90nml library is the recommended approach.
    
    Args:
        config (dict): A dictionary representing the NAMELIST structure.
        input_path (str): The full path where the INPUT.nml file will be saved.
    """
    # The namelist group is typically named 'GRAM' in the GRAM Suite
    nml = {'GRAM': config}
    f90nml.write(nml, input_path)
    print(f"✅ Successfully created input file: {input_path}")

def run_venus_gram(executable_path: str, run_directory: str):
    """
    Executes the Venus-GRAM binary as an external process using subprocess.run().
    
    Args:
        executable_path (str): Path to the Venus-GRAM executable.
        run_directory (str): The directory where the simulation will be run.
                             This directory must contain the INPUT.nml file.
    """
    print(f"🚀 Executing Venus-GRAM...")
    try:
        # Use subprocess.run() as recommended in the technical guide
        result = subprocess.run(
            [executable_path],
            cwd=run_directory,      # Run the executable from this directory
            capture_output=True,
            text=True,
            check=True              # Raise an exception if the return code is non-zero
        )
        print("✅ Venus-GRAM execution completed successfully.")
        # print("   --- Venus-GRAM STDOUT ---")
        # print(result.stdout) # Uncomment for detailed debugging
    except FileNotFoundError:
        print(f"❌ ERROR: Executable not found at '{executable_path}'.")
        print("   Please check the VENUS_GRAM_EXECUTABLE path in this script.")
        raise
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: Venus-GRAM execution failed with return code {e.returncode}.")
        print("   --- Venus-GRAM STDERR ---")
        print(e.stderr)
        raise

def load_venus_gram_output(output_path: str) -> pd.DataFrame:
    """
    Parses the Venus-GRAM CSV output file into a pandas DataFrame.
    
    Args:
        output_path (str): The path to the OUTPUT.csv file.
    
    Returns:
        pd.DataFrame: A DataFrame containing the simulation results.
    """
    try:
        df = pd.read_csv(output_path, skipinitialspace=True)
        print(f"✅ Successfully loaded output data from: {output_path}")
        return df
    except FileNotFoundError:
        print(f"❌ ERROR: Output file not found at '{output_path}'.")
        raise

def run_simulation(config: dict, run_name: str) -> pd.DataFrame:
    """
    Orchestrates the complete simulation workflow: create input, run model, parse output.
    
    Args:
        config (dict): A dictionary with all NAMELIST parameters.
        run_name (str): A unique name for this simulation run.
    
    Returns:
        pd.DataFrame: The resulting atmospheric data.
    """
    run_dir = os.path.join(OUTPUT_DIR, run_name)
    os.makedirs(run_dir, exist_ok=True)
    
    input_file = os.path.join(run_dir, 'INPUT.nml')
    output_file = os.path.join(run_dir, 'OUTPUT.csv')
    
    # Ensure SpicePath is an absolute path for robustness
    config['SpicePath'] = os.path.abspath(SPICE_KERNEL_DIR)
    
    # 1. Generate Input
    create_venus_gram_input(config, input_file)
    
    # 2. Execute Model
    run_venus_gram(VENUS_GRAM_EXECUTABLE, run_dir)
    
    # 3. Parse Output
    df_results = load_venus_gram_output(output_file)
    
    return df_results

# --- Section 5: Data Analysis and Visualization ---

def plot_vertical_profiles(df: pd.DataFrame, run_name: str):
    """
    Visualizes key thermodynamic variables as a function of altitude.
    Uses a log scale for pressure and density as recommended.
    """
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 8), sharey=True)
    fig.suptitle(f'Venus Atmospheric Profiles: {run_name}', fontsize=16)

    # Panel 1: Temperature
    ax1.plot(df['Temperature_K'], df['Height_km'])
    ax1.set_xlabel('Temperature (K)')
    ax1.set_ylabel('Altitude (km)')
    ax1.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Panel 2: Pressure
    ax2.plot(df['Pressure_Nm2'], df['Height_km'])
    ax2.set_xlabel('Pressure (N/m$^2$)')
    ax2.set_xscale('log')
    ax2.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Panel 3: Density
    ax3.plot(df['Density_kgm3'], df['Height_km'])
    ax3.set_xlabel('Density (kg/m$^3$)')
    ax3.set_xscale('log')
    ax3.grid(True, which='both', linestyle='--', linewidth=0.5)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(os.path.join(OUTPUT_DIR, run_name, 'vertical_profiles.png'))
    plt.show()

def plot_monte_carlo_profiles(df: pd.DataFrame, run_name: str):
    """
    Visualizes the mean and standard deviation envelope for Monte Carlo runs.
    As described in Section 4.1, this is key for uncertainty analysis.
    """
    # Group by altitude to analyze the ensemble of runs
    grouped = df.groupby('Height_km')
    mean_density = grouped['PerturbedDensity_kgm3'].mean()
    std_density = grouped['PerturbedDensity_kgm3'].std()
    
    plt.figure(figsize=(10, 8))
    
    # Plot mean density
    plt.plot(mean_density, mean_density.index, 'b-', label='Mean Density')
    
    # Create and plot the +/- 1-sigma envelope using fill_between
    plt.fill_betweenx(mean_density.index, 
                      mean_density - std_density, 
                      mean_density + std_density, 
                      color='blue', alpha=0.2, label='±1σ Dispersion')

    # Plot the +/- 3-sigma envelope
    plt.fill_betweenx(mean_density.index, 
                      mean_density - 3*std_density, 
                      mean_density + 3*std_density, 
                      color='blue', alpha=0.1, label='±3σ Dispersion')

    plt.xscale('log')
    plt.title(f'Monte Carlo Density Profile (N={df["Run_Number"].max()})')
    plt.xlabel('Perturbed Density (kg/m$^3$)')
    plt.ylabel('Altitude (km)')
    plt.legend()
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    plt.savefig(os.path.join(OUTPUT_DIR, run_name, 'monte_carlo_density.png'))
    plt.show()

def plot_wind_profiles(df: pd.DataFrame, run_name: str):
    """Visualizes the zonal and meridional wind components."""
    plt.figure(figsize=(10, 8))
    
    plt.plot(df['EWWind_ms'], df['Height_km'], label='Zonal Wind (East-West)')
    plt.plot(df['NSWind_ms'], df['Height_km'], label='Meridional Wind (North-South)')
    
    plt.axvline(0, color='black', linestyle='--', linewidth=0.7) # Zero wind line
    plt.title(f'Venus Wind Profile: {run_name}')
    plt.xlabel('Wind Speed (m/s)')
    plt.ylabel('Altitude (km)')
    plt.legend()
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    plt.savefig(os.path.join(OUTPUT_DIR, run_name, 'wind_profiles.png'))
    plt.show()

# --- Section 3.2: Strategy 2: High-Performance FFI (Conceptual Example) ---
# NOTE: This is a conceptual demonstration. The actual function names,
#       argument types, and library name ('libgram.so') must be taken from the
#       official GRAM Programmer's Manual. This code will not run without them.

class VenusGramFFI:
    """
    A conceptual class demonstrating direct integration with the GRAM shared library.
    """
    def __init__(self, library_path='libgram.so'):
        # This part will fail if the library is not found or names are wrong.
        try:
            # 1. Load the Shared Library
            self.gram_lib = CDLL(library_path)
            # 2. Define Function Prototypes
            self._define_prototypes()
            print("✅ FFI Wrapper: GRAM library loaded (Conceptual).")
        except OSError:
            print("⚠️ FFI Wrapper: Could not load GRAM shared library. This is expected if not set up.")
            self.gram_lib = None

    def _define_prototypes(self):
        """Define argument and return types for the C functions."""
        # Example: a function 'vgram_get_atmos' that takes position and time
        # and returns atmospheric data via pointers.
        # PROTOTYPE (Hypothetical):
        # int vgram_get_atmos(double lat, double lon, double alt, double time,
        #                     double* temp, double* press, double* dens);
        
        self.gram_lib.vgram_get_atmos.argtypes = [
            c_double, c_double, c_double, c_double, # lat, lon, alt, time
            POINTER(c_double), POINTER(c_double), POINTER(c_double) # pointers for output
        ]
        self.gram_lib.vgram_get_atmos.restype = c_int

    def get_atmosphere(self, lat, lon, alt, time):
        """
        Call the C function to get atmospheric properties at a single point.
        """
        if not self.gram_lib:
            raise RuntimeError("GRAM FFI library not loaded.")
        
        # Prepare variables to receive the output from the C function
        temp = c_double()
        press = c_double()
        dens = c_double()
        
        # 3. Call the Function
        # Use byref() to pass variables by reference (as pointers)
        ret_code = self.gram_lib.vgram_get_atmos(
            lat, lon, alt, time,
            byref(temp), byref(press), byref(dens)
        )
        
        if ret_code != 0:
            raise ValueError(f"GRAM C function returned error code: {ret_code}")
        
        return {
            'temperature': temp.value,
            'pressure': press.value,
            'density': dens.value
        }

# --- Main Execution Block ---

if __name__ == "__main__":
    
    # Ensure the required directories exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if not os.path.exists(SPICE_KERNEL_DIR) or not os.listdir(SPICE_KERNEL_DIR):
        print(f"⚠️ WARNING: SPICE kernel directory '{SPICE_KERNEL_DIR}' is empty or does not exist.")
        print("   Venus-GRAM requires SPICE kernels to run. Download them from NAIF.")
    
    # --- Example 1: Single Vertical Profile (Phase 1 Implementation) ---
    print("\n" + "="*50)
    print("### RUNNING EXAMPLE 1: Single Vertical Profile ###")
    print("="*50)

    # Define the input parameters using the names from Table 2
    single_profile_config = {
        'NumberOfMonteCarloRuns': 1,
        'InitialHeight': 200.0,
        'FinalHeight': 0.0,
        'HeightIncrement': -1.0,
        'InitialLatitude': 30.0,
        'InitialLongitude': 0.0,
        'TrajectoryModel': 1, # 1=Vertical Profile, 2=Ballistic Trajectory, 3=User File
    }

    try:
        df_single = run_simulation(single_profile_config, "single_profile_run")
        print("\n--- Analysis for Single Profile ---")
        print(df_single[['Height_km', 'Temperature_K', 'Pressure_Nm2', 'Density_kgm3']].head())
        
        # Visualize the results using functions from Section 5
        plot_vertical_profiles(df_single, "single_profile_run")
        plot_wind_profiles(df_single, "single_profile_run")

    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print("\n❌ Example 1 failed. Please check your configuration.")
        
    # --- Example 2: Monte Carlo Simulation (Section 4.1) ---
    print("\n" + "="*50)
    print("### RUNNING EXAMPLE 2: Monte Carlo Simulation ###")
    print("="*50)
    
    # Configure a Monte Carlo run
    monte_carlo_config = {
        'NumberOfMonteCarloRuns': 50,
        'InitialRandomSeed': 0, # Use system clock for random seed
        'InitialHeight': 200.0,
        'FinalHeight': 70.0,
        'HeightIncrement': -2.0,
        'InitialLatitude': 0.0,
        'InitialLongitude': 180.0,
        'TrajectoryModel': 1,
        'DensityPerturbationScale': 1.0, # Enable density perturbations
    }

    try:
        df_mc = run_simulation(monte_carlo_config, "monte_carlo_run")
        print("\n--- Analysis for Monte Carlo Run ---")
        # Note the presence of 'Run_Number' and perturbed columns
        print(df_mc[['Run_Number', 'Height_km', 'Density_kgm3', 'PerturbedDensity_kgm3']].head())
        
        # Visualize the statistical dispersion
        plot_monte_carlo_profiles(df_mc, "monte_carlo_run")
    
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print("\n❌ Example 2 failed. Please check your configuration.")