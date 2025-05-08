# Standard Library Imports
import logging
import os

# Local Imports
from app_factory import create_app
from config import OUTPUT_FOLDER_PATH, LOG_FILE_PATH
from schedule_builder.builders.team_initializer import TeamInitializer


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

    # Run application
    app = create_app(
        team=team, preachers=preachers, rotation=rotation, title="Schedule Builder"
    )
    app.start()


if __name__ == "__main__":
    main()
