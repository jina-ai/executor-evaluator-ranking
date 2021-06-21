<p align="center">
<img src="https://github.com/jina-ai/jina/blob/master/.github/logo-only.gif?raw=true" alt="Jina banner" width="200px">
</p>

# Ranking Evaluator

### Description
The Ranking Evaluator offers an executor that can evaluate the performance of a search system by comparing the matches obtained
by a `query` with the matches expected inside a `groundtruth`.

### Parameters

- `metric` (str, default `precision`): The evaluation metric to compute (Possible values are: `precision`, `recall`, `ndcg`, `reciprocal_rank`, `average_precision`, `fscore`)
- `eval_at` (Optional[int], default None): the point at which evaluation is computed, if None give, will consider all the input to evaluate. Not relevant for `reciprocal_rank` metric 
- `beta` (int or float, default 1): Parameter to weight differently precision and recall. Only used when metric is `reciprocal_rank`
- `power_relevance` (bool, default True): The power relevance places stronger emphasis on retrieving relevant documents. Only used when metric is `ndcg`
- `is_relevance_score` (bool, default True): Boolean indicating if the actual scores are to be considered relevance. Highest value is better. If True, the information coming from the actual system results willbe sorted in descending order, otherwise in ascending order. Only used when metric is `ndcg`
- `attribute_fields` (Union[str, Tuple[str]], default ('tags__id', )): The fields names to be extracted from the `matches`. This relies in `DocumentArray` `get_attributes` API to extract these fields. For every `metric` this field should be the field 
                    where the `Document` identifier can be found. For `ndcg` the relevance field is also needed. 
- `evaluation_name` (str): The name of the evaluation to set for the `documents` evaluated
- `default_traversal_path` (str): Fallback traversal path in case there is not traversal path sent in the request.

## Prerequisites

None


## Usages

### Via JinaHub (🚧W.I.P.)

Use the prebuilt images from JinaHub in your python codes, 

```python
from jina import Flow
f = Flow().add(
        uses='jinahub+docker://RankingEvaluator')
```

or in the `.yml` config.

```yaml
jtype: Flow
pods:
  - name: evaluator
    uses: 'jinahub+docker://RankingEvaluator'
```


### Via Pypi

1. Install the `jinahub-ranking-evaluator`

    ```bash
    pip install git+https://github.com/jina-ai/executors-evaluator-ranking.git
    ```

2. Use `jinahub-image` in your code

    ```python
    from jinahub.evaluators.rank.ranking_evaluator import RankingEvaluator
    from jina import Flow
    
    f = Flow().add(uses=RankingEvaluator)
    ```


### Via Docker

1. Clone the repo and build the docker image

    ```shell
    git clone https://github.com/jina-ai/executors-evaluator-ranking.git
    cd executors-evaluator-ranking
    docker build -t jinahub-ranking-evaluator-image .
    ```

2. Use `jinahub-image` in your codes

    ```python
    from jina import Flow
    
    f = Flow().add(
            uses='docker://jinahub-ranking-evaluator-image:latest')
    ```
    


## Example 

```python
from jina import Flow, Document, DocumentArray

def check_resp(resp):
    for doc in resp.docs:
        print(f'evaluations: {doc.evaluations}')

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

with Flow().add(uses='jinahub+docker://RankingEvaluator') as f:
    f.post(on='foo',
           inputs=get_doc_groundtruth_pairs(),
           on_done=check_resp)
```

### Inputs 

[Documents](https://github.com/jina-ai/jina/blob/master/.github/2.0/cookbooks/Document.md) with sorted `matches` plus `groundtruth` with sorted expected matches. 

### Returns

[Documents](https://github.com/jina-ai/jina/blob/master/.github/2.0/cookbooks/Document.md) with `evaluations` field filled with a score value by the name of the computed evaluation metric