# Standard Library Imports
import logging
import os

# Local Imports
from paths import OUTPUT_FOLDER_PATH, LOG_FILE_PATH
from schedule_builder.builders.team_initializer import TeamInitializer
from ui.application import App


def set_logging() -> None:
    """
    Configures logging settings for the application.

    This function sets up logging to write debug and higher-level messages to a specified file.
    The log file is overwritten each time the application starts.
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

    This function performs the following steps:
    - Creates the output directory if it does not exist.
    - Configures logging settings.
    - Initializes team data.
    - Starts the application GUI.
    """
    # Setup output directory and logging config
    os.makedirs(OUTPUT_FOLDER_PATH, exist_ok=True)
    set_logging()

    # Initialize team data
    team_initializer = TeamInitializer()
    team, preachers, rotation = team_initializer.initialize_team()

    # Run application
    app = App(team=team, preachers=preachers, rotation=rotation)
    app.mainloop()


if __name__ == "__main__":
    main()
