import setuptools


setuptools.setup(
    name="executors-evaluator-ranking",
    version="2.0",
    author='Jina Dev Team',
    author_email='dev-team@jina.ai',
    description="Executor that evaluates ranking results",
    url="https://github.com/jina-ai/executors-evaluator-ranking",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    #py_modules=['jinahub.evaluators.rank'],
    package_dir={'jinahub.evaluators.rank': '.'},
    install_requires=open("requirements.txt").readlines(),
    python_requires=">=3.7",
)
