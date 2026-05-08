# Paper Figure Artifact Extraction

## Summary
- Paper source: resources/papers/hoodie/ocr/merged.tex
- Artifact root: artifacts/campaigns/paper-baseline-reproduction
- Full paper comparison ready: false

## Figure Support
- Figure 7: partially_supported (comparison_ready=false)
  - title: Edge layer topology graph of matrix G with 20 EAs
  - missing: topology_adjacency_edges
- Figure 8: unsupported (comparison_ready=false)
  - title: Accumulated reward time-course by learning rate and discount factor
  - missing: training_episode_reward_curves, reward_by_learning_rate, reward_by_discount_factor, true_hoodie_drl_training_logs
- Figure 9: partially_supported (comparison_ready=false)
  - title: HOODIE behavior insights under varying system parameters
  - missing: average_reward_by_task_arrival_probability, reward_by_drl_agent_count, reward_by_cpu_capacity, reward_by_agent_count_traffic_scenario, reward_by_offloading_data_rate, true_hoodie_drl_validation_rewards
- Figure 10: partially_supported (comparison_ready=false)
  - title: Performance comparison of HOODIE and six baselines
  - missing: cpu_capacity_sweep_artifacts, timeout_sweep_artifacts, structured_paper_numeric_curve_values
- Figure 11: unsupported (comparison_ready=false)
  - title: Average task delay of HOODIE with vs without LSTM
  - missing: hoodie_lstm_training_delay_curve, hoodie_without_lstm_training_delay_curve, training_episode_delay_logs

## Global Warnings
- Current baseline artifacts do not contain true HOODIE DRL training curves.
- Do not claim paper reproduction validity from this scaffold.
- high_drop_ratio
- identical_policy_signature
- near_identical_outcome_behavior
- policy_behavior_collapsed
- saturation_dominant
- scenario_output_collapsed
- trace_comparison_status:different_count,same_count_but_different_slots
- weak_scenario_differentiation

## Unsupported Requirements
- average_reward_by_task_arrival_probability
- cpu_capacity_sweep_artifacts
- hoodie_lstm_training_delay_curve
- hoodie_without_lstm_training_delay_curve
- reward_by_agent_count_traffic_scenario
- reward_by_cpu_capacity
- reward_by_discount_factor
- reward_by_drl_agent_count
- reward_by_learning_rate
- reward_by_offloading_data_rate
- structured_paper_numeric_curve_values
- timeout_sweep_artifacts
- topology_adjacency_edges
- training_episode_delay_logs
- training_episode_reward_curves
- true_hoodie_drl_training_logs
- true_hoodie_drl_validation_rewards

## Machine-Readable Figure Entries
```json
[
  {
    "artifact_backed_reproduction_data": {
      "trace_metadata_available": true
    },
    "caveats": [
      "EA count is supported by OCR metadata, but no committed artifact explicitly encodes graph edges."
    ],
    "comparison_ready": false,
    "extracted_artifact_metrics": {
      "observed_trace_count": 20
    },
    "figure_id": "Figure 7",
    "missing_artifacts": [
      "topology_adjacency_edges"
    ],
    "paper_caption_supported_metadata": {
      "ea_count": 20,
      "matrix_name": "G"
    },
    "paper_claim_type": "topology_caption",
    "paper_numeric_target_data": {
      "available": false,
      "missing": [
        "topology_adjacency_edges"
      ]
    },
    "paper_ocr_evidence": [
      {
        "char_offset": 137101,
        "figure_id": "Figure 7",
        "snippet_index": 0,
        "source_path": "resources/papers/hoodie/ocr/merged.tex",
        "text": "<td>10000 samples</td></tr><tr><td>Task Drop Penalty</td><td>\\$C\\$</td><td>40</td></tr><tr><td>Batch size</td><td>\\$N\\_\\{B\\}\\$</td><td>64 samples</td></tr></tbody></table></body></html> 1234567891011121314151617181920 FIGURE 7. Edge layer topology graph of matrix G with 20 EAs. VOLUME , 17 ===== page\\_018\\_0\\_res.txt ===== is the cumulative reward, as defined in (20) and (24), that was collected in a series of 5000 episodes, and averaged across all the distributed HOODIE agents. Note that, since the task delay is considered a negative metric, the ideal value is zero, which explains why the reward curves are negative and increasing. In Fig. 8b, the impact of the discount factor γ is a"
      }
    ],
    "source_artifacts": [
      "matrix/traces/extreme-1.json",
      "matrix/traces/extreme-2.json",
      "matrix/traces/extreme-3.json",
      "matrix/traces/extreme-4.json",
      "matrix/traces/extreme-5.json",
      "matrix/traces/heavy-1.json",
      "matrix/traces/heavy-2.json",
      "matrix/traces/heavy-3.json",
      "matrix/traces/heavy-4.json",
      "matrix/traces/heavy-5.json"
    ],
    "support_status": "partially_supported",
    "title": "Edge layer topology graph of matrix G with 20 EAs"
  },
  {
    "artifact_backed_reproduction_data": {
      "available": false
    },
    "caveats": [
      "Current baseline campaign artifacts are evaluation outputs, not HOODIE DRL training reward curves."
    ],
    "comparison_ready": false,
    "extracted_artifact_metrics": {},
    "figure_id": "Figure 8",
    "missing_artifacts": [
      "training_episode_reward_curves",
      "reward_by_learning_rate",
      "reward_by_discount_factor",
      "true_hoodie_drl_training_logs"
    ],
    "paper_caption_supported_metadata": {
      "dimensions": [
        "learning_rate",
        "discount_factor",
        "training_episode"
      ]
    },
    "paper_claim_type": "training_curve_caption",
    "paper_numeric_target_data": {
      "available": false,
      "missing": [
        "paper_numeric_curve_values"
      ]
    },
    "paper_ocr_evidence": [
      {
        "char_offset": 143495,
        "figure_id": "Figure 8",
        "snippet_index": 0,
        "source_path": "resources/papers/hoodie/ocr/merged.tex",
        "text": "| -61.0 | -62.0 | 32 | -28.5 | -27.5 | -26.5 | 3500 | -56.0 | -58.0 | -598 | | -61.0 | -62.0 | 32.5 | -28.5 | -27.5 | -26.5 | 12.0 4000 | -56.0 | -58.0 | -599 | | -61.0 | -62.0 | 32.8 | -28.5 | -27.5 | -26.5 | FIGURE 8. Accumulated reward time-course averaged across the distributed HOoDIE agents as a function of the training episodes for different (a) Learning rate \\$\\textbackslash\\{\\}alpha\\_\\{l\\_\\{1\\}\\}\\$ and(b) Discount factorγ. 18 VOLUME, ===== page\\_019\\_0\\_res.txt ===== between the CPU capacity and the average reward, indicating that as more computational power is allocated to local tasks,the system's performance improves. This trend is consistent across all agent configurations, althou"
      }
    ],
    "source_artifacts": [],
    "support_status": "unsupported",
    "title": "Accumulated reward time-course by learning rate and discount factor"
  },
  {
    "artifact_backed_reproduction_data": {
      "action_distribution_available": true
    },
    "caveats": [
      "Action distributions are artifact-backed, but reward sweeps and true HOODIE learned-agent curves are missing."
    ],
    "comparison_ready": false,
    "extracted_artifact_metrics": {
      "action_distribution_by_policy": [
        {
          "action_distribution": [
            {
              "action": "horizontal",
              "count": 2140
            },
            {
              "action": "local",
              "count": 20
            }
          ],
          "policy_name": "ADAPTIVE"
        },
        {
          "action_distribution": [
            {
              "action": "local",
              "count": 2180
            }
          ],
          "policy_name": "BCO"
        },
        {
          "action_distribution": [
            {
              "action": "local",
              "count": 2180
            }
          ],
          "policy_name": "FLC"
        },
        {
          "action_distribution": [
            {
              "action": "horizontal",
              "count": 2160
            }
          ],
          "policy_name": "HO"
        },
        {
          "action_distribution": [
            {
              "action": "local",
              "count": 2180
            }
          ],
          "policy_name": "MLEO"
        },
        {
          "action_distribution": [
            {
              "action": "compute_local",
              "count": 340
            },
            {
              "action": "horizontal",
              "count": 400
            },
            {
              "action": "local",
              "count": 380
            },
            {
              "action": "offload_horizontal",
              "count": 320
            },
            {
              "action": "offload_vertical",
              "count": 260
            },
            {
              "action": "vertical",
              "count": 480
            }
          ],
          "policy_name": "RO"
        },
        {
          "action_distribution": [
            {
              "action": "vertical",
              "count": 2160
            }
          ],
          "policy_name": "VO"
        }
      ]
    },
    "figure_id": "Figure 9",
    "missing_artifacts": [
      "average_reward_by_task_arrival_probability",
      "reward_by_drl_agent_count",
      "reward_by_cpu_capacity",
      "reward_by_agent_count_traffic_scenario",
      "reward_by_offloading_data_rate",
      "true_hoodie_drl_validation_rewards"
    ],
    "paper_caption_supported_metadata": {
      "subfigures": [
        "9a",
        "9b",
        "9c",
        "9d",
        "9e"
      ]
    },
    "paper_claim_type": "behavior_and_scalability_context",
    "paper_numeric_target_data": {
      "available": false,
      "missing": [
        "paper_numeric_curve_values"
      ]
    },
    "paper_ocr_evidence": [
      {
        "char_offset": 139277,
        "figure_id": "Figure 9",
        "snippet_index": 0,
        "source_path": "resources/papers/hoodie/ocr/merged.tex",
        "text": "parameters. 1) The impact of Task Arrival Probability Initially, to further explore the impact of the task arrival probability (P), which is directly proportional to the task traffic density underlying the IoT areas, Fig. 9a shows the HOODIE performance as a function of increasing system load and edge layer density \\$(N=[10,15,20])\\$ ). To assess the HOoDIE performance, we used the optimally trained Q models of each agent (as they resulted from Section A) and we calculated the average reward collected during a series of 200 validation episodes (i.e. all agents performed exploitative actions). Evidently, as the task arrival probability increases, the average reward decreases across all config"
      },
      {
        "char_offset": 141152,
        "figure_id": "Figure 9",
        "snippet_index": 1,
        "source_path": "resources/papers/hoodie/ocr/merged.tex",
        "text": "hat the high negative rewards do not reflect the average delay of the tasks, but they indicate the high negative penalties received for task drops, which is more frequent as the P increases. Under the same simulations, Fig. 9b depicts the distribution of actions taken by the HOoDIE agents across different task arrival probabilities, categorized into local computation,horizontal, and vertical offloading. The results show a clear preference for horizontal offloading, especially as the task arrival probability increases, suggesting that agents often opt to share tasks with neighboring EAs rather than process them locally or offload them to the Cloud. However, as the task arrival probability rea"
      }
    ],
    "source_artifacts": [
      "matrix/ADAPTIVE-extreme-1.json",
      "matrix/ADAPTIVE-extreme-2.json",
      "matrix/ADAPTIVE-extreme-3.json",
      "matrix/ADAPTIVE-extreme-4.json",
      "matrix/ADAPTIVE-extreme-5.json",
      "matrix/ADAPTIVE-heavy-1.json",
      "matrix/ADAPTIVE-heavy-2.json",
      "matrix/ADAPTIVE-heavy-3.json",
      "matrix/ADAPTIVE-heavy-4.json",
      "matrix/ADAPTIVE-heavy-5.json"
    ],
    "support_status": "partially_supported",
    "title": "HOODIE behavior insights under varying system parameters"
  },
  {
    "artifact_backed_reproduction_data": {
      "arrival_probabilities_from_traces": [
        "0.5",
        "0.7",
        "0.9"
      ],
      "matrix_metrics_available": true
    },
    "caveats": [
      "Repository average_delay values are preserved as stored; the paper states average delay is negative by convention."
    ],
    "comparison_ready": false,
    "extracted_artifact_metrics": {
      "by_policy": [
        {
          "completed_tasks": 408,
          "count": 20,
          "dropped_tasks": 1752,
          "key": "ADAPTIVE",
          "mean_average_delay": 11.192976190476191,
          "mean_drop_ratio": 0.8111111111111111,
          "total_tasks": 2160
        },
        {
          "completed_tasks": 428,
          "count": 20,
          "dropped_tasks": 1752,
          "key": "BCO",
          "mean_average_delay": 10.698268398268398,
          "mean_drop_ratio": 0.8036697247706426,
          "total_tasks": 2180
        },
        {
          "completed_tasks": 428,
          "count": 20,
          "dropped_tasks": 1752,
          "key": "FLC",
          "mean_average_delay": 10.698268398268398,
          "mean_drop_ratio": 0.8036697247706426,
          "total_tasks": 2180
        },
        {
          "completed_tasks": 408,
          "count": 20,
          "dropped_tasks": 1752,
          "key": "HO",
          "mean_average_delay": 11.242023809523808,
          "mean_drop_ratio": 0.8111111111111111,
          "total_tasks": 2160
        },
        {
          "completed_tasks": 428,
          "count": 20,
          "dropped_tasks": 1752,
          "key": "MLEO",
          "mean_average_delay": 10.698268398268398,
          "mean_drop_ratio": 0.8036697247706426,
          "total_tasks": 2180
        },
        {
          "completed_tasks": 408,
          "count": 20,
          "dropped_tasks": 1772,
          "key": "RO",
          "mean_average_delay": 10.996785714285714,
          "mean_drop_ratio": 0.8128440366972478,
          "total_tasks": 2180
        },
        {
          "completed_tasks": 408,
          "count": 20,
          "dropped_tasks": 1752,
          "key": "VO",
          "mean_average_delay": 11.242023809523808,
          "mean_drop_ratio": 0.8111111111111111,
          "total_tasks": 2160
        }
      ],
      "by_policy_scenario": [
        {
          "completed_tasks": 100,
          "count": 5,
          "dropped_tasks": 440,
          "key": "ADAPTIVE::extreme",
          "mean_average_delay": 11.309999999999999,
          "mean_drop_ratio": 0.8148148148148147,
          "total_tasks": 540
        },
        {
          "completed_tasks": 100,
          "count": 5,
          "dropped_tasks": 440,
          "key": "ADAPTIVE::heavy",
          "mean_average_delay": 11.1,
          "mean_drop_ratio": 0.8148148148148147,
          "total_tasks": 540
        },
        {
          "completed_tasks": 104,
          "count": 5,
          "dropped_tasks": 436,
          "key": "ADAPTIVE::moderate",
          "mean_average_delay": 11.18095238095238,
          "mean_drop_ratio": 0.8074074074074072,
          "total_tasks": 540
        },
        {
          "completed_tasks": 104,
          "count": 5,
          "dropped_tasks": 436,
          "key": "ADAPTIVE::paper_default",
          "mean_average_delay": 11.18095238095238,
          "mean_drop_ratio": 0.8074074074074072,
          "total_tasks": 540
        },
        {
          "completed_tasks": 105,
          "count": 5,
          "dropped_tasks": 440,
          "key": "BCO::extreme",
          "mean_average_delay": 10.81904761904762,
          "mean_drop_ratio": 0.8073394495412846,
          "total_tasks": 545
        },
        {
          "completed_tasks": 105,
          "count": 5,
          "dropped_tasks": 440,
          "key": "BCO::heavy",
          "mean_average_delay": 10.619047619047619,
          "mean_drop_ratio": 0.8073394495412846,
          "total_tasks": 545
        },
        {
          "completed_tasks": 109,
          "count": 5,
          "dropped_tasks": 436,
          "key": "BCO::moderate",
          "mean_average_delay": 10.677489177489178,
          "mean_drop_ratio": 0.7999999999999999,
          "total_tasks": 545
        },
        {
          "completed_tasks": 109,
          "count": 5,
          "dropped_tasks": 436,
          "key": "BCO::paper_default",
          "mean_average_delay": 10.677489177489178,
          "mean_drop_ratio": 0.7999999999999999,
          "total_tasks": 545
        },
        {
          "completed_tasks": 105,
          "count": 5,
          "dropped_tasks": 440,
          "key": "FLC::extreme",
          "mean_average_delay": 10.81904761904762,
          "mean_drop_ratio": 0.8073394495412846,
          "total_tasks": 545
        },
        {
          "completed_tasks": 105,
          "count": 5,
          "dropped_tasks": 440,
          "key": "FLC::heavy",
          "mean_average_delay": 10.619047619047619,
          "mean_drop_ratio": 0.8073394495412846,
          "total_tasks": 545
        },
        {
          "completed_tasks": 109,
          "count": 5,
          "dropped_tasks": 436,
          "key": "FLC::moderate",
          "mean_average_delay": 10.677489177489178,
          "mean_drop_ratio": 0.7999999999999999,
          "total_tasks": 545
        },
        {
          "completed_tasks": 109,
          "count": 5,
          "dropped_tasks": 436,
          "key": "FLC::paper_default",
          "mean_average_delay": 10.677489177489178,
          "mean_drop_ratio": 0.7999999999999999,
          "total_tasks": 545
        },
        {
          "completed_tasks": 100,
          "count": 5,
          "dropped_tasks": 440,
          "key": "HO::extreme",
          "mean_average_delay": 11.360000000000001,
          "mean_drop_ratio": 0.8148148148148147,
          "total_tasks": 540
        },
        {
          "completed_tasks": 100,
          "count": 5,
          "dropped_tasks": 440,
          "key": "HO::heavy",
          "mean_average_delay": 11.15,
          "mean_drop_ratio": 0.8148148148148147,
          "total_tasks": 540
        },
        {
          "completed_tasks": 104,
          "count": 5,
          "dropped_tasks": 436,
          "key": "HO::moderate",
          "mean_average_delay": 11.22904761904762,
          "mean_drop_ratio": 0.8074074074074072,
          "total_tasks": 540
        },
        {
          "completed_tasks": 104,
          "count": 5,
          "dropped_tasks": 436,
          "key": "HO::paper_default",
          "mean_average_delay": 11.22904761904762,
          "mean_drop_ratio": 0.8074074074074072,
          "total_tasks": 540
        },
        {
          "completed_tasks": 105,
          "count": 5,
          "dropped_tasks": 440,
          "key": "MLEO::extreme",
          "mean_average_delay": 10.81904761904762,
          "mean_drop_ratio": 0.8073394495412846,
          "total_tasks": 545
        },
        {
          "completed_tasks": 105,
          "count": 5,
          "dropped_tasks": 440,
          "key": "MLEO::heavy",
          "mean_average_delay": 10.619047619047619,
          "mean_drop_ratio": 0.8073394495412846,
          "total_tasks": 545
        },
        {
          "completed_tasks": 109,
          "count": 5,
          "dropped_tasks": 436,
          "key": "MLEO::moderate",
          "mean_average_delay": 10.677489177489178,
          "mean_drop_ratio": 0.7999999999999999,
          "total_tasks": 545
        },
        {
          "completed_tasks": 109,
          "count": 5,
          "dropped_tasks": 436,
          "key": "MLEO::paper_default",
          "mean_average_delay": 10.677489177489178,
          "mean_drop_ratio": 0.7999999999999999,
          "total_tasks": 545
        },
        {
          "completed_tasks": 100,
          "count": 5,
          "dropped_tasks": 445,
          "key": "RO::extreme",
          "mean_average_delay": 11.110000000000001,
          "mean_drop_ratio": 0.8165137614678899,
          "total_tasks": 545
        },
        {
          "completed_tasks": 100,
          "count": 5,
          "dropped_tasks": 445,
          "key": "RO::heavy",
          "mean_average_delay": 10.9,
          "mean_drop_ratio": 0.8165137614678899,
          "total_tasks": 545
        },
        {
          "completed_tasks": 104,
          "count": 5,
          "dropped_tasks": 441,
          "key": "RO::moderate",
          "mean_average_delay": 10.98857142857143,
          "mean_drop_ratio": 0.8091743119266056,
          "total_tasks": 545
        },
        {
          "completed_tasks": 104,
          "count": 5,
          "dropped_tasks": 441,
          "key": "RO::paper_default",
          "mean_average_delay": 10.98857142857143,
          "mean_drop_ratio": 0.8091743119266056,
          "total_tasks": 545
        },
        {
          "completed_tasks": 100,
          "count": 5,
          "dropped_tasks": 440,
          "key": "VO::extreme",
          "mean_average_delay": 11.360000000000001,
          "mean_drop_ratio": 0.8148148148148147,
          "total_tasks": 540
        },
        {
          "completed_tasks": 100,
          "count": 5,
          "dropped_tasks": 440,
          "key": "VO::heavy",
          "mean_average_delay": 11.15,
          "mean_drop_ratio": 0.8148148148148147,
          "total_tasks": 540
        },
        {
          "completed_tasks": 104,
          "count": 5,
          "dropped_tasks": 436,
          "key": "VO::moderate",
          "mean_average_delay": 11.22904761904762,
          "mean_drop_ratio": 0.8074074074074072,
          "total_tasks": 540
        },
        {
          "completed_tasks": 104,
          "count": 5,
          "dropped_tasks": 436,
          "key": "VO::paper_default",
          "mean_average_delay": 11.22904761904762,
          "mean_drop_ratio": 0.8074074074074072,
          "total_tasks": 540
        }
      ],
      "by_scenario": [
        {
          "completed_tasks": 715,
          "count": 35,
          "dropped_tasks": 3085,
          "key": "extreme",
          "mean_average_delay": 11.085306122448978,
          "mean_drop_ratio": 0.8118537935051693,
          "total_tasks": 3800
        },
        {
          "completed_tasks": 715,
          "count": 35,
          "dropped_tasks": 3085,
          "key": "heavy",
          "mean_average_delay": 10.879591836734694,
          "mean_drop_ratio": 0.8118537935051693,
          "total_tasks": 3800
        },
        {
          "completed_tasks": 743,
          "count": 35,
          "dropped_tasks": 3057,
          "key": "moderate",
          "mean_average_delay": 10.95144094001237,
          "mean_drop_ratio": 0.8044852191641183,
          "total_tasks": 3800
        },
        {
          "completed_tasks": 743,
          "count": 35,
          "dropped_tasks": 3057,
          "key": "paper_default",
          "mean_average_delay": 10.95144094001237,
          "mean_drop_ratio": 0.8044852191641183,
          "total_tasks": 3800
        }
      ],
      "by_seed": [
        {
          "completed_tasks": 572,
          "count": 28,
          "dropped_tasks": 2468,
          "key": "1",
          "mean_average_delay": 10.879591836734695,
          "mean_drop_ratio": 0.8118537935051693,
          "total_tasks": 3040
        },
        {
          "completed_tasks": 586,
          "count": 28,
          "dropped_tasks": 2454,
          "key": "2",
          "mean_average_delay": 10.955967841682128,
          "mean_drop_ratio": 0.8072484345420126,
          "total_tasks": 3040
        },
        {
          "completed_tasks": 586,
          "count": 28,
          "dropped_tasks": 2454,
          "key": "3",
          "mean_average_delay": 11.04053803339517,
          "mean_drop_ratio": 0.8072484345420126,
          "total_tasks": 3040
        },
        {
          "completed_tasks": 586,
          "count": 28,
          "dropped_tasks": 2454,
          "key": "4",
          "mean_average_delay": 11.073840445269017,
          "mean_drop_ratio": 0.8072484345420126,
          "total_tasks": 3040
        },
        {
          "completed_tasks": 586,
          "count": 28,
          "dropped_tasks": 2454,
          "key": "5",
          "mean_average_delay": 10.884786641929503,
          "mean_drop_ratio": 0.8072484345420126,
          "total_tasks": 3040
        }
      ],
      "per_run": [
        {
          "average_delay": 11.35,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "ADAPTIVE",
          "scenario_name": "extreme",
          "seed": 1,
          "total_tasks": 108
        },
        {
          "average_delay": 11.25,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "ADAPTIVE",
          "scenario_name": "extreme",
          "seed": 2,
          "total_tasks": 108
        },
        {
          "average_delay": 11.4,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "ADAPTIVE",
          "scenario_name": "extreme",
          "seed": 3,
          "total_tasks": 108
        },
        {
          "average_delay": 11.35,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "ADAPTIVE",
          "scenario_name": "extreme",
          "seed": 4,
          "total_tasks": 108
        },
        {
          "average_delay": 11.2,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "ADAPTIVE",
          "scenario_name": "extreme",
          "seed": 5,
          "total_tasks": 108
        },
        {
          "average_delay": 11.05,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "ADAPTIVE",
          "scenario_name": "heavy",
          "seed": 1,
          "total_tasks": 108
        },
        {
          "average_delay": 11.1,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "ADAPTIVE",
          "scenario_name": "heavy",
          "seed": 2,
          "total_tasks": 108
        },
        {
          "average_delay": 11.2,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "ADAPTIVE",
          "scenario_name": "heavy",
          "seed": 3,
          "total_tasks": 108
        },
        {
          "average_delay": 11.1,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "ADAPTIVE",
          "scenario_name": "heavy",
          "seed": 4,
          "total_tasks": 108
        },
        {
          "average_delay": 11.05,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "ADAPTIVE",
          "scenario_name": "heavy",
          "seed": 5,
          "total_tasks": 108
        },
        {
          "average_delay": 11.0,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "ADAPTIVE",
          "scenario_name": "moderate",
          "seed": 1,
          "total_tasks": 108
        },
        {
          "average_delay": 11.19047619047619,
          "completed_tasks": 21,
          "drop_ratio": 0.8055555555555556,
          "dropped_tasks": 87,
          "policy_name": "ADAPTIVE",
          "scenario_name": "moderate",
          "seed": 2,
          "total_tasks": 108
        },
        {
          "average_delay": 11.238095238095237,
          "completed_tasks": 21,
          "drop_ratio": 0.8055555555555556,
          "dropped_tasks": 87,
          "policy_name": "ADAPTIVE",
          "scenario_name": "moderate",
          "seed": 3,
          "total_tasks": 108
        },
        {
          "average_delay": 11.380952380952381,
          "completed_tasks": 21,
          "drop_ratio": 0.8055555555555556,
          "dropped_tasks": 87,
          "policy_name": "ADAPTIVE",
          "scenario_name": "moderate",
          "seed": 4,
          "total_tasks": 108
        },
        {
          "average_delay": 11.095238095238095,
          "completed_tasks": 21,
          "drop_ratio": 0.8055555555555556,
          "dropped_tasks": 87,
          "policy_name": "ADAPTIVE",
          "scenario_name": "moderate",
          "seed": 5,
          "total_tasks": 108
        },
        {
          "average_delay": 11.0,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "ADAPTIVE",
          "scenario_name": "paper_default",
          "seed": 1,
          "total_tasks": 108
        },
        {
          "average_delay": 11.19047619047619,
          "completed_tasks": 21,
          "drop_ratio": 0.8055555555555556,
          "dropped_tasks": 87,
          "policy_name": "ADAPTIVE",
          "scenario_name": "paper_default",
          "seed": 2,
          "total_tasks": 108
        },
        {
          "average_delay": 11.238095238095237,
          "completed_tasks": 21,
          "drop_ratio": 0.8055555555555556,
          "dropped_tasks": 87,
          "policy_name": "ADAPTIVE",
          "scenario_name": "paper_default",
          "seed": 3,
          "total_tasks": 108
        },
        {
          "average_delay": 11.380952380952381,
          "completed_tasks": 21,
          "drop_ratio": 0.8055555555555556,
          "dropped_tasks": 87,
          "policy_name": "ADAPTIVE",
          "scenario_name": "paper_default",
          "seed": 4,
          "total_tasks": 108
        },
        {
          "average_delay": 11.095238095238095,
          "completed_tasks": 21,
          "drop_ratio": 0.8055555555555556,
          "dropped_tasks": 87,
          "policy_name": "ADAPTIVE",
          "scenario_name": "paper_default",
          "seed": 5,
          "total_tasks": 108
        },
        {
          "average_delay": 10.857142857142858,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "BCO",
          "scenario_name": "extreme",
          "seed": 1,
          "total_tasks": 109
        },
        {
          "average_delay": 10.761904761904763,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "BCO",
          "scenario_name": "extreme",
          "seed": 2,
          "total_tasks": 109
        },
        {
          "average_delay": 10.904761904761905,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "BCO",
          "scenario_name": "extreme",
          "seed": 3,
          "total_tasks": 109
        },
        {
          "average_delay": 10.857142857142858,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "BCO",
          "scenario_name": "extreme",
          "seed": 4,
          "total_tasks": 109
        },
        {
          "average_delay": 10.714285714285714,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "BCO",
          "scenario_name": "extreme",
          "seed": 5,
          "total_tasks": 109
        },
        {
          "average_delay": 10.571428571428571,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "BCO",
          "scenario_name": "heavy",
          "seed": 1,
          "total_tasks": 109
        },
        {
          "average_delay": 10.619047619047619,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "BCO",
          "scenario_name": "heavy",
          "seed": 2,
          "total_tasks": 109
        },
        {
          "average_delay": 10.714285714285714,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "BCO",
          "scenario_name": "heavy",
          "seed": 3,
          "total_tasks": 109
        },
        {
          "average_delay": 10.619047619047619,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "BCO",
          "scenario_name": "heavy",
          "seed": 4,
          "total_tasks": 109
        },
        {
          "average_delay": 10.571428571428571,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "BCO",
          "scenario_name": "heavy",
          "seed": 5,
          "total_tasks": 109
        },
        {
          "average_delay": 10.523809523809524,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "BCO",
          "scenario_name": "moderate",
          "seed": 1,
          "total_tasks": 109
        },
        {
          "average_delay": 10.681818181818182,
          "completed_tasks": 22,
          "drop_ratio": 0.7981651376146789,
          "dropped_tasks": 87,
          "policy_name": "BCO",
          "scenario_name": "moderate",
          "seed": 2,
          "total_tasks": 109
        },
        {
          "average_delay": 10.727272727272727,
          "completed_tasks": 22,
          "drop_ratio": 0.7981651376146789,
          "dropped_tasks": 87,
          "policy_name": "BCO",
          "scenario_name": "moderate",
          "seed": 3,
          "total_tasks": 109
        },
        {
          "average_delay": 10.863636363636363,
          "completed_tasks": 22,
          "drop_ratio": 0.7981651376146789,
          "dropped_tasks": 87,
          "policy_name": "BCO",
          "scenario_name": "moderate",
          "seed": 4,
          "total_tasks": 109
        },
        {
          "average_delay": 10.590909090909092,
          "completed_tasks": 22,
          "drop_ratio": 0.7981651376146789,
          "dropped_tasks": 87,
          "policy_name": "BCO",
          "scenario_name": "moderate",
          "seed": 5,
          "total_tasks": 109
        },
        {
          "average_delay": 10.523809523809524,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "BCO",
          "scenario_name": "paper_default",
          "seed": 1,
          "total_tasks": 109
        },
        {
          "average_delay": 10.681818181818182,
          "completed_tasks": 22,
          "drop_ratio": 0.7981651376146789,
          "dropped_tasks": 87,
          "policy_name": "BCO",
          "scenario_name": "paper_default",
          "seed": 2,
          "total_tasks": 109
        },
        {
          "average_delay": 10.727272727272727,
          "completed_tasks": 22,
          "drop_ratio": 0.7981651376146789,
          "dropped_tasks": 87,
          "policy_name": "BCO",
          "scenario_name": "paper_default",
          "seed": 3,
          "total_tasks": 109
        },
        {
          "average_delay": 10.863636363636363,
          "completed_tasks": 22,
          "drop_ratio": 0.7981651376146789,
          "dropped_tasks": 87,
          "policy_name": "BCO",
          "scenario_name": "paper_default",
          "seed": 4,
          "total_tasks": 109
        },
        {
          "average_delay": 10.590909090909092,
          "completed_tasks": 22,
          "drop_ratio": 0.7981651376146789,
          "dropped_tasks": 87,
          "policy_name": "BCO",
          "scenario_name": "paper_default",
          "seed": 5,
          "total_tasks": 109
        },
        {
          "average_delay": 10.857142857142858,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "FLC",
          "scenario_name": "extreme",
          "seed": 1,
          "total_tasks": 109
        },
        {
          "average_delay": 10.761904761904763,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "FLC",
          "scenario_name": "extreme",
          "seed": 2,
          "total_tasks": 109
        },
        {
          "average_delay": 10.904761904761905,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "FLC",
          "scenario_name": "extreme",
          "seed": 3,
          "total_tasks": 109
        },
        {
          "average_delay": 10.857142857142858,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "FLC",
          "scenario_name": "extreme",
          "seed": 4,
          "total_tasks": 109
        },
        {
          "average_delay": 10.714285714285714,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "FLC",
          "scenario_name": "extreme",
          "seed": 5,
          "total_tasks": 109
        },
        {
          "average_delay": 10.571428571428571,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "FLC",
          "scenario_name": "heavy",
          "seed": 1,
          "total_tasks": 109
        },
        {
          "average_delay": 10.619047619047619,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "FLC",
          "scenario_name": "heavy",
          "seed": 2,
          "total_tasks": 109
        },
        {
          "average_delay": 10.714285714285714,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "FLC",
          "scenario_name": "heavy",
          "seed": 3,
          "total_tasks": 109
        },
        {
          "average_delay": 10.619047619047619,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "FLC",
          "scenario_name": "heavy",
          "seed": 4,
          "total_tasks": 109
        },
        {
          "average_delay": 10.571428571428571,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "FLC",
          "scenario_name": "heavy",
          "seed": 5,
          "total_tasks": 109
        },
        {
          "average_delay": 10.523809523809524,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "FLC",
          "scenario_name": "moderate",
          "seed": 1,
          "total_tasks": 109
        },
        {
          "average_delay": 10.681818181818182,
          "completed_tasks": 22,
          "drop_ratio": 0.7981651376146789,
          "dropped_tasks": 87,
          "policy_name": "FLC",
          "scenario_name": "moderate",
          "seed": 2,
          "total_tasks": 109
        },
        {
          "average_delay": 10.727272727272727,
          "completed_tasks": 22,
          "drop_ratio": 0.7981651376146789,
          "dropped_tasks": 87,
          "policy_name": "FLC",
          "scenario_name": "moderate",
          "seed": 3,
          "total_tasks": 109
        },
        {
          "average_delay": 10.863636363636363,
          "completed_tasks": 22,
          "drop_ratio": 0.7981651376146789,
          "dropped_tasks": 87,
          "policy_name": "FLC",
          "scenario_name": "moderate",
          "seed": 4,
          "total_tasks": 109
        },
        {
          "average_delay": 10.590909090909092,
          "completed_tasks": 22,
          "drop_ratio": 0.7981651376146789,
          "dropped_tasks": 87,
          "policy_name": "FLC",
          "scenario_name": "moderate",
          "seed": 5,
          "total_tasks": 109
        },
        {
          "average_delay": 10.523809523809524,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "FLC",
          "scenario_name": "paper_default",
          "seed": 1,
          "total_tasks": 109
        },
        {
          "average_delay": 10.681818181818182,
          "completed_tasks": 22,
          "drop_ratio": 0.7981651376146789,
          "dropped_tasks": 87,
          "policy_name": "FLC",
          "scenario_name": "paper_default",
          "seed": 2,
          "total_tasks": 109
        },
        {
          "average_delay": 10.727272727272727,
          "completed_tasks": 22,
          "drop_ratio": 0.7981651376146789,
          "dropped_tasks": 87,
          "policy_name": "FLC",
          "scenario_name": "paper_default",
          "seed": 3,
          "total_tasks": 109
        },
        {
          "average_delay": 10.863636363636363,
          "completed_tasks": 22,
          "drop_ratio": 0.7981651376146789,
          "dropped_tasks": 87,
          "policy_name": "FLC",
          "scenario_name": "paper_default",
          "seed": 4,
          "total_tasks": 109
        },
        {
          "average_delay": 10.590909090909092,
          "completed_tasks": 22,
          "drop_ratio": 0.7981651376146789,
          "dropped_tasks": 87,
          "policy_name": "FLC",
          "scenario_name": "paper_default",
          "seed": 5,
          "total_tasks": 109
        },
        {
          "average_delay": 11.4,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "HO",
          "scenario_name": "extreme",
          "seed": 1,
          "total_tasks": 108
        },
        {
          "average_delay": 11.3,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "HO",
          "scenario_name": "extreme",
          "seed": 2,
          "total_tasks": 108
        },
        {
          "average_delay": 11.45,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "HO",
          "scenario_name": "extreme",
          "seed": 3,
          "total_tasks": 108
        },
        {
          "average_delay": 11.4,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "HO",
          "scenario_name": "extreme",
          "seed": 4,
          "total_tasks": 108
        },
        {
          "average_delay": 11.25,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "HO",
          "scenario_name": "extreme",
          "seed": 5,
          "total_tasks": 108
        },
        {
          "average_delay": 11.1,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "HO",
          "scenario_name": "heavy",
          "seed": 1,
          "total_tasks": 108
        },
        {
          "average_delay": 11.15,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "HO",
          "scenario_name": "heavy",
          "seed": 2,
          "total_tasks": 108
        },
        {
          "average_delay": 11.25,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "HO",
          "scenario_name": "heavy",
          "seed": 3,
          "total_tasks": 108
        },
        {
          "average_delay": 11.15,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "HO",
          "scenario_name": "heavy",
          "seed": 4,
          "total_tasks": 108
        },
        {
          "average_delay": 11.1,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "HO",
          "scenario_name": "heavy",
          "seed": 5,
          "total_tasks": 108
        },
        {
          "average_delay": 11.05,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "HO",
          "scenario_name": "moderate",
          "seed": 1,
          "total_tasks": 108
        },
        {
          "average_delay": 11.238095238095237,
          "completed_tasks": 21,
          "drop_ratio": 0.8055555555555556,
          "dropped_tasks": 87,
          "policy_name": "HO",
          "scenario_name": "moderate",
          "seed": 2,
          "total_tasks": 108
        },
        {
          "average_delay": 11.285714285714286,
          "completed_tasks": 21,
          "drop_ratio": 0.8055555555555556,
          "dropped_tasks": 87,
          "policy_name": "HO",
          "scenario_name": "moderate",
          "seed": 3,
          "total_tasks": 108
        },
        {
          "average_delay": 11.428571428571429,
          "completed_tasks": 21,
          "drop_ratio": 0.8055555555555556,
          "dropped_tasks": 87,
          "policy_name": "HO",
          "scenario_name": "moderate",
          "seed": 4,
          "total_tasks": 108
        },
        {
          "average_delay": 11.142857142857142,
          "completed_tasks": 21,
          "drop_ratio": 0.8055555555555556,
          "dropped_tasks": 87,
          "policy_name": "HO",
          "scenario_name": "moderate",
          "seed": 5,
          "total_tasks": 108
        },
        {
          "average_delay": 11.05,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "HO",
          "scenario_name": "paper_default",
          "seed": 1,
          "total_tasks": 108
        },
        {
          "average_delay": 11.238095238095237,
          "completed_tasks": 21,
          "drop_ratio": 0.8055555555555556,
          "dropped_tasks": 87,
          "policy_name": "HO",
          "scenario_name": "paper_default",
          "seed": 2,
          "total_tasks": 108
        },
        {
          "average_delay": 11.285714285714286,
          "completed_tasks": 21,
          "drop_ratio": 0.8055555555555556,
          "dropped_tasks": 87,
          "policy_name": "HO",
          "scenario_name": "paper_default",
          "seed": 3,
          "total_tasks": 108
        },
        {
          "average_delay": 11.428571428571429,
          "completed_tasks": 21,
          "drop_ratio": 0.8055555555555556,
          "dropped_tasks": 87,
          "policy_name": "HO",
          "scenario_name": "paper_default",
          "seed": 4,
          "total_tasks": 108
        },
        {
          "average_delay": 11.142857142857142,
          "completed_tasks": 21,
          "drop_ratio": 0.8055555555555556,
          "dropped_tasks": 87,
          "policy_name": "HO",
          "scenario_name": "paper_default",
          "seed": 5,
          "total_tasks": 108
        },
        {
          "average_delay": 10.857142857142858,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "MLEO",
          "scenario_name": "extreme",
          "seed": 1,
          "total_tasks": 109
        },
        {
          "average_delay": 10.761904761904763,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "MLEO",
          "scenario_name": "extreme",
          "seed": 2,
          "total_tasks": 109
        },
        {
          "average_delay": 10.904761904761905,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "MLEO",
          "scenario_name": "extreme",
          "seed": 3,
          "total_tasks": 109
        },
        {
          "average_delay": 10.857142857142858,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "MLEO",
          "scenario_name": "extreme",
          "seed": 4,
          "total_tasks": 109
        },
        {
          "average_delay": 10.714285714285714,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "MLEO",
          "scenario_name": "extreme",
          "seed": 5,
          "total_tasks": 109
        },
        {
          "average_delay": 10.571428571428571,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "MLEO",
          "scenario_name": "heavy",
          "seed": 1,
          "total_tasks": 109
        },
        {
          "average_delay": 10.619047619047619,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "MLEO",
          "scenario_name": "heavy",
          "seed": 2,
          "total_tasks": 109
        },
        {
          "average_delay": 10.714285714285714,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "MLEO",
          "scenario_name": "heavy",
          "seed": 3,
          "total_tasks": 109
        },
        {
          "average_delay": 10.619047619047619,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "MLEO",
          "scenario_name": "heavy",
          "seed": 4,
          "total_tasks": 109
        },
        {
          "average_delay": 10.571428571428571,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "MLEO",
          "scenario_name": "heavy",
          "seed": 5,
          "total_tasks": 109
        },
        {
          "average_delay": 10.523809523809524,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "MLEO",
          "scenario_name": "moderate",
          "seed": 1,
          "total_tasks": 109
        },
        {
          "average_delay": 10.681818181818182,
          "completed_tasks": 22,
          "drop_ratio": 0.7981651376146789,
          "dropped_tasks": 87,
          "policy_name": "MLEO",
          "scenario_name": "moderate",
          "seed": 2,
          "total_tasks": 109
        },
        {
          "average_delay": 10.727272727272727,
          "completed_tasks": 22,
          "drop_ratio": 0.7981651376146789,
          "dropped_tasks": 87,
          "policy_name": "MLEO",
          "scenario_name": "moderate",
          "seed": 3,
          "total_tasks": 109
        },
        {
          "average_delay": 10.863636363636363,
          "completed_tasks": 22,
          "drop_ratio": 0.7981651376146789,
          "dropped_tasks": 87,
          "policy_name": "MLEO",
          "scenario_name": "moderate",
          "seed": 4,
          "total_tasks": 109
        },
        {
          "average_delay": 10.590909090909092,
          "completed_tasks": 22,
          "drop_ratio": 0.7981651376146789,
          "dropped_tasks": 87,
          "policy_name": "MLEO",
          "scenario_name": "moderate",
          "seed": 5,
          "total_tasks": 109
        },
        {
          "average_delay": 10.523809523809524,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "MLEO",
          "scenario_name": "paper_default",
          "seed": 1,
          "total_tasks": 109
        },
        {
          "average_delay": 10.681818181818182,
          "completed_tasks": 22,
          "drop_ratio": 0.7981651376146789,
          "dropped_tasks": 87,
          "policy_name": "MLEO",
          "scenario_name": "paper_default",
          "seed": 2,
          "total_tasks": 109
        },
        {
          "average_delay": 10.727272727272727,
          "completed_tasks": 22,
          "drop_ratio": 0.7981651376146789,
          "dropped_tasks": 87,
          "policy_name": "MLEO",
          "scenario_name": "paper_default",
          "seed": 3,
          "total_tasks": 109
        },
        {
          "average_delay": 10.863636363636363,
          "completed_tasks": 22,
          "drop_ratio": 0.7981651376146789,
          "dropped_tasks": 87,
          "policy_name": "MLEO",
          "scenario_name": "paper_default",
          "seed": 4,
          "total_tasks": 109
        },
        {
          "average_delay": 10.590909090909092,
          "completed_tasks": 22,
          "drop_ratio": 0.7981651376146789,
          "dropped_tasks": 87,
          "policy_name": "MLEO",
          "scenario_name": "paper_default",
          "seed": 5,
          "total_tasks": 109
        },
        {
          "average_delay": 11.15,
          "completed_tasks": 20,
          "drop_ratio": 0.8165137614678899,
          "dropped_tasks": 89,
          "policy_name": "RO",
          "scenario_name": "extreme",
          "seed": 1,
          "total_tasks": 109
        },
        {
          "average_delay": 11.05,
          "completed_tasks": 20,
          "drop_ratio": 0.8165137614678899,
          "dropped_tasks": 89,
          "policy_name": "RO",
          "scenario_name": "extreme",
          "seed": 2,
          "total_tasks": 109
        },
        {
          "average_delay": 11.2,
          "completed_tasks": 20,
          "drop_ratio": 0.8165137614678899,
          "dropped_tasks": 89,
          "policy_name": "RO",
          "scenario_name": "extreme",
          "seed": 3,
          "total_tasks": 109
        },
        {
          "average_delay": 11.15,
          "completed_tasks": 20,
          "drop_ratio": 0.8165137614678899,
          "dropped_tasks": 89,
          "policy_name": "RO",
          "scenario_name": "extreme",
          "seed": 4,
          "total_tasks": 109
        },
        {
          "average_delay": 11.0,
          "completed_tasks": 20,
          "drop_ratio": 0.8165137614678899,
          "dropped_tasks": 89,
          "policy_name": "RO",
          "scenario_name": "extreme",
          "seed": 5,
          "total_tasks": 109
        },
        {
          "average_delay": 10.85,
          "completed_tasks": 20,
          "drop_ratio": 0.8165137614678899,
          "dropped_tasks": 89,
          "policy_name": "RO",
          "scenario_name": "heavy",
          "seed": 1,
          "total_tasks": 109
        },
        {
          "average_delay": 10.9,
          "completed_tasks": 20,
          "drop_ratio": 0.8165137614678899,
          "dropped_tasks": 89,
          "policy_name": "RO",
          "scenario_name": "heavy",
          "seed": 2,
          "total_tasks": 109
        },
        {
          "average_delay": 11.0,
          "completed_tasks": 20,
          "drop_ratio": 0.8165137614678899,
          "dropped_tasks": 89,
          "policy_name": "RO",
          "scenario_name": "heavy",
          "seed": 3,
          "total_tasks": 109
        },
        {
          "average_delay": 10.9,
          "completed_tasks": 20,
          "drop_ratio": 0.8165137614678899,
          "dropped_tasks": 89,
          "policy_name": "RO",
          "scenario_name": "heavy",
          "seed": 4,
          "total_tasks": 109
        },
        {
          "average_delay": 10.85,
          "completed_tasks": 20,
          "drop_ratio": 0.8165137614678899,
          "dropped_tasks": 89,
          "policy_name": "RO",
          "scenario_name": "heavy",
          "seed": 5,
          "total_tasks": 109
        },
        {
          "average_delay": 10.8,
          "completed_tasks": 20,
          "drop_ratio": 0.8165137614678899,
          "dropped_tasks": 89,
          "policy_name": "RO",
          "scenario_name": "moderate",
          "seed": 1,
          "total_tasks": 109
        },
        {
          "average_delay": 11.0,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "RO",
          "scenario_name": "moderate",
          "seed": 2,
          "total_tasks": 109
        },
        {
          "average_delay": 11.047619047619047,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "RO",
          "scenario_name": "moderate",
          "seed": 3,
          "total_tasks": 109
        },
        {
          "average_delay": 11.19047619047619,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "RO",
          "scenario_name": "moderate",
          "seed": 4,
          "total_tasks": 109
        },
        {
          "average_delay": 10.904761904761905,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "RO",
          "scenario_name": "moderate",
          "seed": 5,
          "total_tasks": 109
        },
        {
          "average_delay": 10.8,
          "completed_tasks": 20,
          "drop_ratio": 0.8165137614678899,
          "dropped_tasks": 89,
          "policy_name": "RO",
          "scenario_name": "paper_default",
          "seed": 1,
          "total_tasks": 109
        },
        {
          "average_delay": 11.0,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "RO",
          "scenario_name": "paper_default",
          "seed": 2,
          "total_tasks": 109
        },
        {
          "average_delay": 11.047619047619047,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "RO",
          "scenario_name": "paper_default",
          "seed": 3,
          "total_tasks": 109
        },
        {
          "average_delay": 11.19047619047619,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "RO",
          "scenario_name": "paper_default",
          "seed": 4,
          "total_tasks": 109
        },
        {
          "average_delay": 10.904761904761905,
          "completed_tasks": 21,
          "drop_ratio": 0.8073394495412844,
          "dropped_tasks": 88,
          "policy_name": "RO",
          "scenario_name": "paper_default",
          "seed": 5,
          "total_tasks": 109
        },
        {
          "average_delay": 11.4,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "VO",
          "scenario_name": "extreme",
          "seed": 1,
          "total_tasks": 108
        },
        {
          "average_delay": 11.3,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "VO",
          "scenario_name": "extreme",
          "seed": 2,
          "total_tasks": 108
        },
        {
          "average_delay": 11.45,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "VO",
          "scenario_name": "extreme",
          "seed": 3,
          "total_tasks": 108
        },
        {
          "average_delay": 11.4,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "VO",
          "scenario_name": "extreme",
          "seed": 4,
          "total_tasks": 108
        },
        {
          "average_delay": 11.25,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "VO",
          "scenario_name": "extreme",
          "seed": 5,
          "total_tasks": 108
        },
        {
          "average_delay": 11.1,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "VO",
          "scenario_name": "heavy",
          "seed": 1,
          "total_tasks": 108
        },
        {
          "average_delay": 11.15,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "VO",
          "scenario_name": "heavy",
          "seed": 2,
          "total_tasks": 108
        },
        {
          "average_delay": 11.25,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "VO",
          "scenario_name": "heavy",
          "seed": 3,
          "total_tasks": 108
        },
        {
          "average_delay": 11.15,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "VO",
          "scenario_name": "heavy",
          "seed": 4,
          "total_tasks": 108
        },
        {
          "average_delay": 11.1,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "VO",
          "scenario_name": "heavy",
          "seed": 5,
          "total_tasks": 108
        },
        {
          "average_delay": 11.05,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "VO",
          "scenario_name": "moderate",
          "seed": 1,
          "total_tasks": 108
        },
        {
          "average_delay": 11.238095238095237,
          "completed_tasks": 21,
          "drop_ratio": 0.8055555555555556,
          "dropped_tasks": 87,
          "policy_name": "VO",
          "scenario_name": "moderate",
          "seed": 2,
          "total_tasks": 108
        },
        {
          "average_delay": 11.285714285714286,
          "completed_tasks": 21,
          "drop_ratio": 0.8055555555555556,
          "dropped_tasks": 87,
          "policy_name": "VO",
          "scenario_name": "moderate",
          "seed": 3,
          "total_tasks": 108
        },
        {
          "average_delay": 11.428571428571429,
          "completed_tasks": 21,
          "drop_ratio": 0.8055555555555556,
          "dropped_tasks": 87,
          "policy_name": "VO",
          "scenario_name": "moderate",
          "seed": 4,
          "total_tasks": 108
        },
        {
          "average_delay": 11.142857142857142,
          "completed_tasks": 21,
          "drop_ratio": 0.8055555555555556,
          "dropped_tasks": 87,
          "policy_name": "VO",
          "scenario_name": "moderate",
          "seed": 5,
          "total_tasks": 108
        },
        {
          "average_delay": 11.05,
          "completed_tasks": 20,
          "drop_ratio": 0.8148148148148148,
          "dropped_tasks": 88,
          "policy_name": "VO",
          "scenario_name": "paper_default",
          "seed": 1,
          "total_tasks": 108
        },
        {
          "average_delay": 11.238095238095237,
          "completed_tasks": 21,
          "drop_ratio": 0.8055555555555556,
          "dropped_tasks": 87,
          "policy_name": "VO",
          "scenario_name": "paper_default",
          "seed": 2,
          "total_tasks": 108
        },
        {
          "average_delay": 11.285714285714286,
          "completed_tasks": 21,
          "drop_ratio": 0.8055555555555556,
          "dropped_tasks": 87,
          "policy_name": "VO",
          "scenario_name": "paper_default",
          "seed": 3,
          "total_tasks": 108
        },
        {
          "average_delay": 11.428571428571429,
          "completed_tasks": 21,
          "drop_ratio": 0.8055555555555556,
          "dropped_tasks": 87,
          "policy_name": "VO",
          "scenario_name": "paper_default",
          "seed": 4,
          "total_tasks": 108
        },
        {
          "average_delay": 11.142857142857142,
          "completed_tasks": 21,
          "drop_ratio": 0.8055555555555556,
          "dropped_tasks": 87,
          "policy_name": "VO",
          "scenario_name": "paper_default",
          "seed": 5,
          "total_tasks": 108
        }
      ]
    },
    "figure_id": "Figure 10",
    "missing_artifacts": [
      "cpu_capacity_sweep_artifacts",
      "timeout_sweep_artifacts",
      "structured_paper_numeric_curve_values"
    ],
    "paper_caption_supported_metadata": {
      "metrics": [
        "average_delay",
        "drop_ratio"
      ],
      "paper_delay_convention": "negative"
    },
    "paper_claim_type": "baseline_metric_comparison",
    "paper_numeric_target_data": {
      "available": false,
      "missing": [
        "structured_paper_numeric_curve_values"
      ]
    },
    "paper_ocr_evidence": [
      {
        "char_offset": 155096,
        "figure_id": "Figure 10",
        "snippet_index": 0,
        "source_path": "resources/papers/hoodie/ocr/merged.tex",
        "text": "f the task dropped, divided by the total number of tasks arrived in all EAs. By convention, delay values are negative,since they reflect negative impact on the task completion. 1)The impact of Task Arrival Probability Fig. 10a presents the average delay as a function of the task arrival probability across different offloading schemes.As the task arrival probability increases, the average delay generally decreases for all schemes, reflecting the growing challenge of handling a higher load within the system's limited computational resources. Notably, HOoDIE consistently outperforms the other schemes, achieving lower average delays across the entire range of task arrival probabilities.The HO an"
      },
      {
        "char_offset": 155868,
        "figure_id": "Figure 10",
        "snippet_index": 1,
        "source_path": "resources/papers/hoodie/ocr/merged.tex",
        "text": "w significantly higher delays as the load increases. The MLEO scheme also demonstrates strong performance, particularly at moderate task loads, but it falls behind HOoDIE as the task arrival probability approaches 0.9. Fig. 10d illustrates the drop ratio as a function of task arrival probability for the same set of offloading schemes.As expected, the drop ratio increases with higher task arrival probabilities, reflecting the system's difficulty in meeting task deadlines under heavier loads. HOoDIE demonstrates the lowest drop ratios across the board, indicating its effectiveness in preventing task drops even as the system becomes increasingly burdened. The FLC and HO schemes,in contrast, exh"
      },
      {
        "char_offset": 156872,
        "figure_id": "Figure 10",
        "snippet_index": 2,
        "source_path": "resources/papers/hoodie/ocr/merged.tex",
        "text": "lts may highlight the HOODIE superior ability to minimize task computation delays and drop rates by dynamically adjusting offloading decisions based on current system conditions. 2)The impact of Computational Capacity Fig. 10b illustrates the average delay as a function of CPU computation capacity dedicated to local tasks across different offloading schemes. As the CPU capacity increases from \\$3\\textbackslash\\{\\}mathrm\\{\\textasciitilde{}-\\textasciitilde{}\\}7\\$ GHz, most schemes show a reduction in average delay, highlighting the importance of local computational Task | Metric | Metric | 3 | 4 | 5 | 6 | 7 (a) | Average Delay (sec) | RO | -0.05 | -0.05 | -0.05 | -0.05 | | | FLC | 0.0 | -0.05 "
      },
      {
        "char_offset": 159684,
        "figure_id": "Figure 10",
        "snippet_index": 3,
        "source_path": "resources/papers/hoodie/ocr/merged.tex",
        "text": "tation and offloading decisions. The MLEO scheme also performs well, but its delay reduction is less pronounced compared to HOODIE, particularly at lower CPU capacities, where offloading decisions become more critical. Fig. 10e shows the drop ratio as a function of CPU computation capacity for the same set of offloading schemes.As expected, higher CPU capacities lead to a reduction in drop ratios across most schemes, as more tasks can be processed locally, reducing the likelihood of tasks being dropped due to deadline violations. HOODIE demonstrates the most significant reduction in drop ratio, particularly at lower CPU capacities, where its dynamic offloading strategy helps manage the limit"
      }
    ],
    "source_artifacts": [
      "matrix/matrix-summary.csv"
    ],
    "support_status": "partially_supported",
    "title": "Performance comparison of HOODIE and six baselines"
  },
  {
    "artifact_backed_reproduction_data": {
      "available": false
    },
    "caveats": [
      "Current artifacts do not include HOODIE with-LSTM and without-LSTM training delay curves."
    ],
    "comparison_ready": false,
    "extracted_artifact_metrics": {},
    "figure_id": "Figure 11",
    "missing_artifacts": [
      "hoodie_lstm_training_delay_curve",
      "hoodie_without_lstm_training_delay_curve",
      "training_episode_delay_logs"
    ],
    "paper_caption_supported_metadata": {
      "dimensions": [
        "training_episode",
        "with_lstm",
        "without_lstm"
      ]
    },
    "paper_claim_type": "lstm_ablation_training_curve_caption",
    "paper_numeric_target_data": {
      "available": false,
      "missing": [
        "paper_numeric_curve_values"
      ]
    },
    "paper_ocr_evidence": [
      {
        "char_offset": 164767,
        "figure_id": "Figure 11",
        "snippet_index": 0,
        "source_path": "resources/papers/hoodie/ocr/merged.tex",
        "text": "| -0.43 2100 | -0.42 | -0.42 2200 | -0.42 | -0.42 2300 | -0.42 | -0.42 2400 | -0.42 | -0.42 2500 | -0.42 | -0.42 2600 | -0.42 | -0.42 2700 | -0.42 | -0.42 2800 | -0.42 | -0.42 2900 | -0.42 | -0.42 3000 | -0.42 | -0.42 FIGURE 11. Average task delay of HOoDIE with vs without the LSTM inclusion as a function of the training episodes. 22 VOLUME, ===== page\\_023\\_0\\_res.txt ===== unexpected traffic variations (e.g. traffic burst or decline) in which HOODIE could adopt an adaptive behavior to handle these changes. One potential solution would be the P valuebaled model-switching mechanism that allows the agents to respond flexibly to varying traffic conditions without the need for retraining in rea"
      }
    ],
    "source_artifacts": [],
    "support_status": "unsupported",
    "title": "Average task delay of HOODIE with vs without LSTM"
  }
]
```
