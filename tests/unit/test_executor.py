import pytest

from jina import Document, DocumentArray

try:
    from ranking_evaluator import RankingEvaluator
except:
    from jinahub.evaluators.rank.ranking_evaluator import RankingEvaluator


@pytest.mark.parametrize(
    'eval_at, expected',
    [(None, 0.4), (0, 0.0), (2, 1.0), (4, 0.5), (5, 0.4), (100, 0.4)],
)
def test_ranking_evaluator_precision(eval_at, expected):
    matches = DocumentArray([Document(tags={'id': i}) for i in range(5)])
    matches_gt = DocumentArray(
        [Document(tags={'id': 1}), Document(tags={'id': 0}), Document(tags={'id': 20}), Document(tags={'id': 30}),
         Document(tags={'id': 40})])
    query = Document()
    query.matches = matches
    gt = Document()
    gt.matches = matches_gt

    evaluator = RankingEvaluator(metric='precision', eval_at=eval_at)

    evaluator.evaluate(docs=DocumentArray([query]), groundtruths=DocumentArray([gt]), parameters={})
    assert query.evaluations[evaluator._evaluation_name].value == pytest.approx(expected, 0.0001)


@pytest.mark.parametrize(
    'eval_at, expected',
    [(None, 0.4), (0, 0.0), (2, 1.0), (4, 0.5), (5, 0.4), (100, 0.4)],
)
def test_ranking_evaluator_precision_chunks(eval_at, expected):
    matches = DocumentArray([Document(tags={'id': i}) for i in range(5)])
    matches_gt = DocumentArray(
        [Document(tags={'id': 1}), Document(tags={'id': 0}), Document(tags={'id': 20}), Document(tags={'id': 30}),
         Document(tags={'id': 40})])
    query = Document()
    query_chunk = Document()
    query_chunk.matches = matches
    query.chunks = DocumentArray([query_chunk])
    gt = Document()
    gt_chunk = Document()
    gt_chunk.matches = matches_gt
    gt.chunks = DocumentArray([gt_chunk])

    evaluator = RankingEvaluator(metric='precision', eval_at=eval_at)

    evaluator.evaluate(docs=DocumentArray([query]),
                       groundtruths=DocumentArray([gt]),
                       parameters={'traversal_path': 'c'})
    assert query.chunks[0].evaluations[evaluator._evaluation_name].value == pytest.approx(expected, 0.0001)


@pytest.mark.parametrize(
    'eval_at', [0, 1, 3, 5, 10],
)
@pytest.mark.parametrize(
    'metric', ['precision', 'recall', 'average_precision', 'reciprocal_rank', 'fscore']
)
def test_ranking_evaluator_metrics_available(eval_at, metric):
    matches = DocumentArray([Document(tags={'id': i}) for i in range(5)])
    matches_gt = DocumentArray(
        [Document(tags={'id': 1}), Document(tags={'id': 0}), Document(tags={'id': 20}), Document(tags={'id': 30}),
         Document(tags={'id': 40})])
    query = Document()
    query.matches = matches
    gt = Document()
    gt.matches = matches_gt

    evaluator = RankingEvaluator(metric=metric, eval_at=eval_at)

    evaluator.evaluate(docs=DocumentArray([query]), groundtruths=DocumentArray([gt]), parameters={})
    assert evaluator._evaluation_name in query.evaluations


@pytest.mark.parametrize('power_relevance, expected', [(False, 0.278), (True, 0.209)])
def test_ranking_evaluator_ndcg(power_relevance, expected):
    matches = DocumentArray([Document(tags={'id': 1}, scores={'relevance': 0.0}),
                             Document(tags={'id': 3}, scores={'relevance': 0.1}),
                             Document(tags={'id': 4}, scores={'relevance': 0.2}),
                             Document(tags={'id': 2}, scores={'relevance': 0.3}),
                             ])
    matches_gt = DocumentArray([Document(tags={'id': 1}, scores={'relevance': 0.8}),
                                Document(tags={'id': 3}, scores={'relevance': 0.4}),
                                Document(tags={'id': 4}, scores={'relevance': 0.1}),
                                Document(tags={'id': 2}, scores={'relevance': 0.0}),
                                ])
    query = Document()
    query.matches = matches
    gt = Document()
    gt.matches = matches_gt

    evaluator = RankingEvaluator(metric='ndcg', eval_at=3,
                                 attribute_fields=['tags__id', 'scores__values__relevance__value'],
                                 power_relevance=power_relevance)

    evaluator.evaluate(docs=DocumentArray([query]), groundtruths=DocumentArray([gt]), parameters={})
    assert query.evaluations[evaluator._evaluation_name].value == pytest.approx(expected, 0.01)


def test_wrong_configs():
    with pytest.raises(Exception):
        _ = RankingEvaluator(metric='ndcg')
    with pytest.raises(Exception):
        _ = RankingEvaluator(metric='non-existant')
