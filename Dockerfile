FROM jinaai/jina:2.0.0 as base

COPY . ./ranking_evaluator/
WORKDIR ./ranking_evaluator

RUN pip install .

ENTRYPOINT ["jina", "executor", "--uses", "config.yml"]
