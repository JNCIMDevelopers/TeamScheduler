# Standard Library Imports
import logging
import os

# Local Imports
from app_factory import create_app
from config import OUTPUT_FOLDER_PATH, LOG_FILE_PATH

from schedule_builder.builders.team_initializer import TeamInitializer
from schedule_builder.eligibility.eligibility_checker import EligibilityChecker
from schedule_builder.eligibility.rules import (
    RoleCapabilityRule,
    OnLeaveRule,
    BlockoutDateRule,
    PreachingDateRule,
    RoleTimeWindowRule,
    ConsecutiveAssignmentLimitRule,
    ConsecutiveRoleAssignmentLimitRule,
    WorshipLeaderTeachingRule,
    WorshipLeaderPreachingConflictRule,
    LuluEmceeRule,
    GeeWorshipLeaderRule,
    KrisAcousticRule,
    JeffMarielAssignmentRule,
    MarkDrumsRule,
    AubreyAssignmentRule,
)
from schedule_builder.helpers.worship_leader_selector import WorshipLeaderSelector


def set_logging() -> None:
    """
    Configures logging settings for the application.
    """
    logging.basicConfig(
        filename=LOG_FILE_PATH,
        filemode="w",
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )


def main() -> None:
    """
    Main entry point of the application.
    """
    # Setup output directory and logging config
    os.makedirs(OUTPUT_FOLDER_PATH, exist_ok=True)
    set_logging()

    # Initialize team data
    team_initializer = TeamInitializer()
    team, preachers, rotation = team_initializer.initialize_team()

    # Initialize schedule dependencies
    worship_leader_selector = WorshipLeaderSelector(rotation=rotation)
    eligibility_checker = EligibilityChecker(
        rules=[
            OnLeaveRule(),
            BlockoutDateRule(),
            PreachingDateRule(),
            RoleCapabilityRule(),
            WorshipLeaderTeachingRule(),
            ConsecutiveAssignmentLimitRule(),
            ConsecutiveRoleAssignmentLimitRule(assignment_limit=2),
            RoleTimeWindowRule(),
            WorshipLeaderPreachingConflictRule(),
            LuluEmceeRule(),
            GeeWorshipLeaderRule(),
            KrisAcousticRule(),
            JeffMarielAssignmentRule(),
            MarkDrumsRule(),
            AubreyAssignmentRule(),
        ]
    )

    # Create and run application
    app = create_app(
        title="Schedule Builder",
        team=team,
        preachers=preachers,
        worship_leader_selector=worship_leader_selector,
        eligibility_checker=eligibility_checker,
    )
    app.start()


if __name__ == "__main__":
    main()
