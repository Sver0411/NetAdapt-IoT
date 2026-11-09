<h1 align="center">NetAdapt-IoT</h1>

<p align="center"><strong>Adaptive Scheduling for a Shared IoT Gateway Outlet</strong></p>

<p align="center">Age of Information · Deadline-Aware Scheduling · Fair Resource Allocation</p>

---

<p align="center">
  <a href="#project-overview">Overview</a> ·
  <a href="#research-question-and-method">Method</a> ·
  <a href="#key-findings">Results</a> ·
  <a href="#implementation-status">Status</a> ·
  <a href="#quick-start">Quick Start</a> ·
  <a href="README.zh-CN.md">简体中文</a>
</p>

---

<a id="project-overview"></a>

NetAdapt-IoT is a research platform for scheduling multiple IoT traffic flows over a shared communication outlet. It studies how limited network resources can be allocated among fresh state updates, deadline-sensitive events, and devices with different service requirements.

The project combines a Python slotted model, nine baseline schedulers, the Freshness–Urgency–Debt (FUD) policy, three mechanism ablations, and an automated experiment pipeline. The refined evaluation contains **12,480 runs across 48 named conditions, 20 seeds, and 13 policies**: the original 15-scenario matrix, four fixed-total-load scale conditions, 25 model-sensitivity conditions, and four congestion bucket-capacity conditions. It records packet outcomes, class-specific delivery metrics, actual service shares, and paired intervals. ESP32-S3/E220 firmware and a PC replay tool support the next stage of physical link experiments.

<a id="research-question-and-method"></a>

## Research question and method

How should a shared IoT gateway schedule mixed traffic to balance information freshness, event deadlines, and service fairness as load and link conditions change?

FUD makes each scheduling decision from three components:

1. **Freshness:** the expected normalized squared-AoI reduction from delivering a state update.
2. **Urgency:** the remaining deadline slack and waiting time of an event packet.
3. **Debt:** the accumulated service demand of backlogged flows.

The scheduler combines these components with an ACK-based success estimate and packet service cost, then selects an eligible head-of-line packet. The component coefficients are `1 / 1 / 0.25`. The decision scan takes `O(N)` time for `N` flows; queue expiration is handled separately.

State flows keep their newest waiting update. Event flows use bounded FIFO queues. A token bucket regulates the communication budget, and the shared server completes one non-preemptive transmission at a time.

```mermaid
flowchart LR
    CFG["Configuration + seed"] --> TRACE["Traffic + channel trace"]
    TRACE --> QUEUE["State / event queues"]
    QUEUE --> SCHED["Scheduling policy"]
    SCHED --> LINK["Shared outlet + budget"]
    LINK --> ACK["ACK feedback"]
    ACK --> SCHED
    LINK --> LOG["Packet records"]
    LOG --> ANALYSIS["Metrics + paired analysis + plots"]
```

The default simulation uses 100 ms slots, 64-byte payloads, a 16-byte abstract header, and a 6,400 bit/s effective service rate. The token bucket holds four service slots. The [method specification](research/design/proposal.md) defines the score, queue rules, timing, and metrics.

## Baselines and experiment design

| Policy | Scheduling principle |
| --- | --- |
| `fifo` | Oldest eligible head-of-line packet |
| `rr` / `wrr` | Round robin / weighted round robin |
| `edf` / `priority` | Earliest deadline / fixed business priority |
| `maxweight` / `pf` | Queue pressure / proportional fairness |
| `aoi_gain` / `debt` | Freshness gain / accumulated service debt |
| `fud` | Combined freshness, urgency, and debt |
| `fud_no_age` / `fud_no_urgency` / `fud_no_debt` | Individual component ablations |

Each scenario/seed group gives all 13 methods the same traffic, time-indexed potential channel outcomes, queue rules, and resource budget. Scheduling uses packet timestamps, queue state, and past ACK observations.

The 15 scenarios cover normal load, congestion, 8/24/48/96 logical devices, unequal source rates, equal priorities, weak links, Markov losses, bursts, resource-budget changes, feedback delay, mixed packet sizes, and lossless service.

Evaluation separates state AoI, replacement and transmission success from event deadline outcomes. Resource fairness uses actual abstract service slots, with equal-share and weight-proportional Jain references. Every policy uses the same main window and arrival-free tail; main-window pending snapshots are separate from final outcomes. The [metric definitions](docs/metrics-v2.md), [protocol](research/experiments/protocol.md), and [frozen configurations](configs/refined_v1/) define each denominator and control.

<a id="key-findings"></a>

## Key findings: refined software evaluation

The main matrix contains 3,900 runs, the fixed-total-load scale group 1,040, model sensitivity 6,500, and congestion bucket sensitivity 1,040. Each condition uses seeds 100–119 and all 13 methods. Sensitivity groups retain their own baseline; repeated baseline conditions are analyzed within their groups. State AoI and Service Share use the main observation window; event outcomes include the common tail.

| Scenario | Policy | State mean AoI (s) ↓ | Event miss (%) ↓ | Jain Service Share ↑ |
| --- | --- | ---: | ---: | ---: |
| Congestion | FIFO | 2.2841 | 96.42 | 0.7159 |
| Congestion | AoI-gain | 4.8532 | 47.31 | 0.7441 |
| Congestion | FUD | 3.5046 | 63.15 | 0.8187 |
| Bursty | FIFO | 5.5966 | 33.91 | 0.9751 |
| Bursty | AoI-gain | 5.6617 | 13.83 | 0.9808 |
| Bursty | FUD | 5.5926 | 18.13 | 0.9818 |

**Congestion:** FUD−FIFO event miss is -33.27238 [-33.59573, -32.98051] percentage points; state AoI changes by +1.22049 [+1.20904, +1.23202] s (95% paired bootstrap CI). FUD has higher event miss and lower state AoI than AoI-gain.

**Debt ablation:** congestion Service Share Jain changes by +0.00052 [-0.00074, +0.00171]. The interval spans zero, so the resource-fairness gain is unresolved in this condition.

**Scale and model controls:** scale A keeps per-flow rate fixed; scale B keeps total traffic and class arrivals fixed across 8/24/48/96 flows. Bucket capacities 2/4/8/16 and seven other parameter groups test the model conditions. The [A–K report](research/REPORT.md) gives all five hypotheses, comparator intervals, favorable and adverse results.

![Main-window freshness, event deadlines, and service allocation](output/study_refined_v1/overview.png)

![FUD component ablations](output/study_refined_v1/ablations.png)

Full data: [summary](output/study_refined_v1/summary.csv) · [paired comparisons](output/study_refined_v1/paired_differences.csv) · [per-flow metrics](output/study_refined_v1/per_flow.csv) · [adverse directions](output/study_refined_v1/negative_results.csv) · [fixed-total scale](output/study_refined_v1/scaling/results.md) · [model sensitivity](output/study_refined_v1/sensitivity/results.md) · [congestion buckets](output/study_refined_v1/bucket_load/results.md). Historical v1 results remain in [output/study](output/study/results.md).

<a id="implementation-status"></a>

## Implementation status

| Component | Progress |
| --- | --- |
| Mixed-flow queues, common tail, and 13 scheduling policies | Implemented; FUD score unchanged |
| Refined software experiments | 12,480 completed runs; zero execution failures |
| Python unit and integration checks | 48 tests passed |
| Independent raw-ledger audit | All 12,480 runs; packet, resource, AoI, and QoS checks passed |
| Published baseline preservation | 40,111 historical files unchanged; 100 FUD main-window runs match |
| PF simulation and replay | Shared slot EWMA; mocked ACK timing tests passed |
| ESP32-S3 N16R8 firmware | Sender/receiver builds passed; QIO/OPI SDK and 16 MB image header verified |
| Physical calibration, radio runs, and power capture | Next stage |

The hardware path uses two ESP32-S3 boards and two E220-400T22S radios. The PC schedules logical flows through the sender; the receiver validates CRC-protected frames and returns ACKs. See the [hardware guide](hardware/README.md) and [validation record](docs/validation/status.md).

<a id="quick-start"></a>

## Quick start and reproduction

Use Python 3.11 or newer. From the project directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev,hardware]'
python -m pytest -q
```

Run the 78-run software example and generate its report:

```bash
python run.py run --config configs/refined_v1/pilot.json --out output/quickstart --workers 2
python run.py analyze --out output/quickstart
```

Run the main experiment matrix:

```bash
python run.py run --config configs/refined_v1/main.json --out output/reproduction --workers 4
python run.py analyze --out output/reproduction
```

Full scale and sensitivity commands are in the [reproduction guide](docs/reproducibility.md).

Choose a new output directory for each fresh experiment. Matching source hashes and configurations allow an existing experiment to resume. The `hardware` extra includes serial-test dependencies and PlatformIO.

Audit the reproduced dataset or build the firmware:

```bash
python scripts/audit_refined.py output/reproduction
pio run -d hardware/firmware
```

Each run saves its configuration, seed, source/trace hashes, packet outcomes, and scheduling decisions. Analysis adds CSV summaries, paired bootstrap intervals, PNG figures, and a Markdown report. Environment details are recorded in [requirements-lock.txt](requirements-lock.txt) and the experiment [manifest](output/study_refined_v1/manifest.json).

The repository includes experiment summaries, per-flow tables, reports, and figures. Packet-level logs and historical source snapshots remain in the local output directories; the experiment commands regenerate packet records from the saved configurations.

## Related research projects

| Project | Research focus |
| --- | --- |
| [AdaptiveSense](https://github.com/Sver0411/AdaptiveSense) | Change-aware sampling and upload decisions |
| [SensorTrust](https://github.com/Sver0411/SensorTrust) | Sensor health assessment and fault detection |
| [EventGuard-LoRa](https://github.com/Sver0411/EventGuard-LoRa) | Critical-event delivery and bounded communication redundancy |
| [Smart-Agriculture-Edge-AI](https://github.com/Sver0411/Smart-Agriculture-Edge-AI) | Multi-node sensing, edge decisions, and offline recovery |

NetAdapt-IoT focuses on network-level service ordering. It keeps source generation fixed and studies how multiple devices and business flows share communication opportunities.

## Documentation and roadmap

| Topic | Documentation |
| --- | --- |
| Method and equations | [Research proposal](research/design/proposal.md) |
| Experiment design | [Protocol](research/experiments/protocol.md) · [Configuration](configs/refined_v1/main.json) |
| Software structure | [Architecture](docs/architecture.md) |
| Results and data | [Results report](output/study_refined_v1/results.md) · [Summary CSV](output/study_refined_v1/summary.csv) |
| Reproduction and auditing | [Reproduction guide](docs/reproducibility.md) · [Audit](output/study_refined_v1/audit.json) |
| Hardware and development | [Hardware guide](hardware/README.md) · [Roadmap](docs/roadmap.md) |

Next development priorities:

- Calibrate single-frame transmission, ACK timing, and effective service rate on the ESP32-S3/E220 link.
- Replay shared logical-flow workloads through the physical outlet.
- Extend experiments to independent sending nodes and network access control.
- Evaluate longer traffic traces, additional scheduling methods, and measured communication energy.
