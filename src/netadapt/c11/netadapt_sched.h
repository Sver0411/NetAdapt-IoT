#ifndef NETADAPT_SCHED_H
#define NETADAPT_SCHED_H

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define NETADAPT_MAX_FLOWS 96

typedef enum {
    NA_KIND_EVENT = 0,
    NA_KIND_STATUS = 1,
    NA_KIND_TELEMETRY = 2
} na_flow_kind_t;

typedef enum {
    NA_POL_FIFO = 0,
    NA_POL_EDF = 1,
    NA_POL_MAXWEIGHT = 2,
    NA_POL_PF = 3,
    NA_POL_AOI_GAIN = 4,
    NA_POL_FUD = 5,
    NA_POL_FUD_ADA = 6,
    NA_POL_FUD_ADA_NO_DEBT = 7
} na_policy_t;

typedef struct {
    uint16_t id;
    uint8_t kind;
    uint8_t weight;
    uint16_t tau;
    uint16_t deadline; /* 0 if none */
    uint16_t size_bytes;
    uint16_t service_slots;
} na_flow_cfg_t;

typedef struct {
    int32_t packet_id;
    int32_t generated_slot;
    uint32_t queue_bytes;
    uint8_t has_packet;
} na_head_t;

typedef struct {
    uint16_t n_flows;
    uint8_t policy;
    uint8_t delay_slots;
    double duty;
    na_flow_cfg_t flows[NETADAPT_MAX_FLOWS];
    int32_t last_rx_gen[NETADAPT_MAX_FLOWS];
    double prob[NETADAPT_MAX_FLOWS];
    double debt[NETADAPT_MAX_FLOWS];
    double throughput[NETADAPT_MAX_FLOWS];
    double target_share[NETADAPT_MAX_FLOWS];
} na_sched_t;

void na_sched_init(
    na_sched_t *s,
    na_policy_t policy,
    const na_flow_cfg_t *flows,
    uint16_t n_flows,
    uint8_t delay_slots,
    double duty
);

void na_sched_on_ack(
    na_sched_t *s,
    uint16_t flow_id,
    int32_t pkt_generated,
    int32_t arrival_slot,
    uint16_t pkt_size,
    bool ok,
    double *received_out,
    double *ack_bytes_out
);

void na_sched_step_state(
    na_sched_t *s,
    const uint8_t *backlogged,
    const double *received,
    const double *ack_bytes
);

/* Returns selected flow index in [0, n_flows-1], or -1 if none eligible. */
int32_t na_sched_choose(
    const na_sched_t *s,
    int32_t t,
    const na_head_t *heads,
    double tokens
);

#ifdef __cplusplus
}
#endif

#endif /* NETADAPT_SCHED_H */
