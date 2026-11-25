/*
 * ESP32-S3 On-Chip Hardware Benchmark for NetAdapt-IoT Pure C11 Scheduler Kernel.
 * Runs the exact same per-slot workload as src/netadapt/c11/bench_main.c on real
 * ESP32-S3 silicon (240 MHz Xtensa LX7, -Os) and measures:
 *   1. Full per-slot loop (na_sched_step_state + na_sched_choose + na_sched_on_ack)
 *   2. Decision-only scan (na_sched_choose)
 *   3. Static struct RAM (sizeof(na_sched_t)) and exact 0-byte dynamic heap delta
 */
#include <Arduino.h>
#include <esp_timer.h>
#include <stdio.h>

extern "C" {
#include "netadapt_sched.h"
}

static na_sched_t g_sched;
static na_flow_cfg_t g_cfgs[NETADAPT_MAX_FLOWS];
static na_head_t g_heads[NETADAPT_MAX_FLOWS];
static uint8_t g_back[NETADAPT_MAX_FLOWS];
static double g_rec[NETADAPT_MAX_FLOWS];
static double g_ackb[NETADAPT_MAX_FLOWS];

static void init_workload(na_policy_t pol, uint16_t n_flows) {
  for (uint16_t i = 0; i < n_flows; ++i) {
    g_cfgs[i].id = i;
    g_cfgs[i].kind = (uint8_t)(i % 3);
    g_cfgs[i].weight = (i % 3 == 0) ? 4 : ((i % 3 == 1) ? 3 : 1);
    g_cfgs[i].tau = (i % 3 == 0) ? 6 : ((i % 3 == 1) ? 12 : 30);
    g_cfgs[i].deadline = (i % 3 == 0) ? 6 : 0;
    g_cfgs[i].size_bytes = 64;
    g_cfgs[i].service_slots = 1;

    g_heads[i].packet_id = (int32_t)i;
    g_heads[i].generated_slot = 100 - (int32_t)(i % 5);
    g_heads[i].queue_bytes = 128;
    g_heads[i].has_packet = 1;
    g_back[i] = 1;
    g_rec[i] = 0.0;
    g_ackb[i] = 0.0;
  }
  na_sched_init(&g_sched, pol, g_cfgs, n_flows, 1, 0.8);
}

static void bench_one(na_policy_t pol, const char *name, uint16_t n_flows, int iters) {
  init_workload(pol, n_flows);
  volatile int64_t sink = 0;

  /* Warmup */
  for (int w = 0; w < 100; ++w) {
    int32_t t = 105 + w;
    g_heads[w % n_flows].generated_slot = t - (int32_t)(w % 4);
    na_sched_step_state(&g_sched, g_back, g_rec, g_ackb);
    int32_t pick = na_sched_choose(&g_sched, t, g_heads, 4.0);
    if (pick >= 0) {
      g_rec[pick] = 0.0;
      g_ackb[pick] = 0.0;
      na_sched_on_ack(&g_sched, (uint16_t)pick, g_heads[pick].generated_slot, t + 2, 64,
                      (w % 5) != 0, g_rec, g_ackb);
      sink += pick;
    }
  }

  /* 1. Full per-slot loop (identical to host bench_main.c) */
  init_workload(pol, n_flows);
  int64_t t0 = esp_timer_get_time();
  uint32_t c0 = ESP.getCycleCount();
  for (int k = 0; k < iters; ++k) {
    int32_t t = 105 + k;
    g_heads[k % n_flows].generated_slot = t - (int32_t)(k % 4);
    na_sched_step_state(&g_sched, g_back, g_rec, g_ackb);
    int32_t pick = na_sched_choose(&g_sched, t, g_heads, 4.0);
    if (pick >= 0) {
      g_rec[pick] = 0.0;
      g_ackb[pick] = 0.0;
      na_sched_on_ack(&g_sched, (uint16_t)pick, g_heads[pick].generated_slot, t + 2, 64,
                      (k % 5) != 0, g_rec, g_ackb);
      sink += pick;
    }
  }
  uint32_t c1 = ESP.getCycleCount();
  int64_t t1 = esp_timer_get_time();
  double full_us = (double)(t1 - t0) / (double)iters;
  double full_cyc = (double)(c1 - c0) / (double)iters;

  /* 2. Decision-only scan (na_sched_choose) */
  int64_t t2 = esp_timer_get_time();
  uint32_t c2 = ESP.getCycleCount();
  for (int k = 0; k < iters; ++k) {
    int32_t pick = na_sched_choose(&g_sched, 600, g_heads, 4.0);
    sink += pick;
  }
  uint32_t c3 = ESP.getCycleCount();
  int64_t t3 = esp_timer_get_time();
  double choose_us = (double)(t3 - t2) / (double)iters;
  double choose_cyc = (double)(c3 - c2) / (double)iters;

  Serial.printf(
      "BENCH policy=%s n_flows=%u iters=%d full_us=%.3f full_cyc=%.1f choose_us=%.3f choose_cyc=%.1f sink=%lld\n",
      name, n_flows, iters, full_us, full_cyc, choose_us, choose_cyc, (long long)sink);
  Serial.flush();
  delay(15);
}

static void run_suite() {
  const uint16_t scales[4] = {8, 24, 48, 96};
  const int iters = 500;
  uint32_t heap_before = ESP.getFreeHeap();

  Serial.println("NETADAPT_ESP32S3_BENCH_START");
  Serial.printf("MCU_INFO chip=%s rev=%d cpu_mhz=%u sizeof_na_sched_t=%u max_flows=%d\n",
                ESP.getChipModel(), ESP.getChipRevision(), ESP.getCpuFreqMHz(),
                (unsigned)sizeof(na_sched_t), NETADAPT_MAX_FLOWS);

  for (int i = 0; i < 4; ++i) {
    bench_one(NA_POL_FIFO, "fifo", scales[i], iters);
    bench_one(NA_POL_EDF, "edf", scales[i], iters);
    bench_one(NA_POL_AOI_GAIN, "aoi_gain", scales[i], iters);
    bench_one(NA_POL_FUD, "fud", scales[i], iters);
    bench_one(NA_POL_FUD_ADA, "fud_ada", scales[i], iters);
  }

  uint32_t heap_after = ESP.getFreeHeap();
  Serial.printf("HEAP_CHECK before=%u after=%u delta=%d\n",
                heap_before, heap_after, (int)heap_before - (int)heap_after);
  Serial.println("NETADAPT_ESP32S3_BENCH_END");
}

void setup() {
  Serial.begin(115200);
  uint32_t t0 = millis();
  while (!Serial && (millis() - t0) < 4000) {
    delay(20);
  }
  delay(800);
  run_suite();
}

void loop() {
  delay(6000);
  run_suite();
}
