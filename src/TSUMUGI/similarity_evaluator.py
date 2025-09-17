from __future__ import annotations

import random

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import average_precision_score, roc_auc_score, silhouette_score


def evaluate_with_known_relationships(
    similarity_scores: dict[frozenset, float],
    known_relationships: set[frozenset],
    negative_pairs: set[frozenset] = None,
) -> dict[str, float]:
    """既知の遺伝子関係を用いて類似度指標の性能を評価

    Args:
        similarity_scores: 遺伝子ペアの類似度スコア
        known_relationships: 既知の関連遺伝子ペア（正例）
        negative_pairs: 非関連遺伝子ペア（負例）、Noneの場合はランダムサンプリング

    Returns:
        評価指標の辞書（AUC-ROC, AP, Precision@K）
    """
    # 正例の類似度スコア取得
    positive_scores = []
    for pair in known_relationships:
        if pair in similarity_scores:
            positive_scores.append(similarity_scores[pair])

    # 負例の生成または取得
    if negative_pairs is None:
        all_genes = set()
        for pair in similarity_scores.keys():
            all_genes.update(pair)

        # ランダムに負例を生成（正例と同数）
        negative_pairs = set()
        all_pairs = list(similarity_scores.keys())
        random.shuffle(all_pairs)

        for pair in all_pairs:
            if pair not in known_relationships:
                negative_pairs.add(pair)
                if len(negative_pairs) >= len(positive_scores):
                    break

    negative_scores = []
    for pair in negative_pairs:
        if pair in similarity_scores:
            negative_scores.append(similarity_scores[pair])

    # ラベルとスコアの準備
    y_true = [1] * len(positive_scores) + [0] * len(negative_scores)
    y_scores = positive_scores + negative_scores

    # 評価指標の計算
    results = {}

    if len(set(y_true)) > 1:  # 正例と負例の両方が存在
        results["auc_roc"] = roc_auc_score(y_true, y_scores)
        results["average_precision"] = average_precision_score(y_true, y_scores)

    # Precision@K の計算
    k_values = [10, 50, 100]
    sorted_pairs = sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)

    for k in k_values:
        top_k_pairs = [pair for pair, _ in sorted_pairs[:k]]
        precision_k = len([p for p in top_k_pairs if p in known_relationships]) / k
        results[f"precision_at_{k}"] = precision_k

    return results


def evaluate_clustering_quality(
    similarity_matrix: np.ndarray, gene_labels: list[str], functional_groups: dict[str, list[str]]
) -> dict[str, float]:
    """機能グループに基づくクラスタリング品質の評価

    Args:
        similarity_matrix: 遺伝子間の類似度行列
        gene_labels: 遺伝子名のリスト（行列のインデックスに対応）
        functional_groups: 機能グループ名から遺伝子リストへのマッピング

    Returns:
        クラスタリング評価指標
    """
    # 遺伝子から機能グループへのマッピング作成
    gene_to_group = {}
    for group_name, genes in functional_groups.items():
        for gene in genes:
            if gene in gene_labels:
                gene_to_group[gene] = group_name

    # ラベル配列の作成
    labels = []
    valid_indices = []
    for i, gene in enumerate(gene_labels):
        if gene in gene_to_group:
            labels.append(gene_to_group[gene])
            valid_indices.append(i)

    if len(set(labels)) < 2:
        return {"silhouette_score": 0.0}

    # 有効な遺伝子のみの類似度行列
    valid_similarity = similarity_matrix[np.ix_(valid_indices, valid_indices)]

    # 距離行列に変換（類似度が高いほど距離が近い）
    distance_matrix = 1 - valid_similarity

    # Silhouette係数の計算
    silhouette = silhouette_score(distance_matrix, labels, metric="precomputed")

    # グループ内/グループ間類似度の計算
    intra_group_similarity = []
    inter_group_similarity = []

    for group_name in set(labels):
        group_indices = [i for i, lst in enumerate(labels) if lst == group_name]
        other_indices = [i for i, lst in enumerate(labels) if lst != group_name]

        if len(group_indices) > 1:
            # グループ内の平均類似度
            group_sim = valid_similarity[np.ix_(group_indices, group_indices)]
            np.fill_diagonal(group_sim, np.nan)
            intra_group_similarity.append(np.nanmean(group_sim))

        if len(other_indices) > 0:
            # グループ間の平均類似度
            inter_sim = valid_similarity[np.ix_(group_indices, other_indices)]
            inter_group_similarity.append(np.mean(inter_sim))

    results = {
        "silhouette_score": silhouette,
        "mean_intra_group_similarity": np.mean(intra_group_similarity) if intra_group_similarity else 0,
        "mean_inter_group_similarity": np.mean(inter_group_similarity) if inter_group_similarity else 0,
        "separation_ratio": np.mean(intra_group_similarity) / np.mean(inter_group_similarity)
        if inter_group_similarity and intra_group_similarity
        else 0,
    }

    return results


def evaluate_prediction_performance(
    gene_phenotypes: dict[str, set[str]], similarity_scores: dict[frozenset, float], n_folds: int = 5
) -> dict[str, float]:
    """Leave-one-out的な予測性能の評価

    Args:
        gene_phenotypes: 各遺伝子の表現型セット
        similarity_scores: 遺伝子ペアの類似度スコア
        n_folds: 交差検証のフォールド数

    Returns:
        予測性能指標
    """
    genes = list(gene_phenotypes.keys())
    random.shuffle(genes)

    fold_size = len(genes) // n_folds
    predictions_correct = []

    for fold in range(n_folds):
        test_genes = genes[fold * fold_size : (fold + 1) * fold_size]
        train_genes = genes[: fold * fold_size] + genes[(fold + 1) * fold_size :]

        for test_gene in test_genes:
            true_phenotypes = gene_phenotypes[test_gene]

            # 最も類似した遺伝子を見つける
            best_similarity = 0
            best_gene = None

            for train_gene in train_genes:
                pair = frozenset([test_gene, train_gene])
                if pair in similarity_scores:
                    if similarity_scores[pair] > best_similarity:
                        best_similarity = similarity_scores[pair]
                        best_gene = train_gene

            if best_gene:
                predicted_phenotypes = gene_phenotypes[best_gene]
                # Jaccard係数で予測精度を評価
                intersection = len(true_phenotypes & predicted_phenotypes)
                union = len(true_phenotypes | predicted_phenotypes)
                if union > 0:
                    accuracy = intersection / union
                    predictions_correct.append(accuracy)

    return {
        "mean_prediction_accuracy": np.mean(predictions_correct) if predictions_correct else 0,
        "std_prediction_accuracy": np.std(predictions_correct) if predictions_correct else 0,
    }


def evaluate_robustness(
    original_scores: dict[frozenset, float], perturbed_scores: dict[frozenset, float], noise_level: float
) -> dict[str, float]:
    """ノイズに対するロバスト性の評価

    Args:
        original_scores: 元の類似度スコア
        perturbed_scores: ノイズ追加後の類似度スコア
        noise_level: ノイズレベル（0-1）

    Returns:
        ロバスト性指標
    """
    common_pairs = set(original_scores.keys()) & set(perturbed_scores.keys())

    if not common_pairs:
        return {"spearman_correlation": 0, "pearson_correlation": 0}

    orig_values = []
    pert_values = []

    for pair in common_pairs:
        orig_values.append(original_scores[pair])
        pert_values.append(perturbed_scores[pair])

    spearman_corr, _ = stats.spearmanr(orig_values, pert_values)
    pearson_corr, _ = stats.pearsonr(orig_values, pert_values)

    # ランキングの安定性
    orig_ranking = {
        pair: rank for rank, (pair, _) in enumerate(sorted(original_scores.items(), key=lambda x: x[1], reverse=True))
    }
    pert_ranking = {
        pair: rank for rank, (pair, _) in enumerate(sorted(perturbed_scores.items(), key=lambda x: x[1], reverse=True))
    }

    rank_differences = []
    for pair in common_pairs:
        if pair in orig_ranking and pair in pert_ranking:
            rank_differences.append(abs(orig_ranking[pair] - pert_ranking[pair]))

    mean_rank_change = np.mean(rank_differences) if rank_differences else 0

    return {
        "spearman_correlation": spearman_corr,
        "pearson_correlation": pearson_corr,
        "mean_rank_change": mean_rank_change,
        "noise_level": noise_level,
    }


def compare_similarity_metrics(
    shared_phenotypes_scores: dict[frozenset, int],
    jaccard_scores: dict[frozenset, float],
    phenodigm_scores: dict[frozenset, float],
    known_relationships: set[frozenset],
    functional_groups: dict[str, list[str]],
) -> pd.DataFrame:
    """3つの類似度指標を包括的に比較

    Returns:
        各指標の評価結果を含むDataFrame
    """
    results = []

    # 各指標を正規化（0-1スケール）
    def normalize_scores(scores):
        values = list(scores.values())
        min_val, max_val = min(values), max(values)
        if max_val > min_val:
            return {k: (v - min_val) / (max_val - min_val) for k, v in scores.items()}
        return scores

    normalized_metrics = {
        "shared_phenotypes": normalize_scores(shared_phenotypes_scores),
        "jaccard": normalize_scores(jaccard_scores),
        "phenodigm": normalize_scores(phenodigm_scores),
    }

    for metric_name, scores in normalized_metrics.items():
        # 既知関係による評価
        bio_eval = evaluate_with_known_relationships(scores, known_relationships)

        result = {
            "metric": metric_name,
            "auc_roc": bio_eval.get("auc_roc", 0),
            "average_precision": bio_eval.get("average_precision", 0),
            "precision_at_10": bio_eval.get("precision_at_10", 0),
            "precision_at_50": bio_eval.get("precision_at_50", 0),
            "precision_at_100": bio_eval.get("precision_at_100", 0),
        }

        results.append(result)

    return pd.DataFrame(results)
