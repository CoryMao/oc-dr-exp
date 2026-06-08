# Action Memory Recall Audit — exp_mllm_vision_run2

> Generated: 2026-06-08T23:15:22+08:00

## Overview

- **Total retrievals:** 2
- **Total hits:** 6 (avg 3.0/retrieval)
- **Zero-hit retrievals:** 0 (0%)
- **Same-case hits:** 4 (67%)
- **Cross-case hits:** 2 (33%)

## Retrieval Log Detail

### #1: 2026-06-08T23:14:22+08:00

- **Context:** `exp_mllm_vision_run2`
- **Query:** `Cartesian Shortcut Polaris-Bench polar coordinate topology-invariant visual reasoning collapse`
- **Method:** `bm25` | top_k: `3`
- **Hits:** 3

| Score | Hit Relation | Success | Case:Step | Action Type | Outcome Excerpt |
|-------|-------------|---------|-----------|-------------|-----------------|
| 54.83 | same-case | ✅ | `exp_mllm_vision_run2:step4` | `fetch_paper` | 成功获取 Cartesian Shortcut 论文。模型在笛卡尔布局达 70-83%，在极坐标等价任务降至 31-39 |
| 22.99 | same-case | ✅ | `exp_mllm_vision_run2:step2` | `search_papers` | 通过 arXiv API 搜索了 'large language model visual reasoning benc |
| 8.51 | cross-case(exp_mllm_vision_run1) | ✅ | `exp_mllm_vision_run1:step1` | `other` | Run 1 started for topic: systematic literature review of MLL |

### #2: 2026-06-08T23:14:29+08:00

- **Context:** `exp_mllm_vision_run2`
- **Query:** `ReasonMatch-Bench wide-baseline matching spatial reasoning DCRL MLLM gap`
- **Method:** `bm25` | top_k: `3`
- **Hits:** 3

| Score | Hit Relation | Success | Case:Step | Action Type | Outcome Excerpt |
|-------|-------------|---------|-----------|-------------|-----------------|
| 48.58 | same-case | ✅ | `exp_mllm_vision_run2:step5` | `fetch_paper` | 成功获取 Eliciting Complex Spatial Reasoning 论文。ReasonMatch-Benc |
| 13.44 | same-case | ✅ | `exp_mllm_vision_run2:step6` | `make_claim` | CLAIM: MLLMs exhibit substantial vision-centric reasoning de |
| 12.60 | cross-case(exp_mllm_vision_run1) | ✅ | `exp_mllm_vision_run1:step5` | `fetch_paper` | Fetched MMPerspective: benchmark for MLLM perspective percep |
