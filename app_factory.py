# Standard Library Imports
from typing import List

# Local Imports
from schedule_builder.builders.schedule import Schedule
from schedule_builder.eligibility.eligibility_checker import EligibilityChecker
from schedule_builder.helpers.file_exporter import FileExporter
from schedule_builder.helpers.worship_leader_selector import WorshipLeaderSelector
from schedule_builder.models.person import Person
from schedule_builder.models.preacher import Preacher
from ui.application import App
from ui.ui_manager import UIManager
from ui.ui_schedule_handler import UIScheduleHandler


def create_app(
    title: str,
    team: List[Person],
    preachers: List[Preacher],
    worship_leader_selector: WorshipLeaderSelector,
    eligibility_checker: EligibilityChecker,
) -> App:
    """
    Factory function to create the application instance with all dependencies wired up.


    Args:
        title (str): The title of the application.
        team (List[Person]): List of team members to be scheduled.
        preachers (List[Preacher]): List of preachers available for the schedule.
        worship_leader_selector (WorshipLeaderSelector): Selector for worship leaders.
        eligibility_checker (EligibilityChecker): Eligibility checker for scheduling.

    """
    # Create file exporter
    file_exporter = FileExporter()

    # Create schedule handler
    schedule_handler = UIScheduleHandler(
        team=team,
        preachers=preachers,
        worship_leader_selector=worship_leader_selector,
        eligibility_checker=eligibility_checker,
        file_exporter=file_exporter,
        schedule_class=Schedule,
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
