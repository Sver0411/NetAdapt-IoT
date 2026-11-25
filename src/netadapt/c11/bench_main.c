#include "netadapt_sched.h"

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

static double now_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1e9 + (double)ts.tv_nsec;
}

static void bench_one(na_policy_t pol, const char *name, uint16_t n_flows, int iters) {
    na_flow_cfg_t cfgs[NETADAPT_MAX_FLOWS];
    na_head_t heads[NETADAPT_MAX_FLOWS];
    uint8_t back[NETADAPT_MAX_FLOWS];
    double rec[NETADAPT_MAX_FLOWS];
    double ackb[NETADAPT_MAX_FLOWS];

    for (uint16_t i = 0; i < n_flows; ++i) {
        cfgs[i].id = i;
        cfgs[i].kind = (uint8_t)(i % 3);
        cfgs[i].weight = (i % 3 == 0) ? 4 : ((i % 3 == 1) ? 3 : 1);
        cfgs[i].tau = (i % 3 == 0) ? 6 : ((i % 3 == 1) ? 12 : 30);
        cfgs[i].deadline = (i % 3 == 0) ? 6 : 0;
        cfgs[i].size_bytes = 64;
        cfgs[i].service_slots = 1;
        heads[i].packet_id = (int32_t)i;
        heads[i].generated_slot = 100 - (int32_t)(i % 5);
        heads[i].queue_bytes = 128;
        heads[i].has_packet = 1;
        back[i] = 1;
        rec[i] = 0.0;
        ackb[i] = 0.0;
    }

    na_sched_t st;
    na_sched_init(&st, pol, cfgs, n_flows, 1, 0.8);

    volatile int64_t sink = 0;
    double t0 = now_ns();
    for (int k = 0; k < iters; ++k) {
        int32_t t = 105 + k;
        heads[k % n_flows].generated_slot = t - (int32_t)(k % 4);
        na_sched_step_state(&st, back, rec, ackb);
        int32_t pick = na_sched_choose(&st, t, heads, 4.0);
        if (pick >= 0) {
            rec[pick] = 0.0;
            ackb[pick] = 0.0;
            na_sched_on_ack(&st, (uint16_t)pick, heads[pick].generated_slot, t + 2, 64, (k % 5) != 0, rec, ackb);
            sink += pick;
        }
    }
    double dt_ns = now_ns() - t0;
    printf("{\"policy\":\"%s\",\"n_flows\":%u,\"iters\":%d,\"mean_ns\":%.2f,\"sink\":%lld}\n",
           name, n_flows, iters, dt_ns / (double)iters, (long long)sink);
}

int main(void) {
    printf("{\"sizeof_na_sched_t\":%zu,\"sizeof_na_flow_cfg_t\":%zu,\"sizeof_na_head_t\":%zu,\"max_flows\":%d}\n",
           sizeof(na_sched_t), sizeof(na_flow_cfg_t), sizeof(na_head_t), NETADAPT_MAX_FLOWS);
    const uint16_t scales[4] = {8, 24, 48, 96};
    for (int i = 0; i < 4; ++i) {
        bench_one(NA_POL_FUD, "fud", scales[i], 50000);
        bench_one(NA_POL_FUD_ADA, "fud_ada", scales[i], 50000);
    }
    return 0;
}
