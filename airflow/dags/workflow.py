from pathlib import Path

from great_expectations_provider.operators.great_expectations import (
    GreatExpectationsOperator,
)

from airflow.decorators import dag
from airflow.providers.airbyte.operators.airbyte import (
    AirbyteTriggerSyncOperator,
)
from airflow.utils.dates import days_ago

default_args = {
    "owner": "airflow",
    "catch_up": False,
}

BASE_DIR = Path(__file__).parent.parent.parent.absolute()
GE_DIR = Path(BASE_DIR, "great_expectations")


@dag(
    dag_id="dataops",
    description="DataOps Workflows",
    default_args=default_args,
    schedule_interval=None,
    start_date=days_ago(2),
    tags=["dataops"],
)
def dataops():
    """DataOps Workflows"""
    # Extract + Load
    extract_and_load_projects = AirbyteTriggerSyncOperator(
        task_id="extract_and_load_projects",
        airbyte_conn_id="airbyte",
        connection_id="5d952c97-620c-44fb-8b00-fc5cb873ba23",  # REPLACE
        asynchronous=False,
        timeout=3600,
        wait_seconds=3,
    )
    extract_and_load_tags = AirbyteTriggerSyncOperator(
        task_id="extract_and_load_tags",
        airbyte_conn_id="airbyte",
        connection_id="26c08f6f-3b7b-4a91-9c9c-7d4fc1303138",  # REPLACE
        asynchronous=False,
        timeout=3600,
        wait_seconds=3,
    )

    validate_projects = GreatExpectationsOperator(
        task_id="validate_projects",
        checkpoint_name="projects",
        data_context_root_dir=GE_DIR,
        fail_task_on_validation_failure=True,
    )

    validate_tags = GreatExpectationsOperator(
        task_id="validate_tags",
        checkpoint_name="tags",
        data_context_root_dir=GE_DIR,
        fail_task_on_validation_failure=True,
    )

    # Defining DAG
    extract_and_load_projects >> validate_projects
    extract_and_load_tags >> validate_tags


# Running DAG
do = dataops()