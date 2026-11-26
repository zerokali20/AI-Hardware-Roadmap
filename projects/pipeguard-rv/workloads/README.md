# PipeGuard-RV Workloads

Eight deterministic RV32I workloads defined in [workloads.py](file:///d:/AI-Hardware-Roadmap/projects/pipeguard-rv/workloads/workloads.py) for fair comparative evaluation across `B0`, `M0`, `M1`, and `M2`:

| Workload | Cycles | Target Behaviour |
|---|---:|---|
| `sequential` | 35 | Linear ALU execution without branches or stalls |
| `conditional_branch` | 45 | Taken and not-taken `BEQ`, `BNE`, `BLT` |
| `loop` | 70 | Iterative backward-branch summation loop |
| `jal_jalr` | 45 | Direct call (`JAL`) and indirect return (`JALR`) |
| `load_use_hazard` | 45 | Dependent `LW` → `ADD`/`ADDI` triggering load-use stalls |
| `pipeline_flush` | 45 | Repeated control-hazard pipeline squashes |
| `mixed` | 75 | Combined ALU, store/load, stall, loop, and call/return |
| `iot_controller` | 90 | Simulated embedded IoT sensor-threshold controller writing actuator output |
