#include "netadapt_sched.h"

#include <math.h>
#include <string.h>

#define NA_PF_ALPHA 0.01
#define NA_FUD_ADA_ALPHA_U 1.0
#define NA_FUD_ADA_BETA_D 2.5

void na_sched_init(
    na_sched_t *s,
    na_policy_t policy,
    const na_flow_cfg_t *flows,
    uint16_t n_flows,
    uint8_t delay_slots,
    double duty
) {
    memset(s, 0, sizeof(*s));
    if (n_flows > NETADAPT_MAX_FLOWS) {
        n_flows = NETADAPT_MAX_FLOWS;
    }
    s->n_flows = n_flows;
    s->policy = (uint8_t)policy;
    s->delay_slots = delay_slots;
    s->duty = duty;

    double w_sum = 0.0;
    for (uint16_t i = 0; i < n_flows; ++i) {
        s->flows[i] = flows[i];
        w_sum += (double)flows[i].weight;
    }
    if (w_sum <= 0.0) {
        w_sum = 1.0;
    }
    for (uint16_t i = 0; i < n_flows; ++i) {
        s->last_rx_gen[i] = 0;
        s->prob[i] = 0.8;
        s->debt[i] = 0.0;
        s->throughput[i] = 1.0;
        s->target_share[i] = 0.5 * duty * 0.8 * (double)flows[i].weight
                             / (w_sum * (double)flows[i].service_slots);
    }
}

void na_sched_on_ack(
    na_sched_t *s,
    uint16_t flow_id,
    int32_t pkt_generated,
    int32_t arrival_slot,
    uint16_t pkt_size,
    bool ok,
    double *received_out,
    double *ack_bytes_out
) {
    if (flow_id >= s->n_flows) {
        return;
    }
    const na_flow_cfg_t *f = &s->flows[flow_id];
    s->prob[flow_id] = 0.9 * s->prob[flow_id] + 0.1 * (ok ? 1.0 : 0.0);
    if (!ok) {
        return;
    }
    bool fresh = pkt_generated > s->last_rx_gen[flow_id];
    bool timely = (f->deadline == 0) || (arrival_slot <= pkt_generated + (int32_t)f->deadline);
    if (pkt_generated > s->last_rx_gen[flow_id]) {
        s->last_rx_gen[flow_id] = pkt_generated;
    }
    if (timely && (f->kind == NA_KIND_EVENT || fresh)) {
        received_out[flow_id] += 1.0;
    }
    ack_bytes_out[flow_id] += (double)pkt_size;
}

void na_sched_step_state(
    na_sched_t *s,
    const uint8_t *backlogged,
    const double *received,
    const double *ack_bytes
) {
    for (uint16_t i = 0; i < s->n_flows; ++i) {
        double d = s->debt[i] + s->target_share[i] * (backlogged[i] ? 1.0 : 0.0) - received[i];
        if (d < 0.0) d = 0.0;
        if (d > 50.0) d = 50.0;
        s->debt[i] = d;
        s->throughput[i] = (1.0 - NA_PF_ALPHA) * s->throughput[i] + NA_PF_ALPHA * ack_bytes[i];
    }
}

static double compute_score(const na_sched_t *s, uint16_t i, int32_t t, const na_head_t *h) {
    const na_flow_cfg_t *f = &s->flows[i];
    double svc = (double)f->service_slots;
    double w = (double)f->weight;
    double tau = (double)f->tau;
    double age = (double)(t - s->last_rx_gen[i]);
    double wait = (double)(t - h->generated_slot);
    double lag = svc + (double)s->delay_slots;
    double dl = (double)(f->deadline ? f->deadline : f->tau);
    double slack = (double)h->generated_slot + dl - ((double)t + lag);
    double a2 = (age + lag) * (age + lag);
    double w2 = (wait + lag) * (wait + lag);
    double raw_gain = (a2 > w2) ? (a2 - w2) / (2.0 * tau * tau) : 0.0;

    switch ((na_policy_t)s->policy) {
        case NA_POL_EDF:
            return -((double)h->generated_slot + dl);
        case NA_POL_MAXWEIGHT:
            return s->prob[i] * (double)h->queue_bytes / svc;
        case NA_POL_PF: {
            double thr = s->throughput[i] > 1e-6 ? s->throughput[i] : 1e-6;
            return s->prob[i] * (double)f->size_bytes / (svc * thr);
        }
        case NA_POL_AOI_GAIN:
            return s->prob[i] * (w * raw_gain) / svc;
        case NA_POL_FUD: {
            double gain = (f->kind == NA_KIND_EVENT) ? 0.0 : (w * raw_gain);
            double urg = (f->kind == NA_KIND_EVENT)
                             ? (w * (1.0 + wait / tau) / (1.0 + (slack > 0.0 ? slack : 0.0)))
                             : 0.0;
            return s->prob[i] * (gain + urg + 0.25 * s->debt[i]) / svc;
        }
        case NA_POL_FUD_ADA:
        case NA_POL_FUD_ADA_NO_DEBT: {
            double fresh_t = (f->kind == NA_KIND_EVENT) ? 0.0 : (w * sqrt(raw_gain));
            double urg_t = (f->kind == NA_KIND_EVENT)
                               ? (w * (1.0 + wait / tau)
                                  * (1.0 + NA_FUD_ADA_ALPHA_U / (1.0 + (slack > 0.0 ? slack : 0.0))))
                               : 0.0;
            double debt_t = (s->policy == NA_POL_FUD_ADA)
                                ? (NA_FUD_ADA_BETA_D * w * log1p(s->debt[i]))
                                : 0.0;
            return s->prob[i] * (fresh_t + urg_t + debt_t) / svc;
        }
        case NA_POL_FIFO:
        default:
            return 0.0;
    }
}

int32_t na_sched_choose(
    const na_sched_t *s,
    int32_t t,
    const na_head_t *heads,
    double tokens
) {
    int32_t best = -1;
    double best_score = -1e300;
    int32_t best_gen = 0;
    int32_t best_pid = 0;

    for (uint16_t i = 0; i < s->n_flows; ++i) {
        if (!heads[i].has_packet) {
            continue;
        }
        if ((double)s->flows[i].service_slots > tokens + 1e-9) {
            continue;
        }
        if (s->policy == NA_POL_FIFO) {
            if (best < 0
                || heads[i].generated_slot < best_gen
                || (heads[i].generated_slot == best_gen && heads[i].packet_id < best_pid)) {
                best = (int32_t)i;
                best_gen = heads[i].generated_slot;
                best_pid = heads[i].packet_id;
            }
            continue;
        }
        double sc = compute_score(s, i, t, &heads[i]);
        if (best < 0
            || sc > best_score
            || (sc == best_score && heads[i].generated_slot < best_gen)
            || (sc == best_score && heads[i].generated_slot == best_gen && (int32_t)i < best)) {
            best = (int32_t)i;
            best_score = sc;
            best_gen = heads[i].generated_slot;
        }
    }
    return best;
}
