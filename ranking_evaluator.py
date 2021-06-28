__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

from typing import Optional, Union, List, Dict, Tuple

from jina.logging.logger import JinaLogger
from jina import DocumentArray, Executor, requests, Document
from jina.types.arrays.traversable import TraversableSequence

from metrics import precision, recall, reciprocal_rank, average_precision, fscore, ndcg


class RankingEvaluator(Executor):
    class DocGroundtruthPair:
        def __init__(self, doc: 'Document', groundtruth: 'Document'):
            self.pair = (doc, groundtruth)

        def __getitem__(self, item):
            return self.pair[item]

        @property
        def doc(self):
            return self[0]

        @property
        def groundtruth(self):
            return self[1]

        @property
        def matches(self):
            pairs = []
            for doc, groundtruth in zip(self.doc.matches, self.groundtruth.matches):
                pairs.append(RankingEvaluator.DocGroundtruthPair(doc, groundtruth))
            return RankingEvaluator.DocGroundtruthArray(pairs)

        @property
        def chunks(self):
            assert len(self.doc.chunks) == len(self.groundtruth.chunks)
            pairs = []
            for doc, groundtruth in zip(self.doc.chunks, self.groundtruth.chunks):
                pairs.append(RankingEvaluator.DocGroundtruthPair(doc, groundtruth))
            return RankingEvaluator.DocGroundtruthArray(pairs)

    class DocGroundtruthArray(TraversableSequence):
        def __init__(self, pairs):
            self._pairs = pairs

        @property
        def matches(self):
            pairs = []
            for doc, groundtruth in zip(self.doc.matches, self.groundtruth.matches):
                pairs.append(RankingEvaluator.DocGroundtruthPair(doc, groundtruth))
            return RankingEvaluator.DocGroundtruthArray(pairs)

        @property
        def chunks(self):
            assert len(self.doc.chunks) == len(self.groundtruth.chunks)
            pairs = []
            for doc, groundtruth in zip(self.doc.chunks, self.groundtruth.chunks):
                pairs.append(RankingEvaluator.DocGroundtruthPair(doc, groundtruth))
            return RankingEvaluator.DocGroundtruthArray(pairs)

        def __iter__(self):
            for pair in self._pairs:
                yield pair

    def __init__(
            self,
            metric: str = 'precision',
            eval_at: Optional[int] = None,
            beta: Union[int, float] = 1,
            power_relevance: bool = True,
            is_relevance_score: bool = True,
            attribute_fields: Union[str, Tuple[str]] = ('tags__id',),
            evaluation_name: Optional[str] = None,
            default_traversal_paths: List[str] = ['r'],
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
        if metric == 'ndcg' and (not isinstance(attribute_fields, list) or len(attribute_fields) != 2):
            raise Exception(f'NDCG metric requires 2 attribute fields, one for the id and one for the score value')
        self.logger = JinaLogger(self.__class__.__name__)
        self.metric = metric
        self.eval_at = eval_at
        self.beta = beta
        self.power_relevance = power_relevance
        self.is_relevance_score = is_relevance_score
        self.attribute_fields = attribute_fields if isinstance(attribute_fields, list) else list(attribute_fields)
        self.default_traversal_paths = default_traversal_paths
        self.evaluation_name = evaluation_name

        self.metric_fn = funcs[self.metric]
        self.func_extra_args = {
            'eval_at': self.eval_at,
            'beta': self.beta,
            'power_relevance': self.power_relevance,
            'is_relevance_score': self.is_relevance_score
        }

    @property
    def _evaluation_name(self):
        return self.evaluation_name or f'{self.metric}@{self.eval_at}' if self.eval_at is not None else self.metric

    @requests
    def evaluate(self, docs: Optional[DocumentArray], groundtruths: Optional[DocumentArray], parameters: Dict, **kwargs):
        if docs is None or groundtruths is None:
            return
        traversal_paths = parameters.get('traversal_paths', self.default_traversal_paths)
        docs_groundtruths = self.DocGroundtruthArray(
            [
                self.DocGroundtruthPair(doc, groundtruth)
                for doc, groundtruth in zip(docs, groundtruths)
            ]
        )

        for doc, groundtruth in docs_groundtruths.traverse_flat(traversal_paths):
            actual = [match.get_attributes(*self.attribute_fields) for match in doc.matches]
            desired = [match.get_attributes(*self.attribute_fields) for match in groundtruth.matches]
            evaluation = self.metric_fn(actual=actual, desired=desired, **self.func_extra_args)
            print(f' name {self._evaluation_name} => {evaluation}')
            doc.evaluations[self._evaluation_name] = evaluation
