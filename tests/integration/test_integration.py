import pytest

import os

from jina import Flow, Document, DocumentArray

cur_dir = os.path.dirname(os.path.abspath(__file__))


def test_evaluation():

    def get_doc_groundtruth_pairs():
        matches = DocumentArray([Document(tags={'id': i}) for i in range(5)])
        matches_gt = DocumentArray(
            [Document(tags={'id': 1}), Document(tags={'id': 0}), Document(tags={'id': 20}), Document(tags={'id': 30}),
             Document(tags={'id': 40})])
        query = Document()
        query.matches = matches
        gt = Document()
        gt.matches = matches_gt
        yield query, gt

    with Flow.load_config(os.path.join(cur_dir, 'flow.yml')) as evaluate_flow:
        results = evaluate_flow.search(
            inputs=get_doc_groundtruth_pairs()
        )

    assert results[0].docs[0].evaluations[f'precision@5'].value == pytest.approx(0.4, 0.0001)
