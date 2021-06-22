import setuptools


setuptools.setup(
    name="executors-evaluator-ranking",
    version="1",
    author='Jina Dev Team',
    author_email='dev-team@jina.ai',
    description="Executor that evaluates ranking results",
    url="https://github.com/jina-ai/executors-evaluator-ranking",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    py_modules=['jinahub.evaluators.rank.ranking_evaluator', 'jinahub.evaluators.rank.metrics'],
    package_dir={'jinahub.evaluators.rank': '.'},
    install_requires=open("requirements.txt").readlines(),
    python_requires=">=3.7",
)
