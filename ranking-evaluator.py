__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

from typing import Optional, Union, List, Dict

from jina import DocumentArray, Executor, requests, Document
from jina.types.arrays.traversable import TraversableSequence

from .metrics import precision, recall, reciprocal_rank, average_precision, fscore, ndcg


class RankingEvaluator(Executor):
    class DocGroundtruthPair:
        def __init__(self, doc: 'Document', groundtruth: 'Document'):
            self.doc = doc
            self.groundtruth = groundtruth

        @property
        def matches(self):
            pairs = []
            for doc, groundtruth in zip(self.doc.matches, self.groundtruth.matches):
                pairs.append(RankingEvaluator.DocGroundtruthPair(doc, groundtruth))
            return RankingEvaluator.DocumentGroundtruthArray(pairs)

        @property
        def chunks(self):
            assert len(self.doc.chunks) == len(self.groundtruth.chunks)
            pairs = []
            for doc, groundtruth in zip(self.doc.chunks, self.groundtruth.chunks):
                pairs.append(RankingEvaluator.DocGroundtruthPair(doc, groundtruth))
            return RankingEvaluator.DocumentGroundtruthArray(pairs)

    class DocumentGroundtruthArray(TraversableSequence):
        def __init__(self, pairs):
            self._pairs = pairs

        def __iter__(self):
            for pair in self._pairs:
                yield pair.doc, pair.groundtruth

    def __init__(
            self,
            metric: str = 'precision',
            eval_at: Optional[int] = None,
            beta: int = 1,
            power_relevance: bool = True,
            is_relevance_score: bool = True,
            attribute_id: str = 'tags__id',
            default_traversal_path: Union[str, List[str]] = 'r',
            evaluation_name: Optional[str] = None,
            *args,
            **kwargs,
    ):
        """Set Constructor."""
        super().__init__(*args, **kwargs)
        funcs = {
            'precision': precision,
            'recall': recall,
            'ndcg': ndcg,
            'reciprocal_rank': reciprocal_rank,
            'average_precision': average_precision,
            'fscore': fscore
        }
        if metric not in funcs.keys():
            raise Exception(f'Evaluation Metric {metric} is not supported. Potential values are {set(funcs.keys())}')
        self.metric = metric
        self.eval_at = eval_at
        self.beta = beta
        self.power_relevance = power_relevance
        self.is_relevance_score = is_relevance_score
        self.attribute_id = attribute_id
        self.default_traversal_path = default_traversal_path
        self.evaluation_name = evaluation_name or f'{self.metric}@{self.eval_at}' if self.eval_at is not None else self.metric

        self.metric_fn = funcs[self.metric]
        self.func_extra_args = {
            'eval_at': self.eval_at,
            'beta': self.beta,
            'power_relevance': self.power_relevance,
            'is_relevance_score': self.is_relevance_score
        }

    @requests
    def evaluate(self, docs: DocumentArray, groundtruths: DocumentArray, parameters: Dict, **kwargs):
        traversal_paths = parameters.get('traversal_path', self.default_traversal_path)
        docs_groundtruths = self.DocumentGroundtruthArray(
            [
                self.DocGroundtruthPair(doc, groundtruth)
                for doc, groundtruth in zip(docs, groundtruths)
            ]
        )

        for doc, groundtruth in docs_groundtruths.traverse_flatten(traversal_paths):
            actual = [match.get_attributes(self.attribute_id) for match in doc.matches]
            desired = [match.get_attributes(self.attribute_id) for match in groundtruth.matches]
            evaluation = self.metric_fn(actual=actual, desired=desired, **self.func_extra_args)
            doc.evaluations[self.evaluation_name] = evaluation
