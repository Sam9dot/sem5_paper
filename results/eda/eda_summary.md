# Day 1 EDA — Shriya

- **Dataset:** `Dataset 2 system logs dataset.csv`
- **Rows analysed:** 100,000; **columns:** 63
- **Key features plotted:** CPU (%), network_bandwidth, network_latency, firewall_packets_dropped, TCP Connection Count, memory (GB), packet_loss_rate, Disk Write Operations per Second

## Top 10 predictive-feature candidates

Ranked by absolute Pearson correlation with the binary target. This is exploratory association, not causal feature importance.

|                   |   abs_correlation_with_is_attack |   correlation_direction |   normal_median |   attack_median |
|:------------------|---------------------------------:|------------------------:|----------------:|----------------:|
| load              |                           0.7503 |                  0.7503 |          1.5    |          3.73   |
| pgpgio            |                           0.6889 |                  0.6889 |        550      |        999      |
| io (MB/s)         |                           0.6731 |                  0.6731 |          3      |          6      |
| ram (GB)          |                           0.6568 |                  0.6568 |          6      |         11      |
| processes         |                           0.5674 |                  0.5674 |        250      |        448      |
| CPU (%)           |                           0.5642 |                  0.5642 |         18      |         35      |
| CPU system (%)    |                           0.5499 |                  0.5499 |          9      |         17      |
| network_errors    |                           0.5046 |                  0.5046 |          4.9929 |          9.3041 |
| writeback (MB)    |                           0.4361 |                  0.4361 |        299      |        498      |
| network_bandwidth |                           0.4085 |                  0.4085 |        551.308  |        867.456  |

## Outlier interpretation

IQR outlier rates overall and by class are stored in `iqr_outlier_summary.csv`. A higher attack-class rate can indicate real attack behaviour; these observations should not be removed without a documented domain-based data-quality reason.

## Redundancy note

Pairs with absolute correlation ≥ 0.90 are listed in `highly_correlated_feature_pairs.csv` for later modelling consideration.

## Saved EDA assets

- `distribution_*.png`: normal-versus-attack distributions
- `correlation_heatmap.png`: correlations among target-associated numeric features
- `outlier_boxplots_by_class.png`: class-specific boxplots