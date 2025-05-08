# Standard Library Imports
from typing import List

# Local Imports
from schedule_builder.helpers.file_exporter import FileExporter
from schedule_builder.models.person import Person
from schedule_builder.models.preacher import Preacher
from ui.application import App
from ui.ui_manager import UIManager
from ui.ui_schedule_handler import UIScheduleHandler


def create_app(
    team: List[Person],
    preachers: List[Preacher],
    rotation: List[str],
    title: str,
) -> App:
    """
    Factory method to create and configure the app instance with the necessary dependencies.

    Args:
        team (List[Person]): A list of team members.
        preachers (List[Preacher]): A list of preachers.
        rotation (List[str]): A list of worship leader names.
        title (str): The title of the app.

    Returns:
        App: A fully initialized App instance.
    """
    file_exporter = FileExporter()
    schedule_handler = UIScheduleHandler(
        team=team,
        preachers=preachers,
        rotation=rotation,
        file_exporter=file_exporter,
    )

    # Create UIManager without app reference initially
    ui_manager = UIManager(
        app=None,
        schedule_handler=schedule_handler,
        title=title,
    )

    # Create App
    app = App(
        file_exporter=file_exporter,
        schedule_handler=schedule_handler,
        ui_manager=ui_manager,
    )

    # Inject the App reference into UIManager
    ui_manager.app = app

    return app
