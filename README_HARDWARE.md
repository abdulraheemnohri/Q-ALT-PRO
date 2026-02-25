# Q-ALT PRO: Hardware Probabilistic Accelerator Blueprint

## Vision
To move beyond software simulation of probabilistic states and implement a dedicated classical CMOS-based accelerator that mimics stochastic quantum behaviors (Probabilistic Bits or p-bits).

## Architecture Overview

### 1. Probabilistic Bit (p-bit) Unit
Unlike a standard digital bit (0 or 1), the p-bit unit fluctuates between states based on an input bias $I$.
- **Components**:
    - CMOS Thermal Noise Source (or pseudo-random bitstream).
    - Tunable Comparator.
    - Activation Function (Sigmoid-like) implemented in analog or lookup tables.
- **Equation**: $State = sign(tanh(\beta \cdot I) - random(-1, 1))$

### 2. Interaction Matrix (Synaptic Layer)
A crossbar array or digital multiplier-accumulator (MAC) tree that implements the correlation matrix $C_{ij}$.
- Allows $O(1)$ or $O(N)$ calculation of the local field $I_i = \sum C_{ij} \cdot s_j$.

### 3. Annealing Controller
A hardware state machine that controls the "Temperature" ($\beta$) by scaling the bias currents or noise levels.
- Fast cooling schedules implemented in hardware to avoid CPU overhead.

## Implementation Paths

### Phase A: FPGA Prototype
- Map p-bits to FPGA LUTs.
- Use High-Speed Transceivers for cluster communication.
- Target: 100+ fully connected p-bits.

### Phase B: Custom ASIC
- Use sub-threshold MOSFET noise for true entropy generation.
- Massive parallel updates (Asynchronous Gibbs Sampling).
- Target: 1000+ p-bits at sub-1W power.

## Integration with Q-ALT PRO
The hardware accelerator connects via the **Cluster Mode** interface. The `WorkerNode` in Termux can offload the `core/state.py` calculations to the hardware via a serial or PCIe bridge.

---
*Blueprint Version: 1.0.0*
*Focus: Scalability, Energy Efficiency, Probabilistic Intelligence*
