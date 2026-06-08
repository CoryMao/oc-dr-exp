# Recall Audit — exp_binding_affinity_run2

## 记忆检索记录

### Query 1: "binding affinity protein ligand prediction benchmark"
- 命中 5 条，全部来自 exp_binding_affinity_run1
- 最高分条目: step4 search_papers (score 22.57)
- 关键上下文: Run 1 论文 ID [A]-[F] 及核心发现

### Query 2: "binding affinity overclaim mis-citation error"
- 命中 5 条，含 exp_audit_run1 记录
- 关键上下文: "not in Abstract ≠ Overclaim" 原则、43/45 正确率审计

### Query 3: "binding affinity arXiv paper ID"
- 命中 5 条，确认 Run 1 论文 ID: 2405.14108, 2602.07735, 2512.05386, 2512.22031, 2603.05532, 1911.00930

## Claim 检索记录

### pre_action_hook for Claim 10 (ShallowBench)
- 查询: "ShallowBench shallow pocket generative drug design binding affinity low concavity"
- 命中 3 条（本 run 的 fetch_paper 和 extract_claim）
- ✅ 上下文完整，未发现与已有 claims 冲突

### pre_action_hook for Claim 11 (HonestAffinity)
- 查询: "HonestAffinity leak-aware evaluation binding affinity split-conditioned reversal pocket prior ESM-2"
- 命中 3 条（本 run 的 fetch_paper 和 extract_claim）
- ✅ 上下文完整

### pre_action_hook for Claim 12 (InteractBind)
- 查询: "InteractBind binding site localization non-covalent interaction protein-ligand benchmark evaluation"
- 命中 3 条（本 run 的 fetch_paper 和 extract_claim）
- ✅ 上下文完整

## 验证结果
- 所有 3 个 claims 均通过 recall 检查
- 无 overclaim/mis-citation/unsupported 标记
- 所有来源为 arXiv 摘要，可直接验证
- 与 Run 1 的 9 条 claims 无冲突

## Run 1 vs Run 2 交叉检查

| 维度 | Run 1 | Run 2 | 关系 |
|------|-------|-------|------|
| OOD 泛化 | [A] PoseBench DL 在新靶点性能下降 | [G] ShallowBench 浅口袋困境 | ✅ 一致，扩展靶点类型 |
| 基准泄漏 | [C] 标准基准存在泄漏 | [H] HonestAffinity 泄漏翻转先验排名 | ✅ 一致，提供新证据 |
| 可解释性 | 未覆盖 | [I] InteractBind 结合位点定位不足 | 🆕 新维度 |
| 物理方法价值 | [E] Boltz-2 vs ESMACS 弱相关 | [I] 模型学结合概率非结合位点 | ✅ 一致，不同角度 |
| TerraBind 粗粒表征 | [B] 26×加速，Pearson r +20% | 未重复评估 | — |
| 2D 指纹 vs 3D DL | [F] 无结构任务相当 | 未重复评估 | — |
