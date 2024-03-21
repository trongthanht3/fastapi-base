from celery import Task
from celeryApp.celery_app import celery_app
from ragatouille import RAGPretrainedModel

import logging
logger = logging.getLogger("celeryApp")


class EthereumRetrievalModel:
    def __init__(self, k=10):
        self.model = RAGPretrainedModel.from_index(
            "app/vectordb/colbert/indexes/ethereum-org-no-split")
        self.retriever = self.model.as_langchain_retriever(k=k)

    @staticmethod
    def _load_model_from_path(path):
        model = RAGPretrainedModel.from_index(
            "app/vectordb/colbert/indexes/ethereum-org-no-split")
        return model

    def predict(self, query):
        """
        Make batch prediction on list of preprocessed feature dicts.
        Returns class probabilities if 'return_options' is 'Prob', otherwise returns class membership predictions
        """
        predictions = self.retriever.invoke(query)
        return predictions


class PredictTask(Task):
    """
    Abstraction of Celery's Task class to support loading ML model.

    """
    abstract = True

    def __init__(self):
        super().__init__()
        self.model = None

    def __call__(self, *args, **kwargs):
        """
        Load model on first call (i.e. first task processed)
        Avoids the need to load model on each task request
        """
        if not self.model:
            logging.info('Loading Model...')
            self.model = EthereumRetrievalModel()
            logging.info('Model loaded')
        return self.run(*args, **kwargs)


@celery_app.task(ignore_result=False,
                 bind=True,
                 base=PredictTask,
                 path=('celeryApp.ethereum_worker', 'EthereumRetrievalModel'),
                 acks_late=True)
def ethorg_retrieve(self, query):
    """
    Essentially the run method of PredictTask
    """
    results = self.model.predict(query)
    return results
