FROM jinaai/jina:master as base

COPY . ./ranking_evaluator/
WORKDIR ./ranking_evaluator

RUN pip install .

FROM base
RUN pip install -r tests/requirements.txt
RUN pytest -v -s tests

FROM base
ENTRYPOINT ["jina", "executor", "--uses", "config.yml"]