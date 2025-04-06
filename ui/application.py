# Standard Library Imports
import copy
import logging
import os
import traceback
from datetime import date
from typing import List, Tuple

# Third-Party Imports
import customtkinter
from tkcalendar import DateEntry
from tkinter import messagebox

# Local Imports
from paths import (
    LOG_FILE_PATH,
    SCHEDULE_CSV_FILE_PATH,
    SCHEDULE_DETAILS_HTML_FILE_PATH
)
from schedule_builder.builders.schedule import Schedule
from schedule_builder.builders.file_builder import (
    generate_team_schedule_html,
    create_html,
    get_schedule_data_for_csv,
    format_data_for_csv,
    create_csv
)
from schedule_builder.util.date_generator import get_all_sundays
from schedule_builder.models.person import Person
from schedule_builder.models.preacher import Preacher


customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")


class App(customtkinter.CTk):
    """
    A GUI application for scheduling using customtkinter and tkcalendar.

    This class initializes and configures the user interface, allowing users to input
    a date range for scheduling. It handles the creation of schedules based on team
    and preacher data, validates date inputs, and provides options to view and manage
    the generated schedules.
    """

    def __init__(self, team: List[Person], preachers: List[Preacher], rotation: List[str]):
        """
        Initializes the application with a list of team members and preachers.

        Args:
            team (List[Person]): A list of Person objects representing the team members.
            preachers (List[Preacher]): A list of Preacher objects representing the preachers.
            rotation (List[str]): A list of strings representing the priority list of worship leader names.
        """
        super().__init__()

        self.logger = logging.getLogger(__name__)

        self.team = team
        self.preachers = preachers
        self.rotation = rotation
        self.earliest_date, self.latest_date = self.calculate_preaching_date_range()
        self.logger.debug(f"Earliest Preaching Date: {str(self.earliest_date)}")
        self.logger.debug(f"Latest Preaching Date: {str(self.latest_date)}")

        self.setup_ui()

    def setup_ui(self) -> None:
        """
        Sets up the user interface for the application, including window size, widgets, and layout.
        """
        # Setup window
        self.title("Schedule Builder")
        self.STANDARD_FONT = "Roboto"
        self.CONFIRMATION_LABEL_FONT_SIZE = 20

        window_width = 500
        window_height = 375
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.geometry(f'{window_width}x{window_height}+{x}+{y}')

        # Create frame to hold all widgets
        self.frame = customtkinter.CTkFrame(master=self)
        self.frame.pack(pady=20, padx=60, fill="both", expand=True)

        # Title label
        self.title_label = customtkinter.CTkLabel(
            master=self.frame, text="Schedule Builder", font=(self.STANDARD_FONT, 24)
        )
        self.title_label.pack(pady=20)

        # Start date label and entry
        self.start_date_label = customtkinter.CTkLabel(
            master=self.frame,
            text="START DATE",
            font=(self.STANDARD_FONT, 14)
        )
        self.start_date_label.pack()
        self.start_date_entry = DateEntry(
            master=self.frame,
            selectmode="day",
            locale="en_US",
            date_pattern="MM/dd/yyyy",
            font=(self.STANDARD_FONT, 12),
        )
        self.start_date_entry.pack(pady=(0, 10))

        # End date label and entry
        self.end_date_label = customtkinter.CTkLabel(
            master=self.frame,
            text="END DATE",
            font=(self.STANDARD_FONT, 14)
        )
        self.end_date_label.pack()
        self.end_date_entry = DateEntry(
            master=self.frame,
            selectmode="day",
            locale="en_US",
            date_pattern="MM/dd/yyyy",
            font=(self.STANDARD_FONT, 12),
        )
        self.end_date_entry.pack(pady=(0, 10))

        # Create button
        self.create_button = customtkinter.CTkButton(
            master=self.frame,
            text="CREATE",
            command=self.handle_create_button_click,
            font=(self.STANDARD_FONT, 14),
        )
        self.create_button.pack(pady=10)

        # Confirmation label
        self.confirmation_label = customtkinter.CTkLabel(
            master=self.frame,
            text="",
            font=(self.STANDARD_FONT, self.CONFIRMATION_LABEL_FONT_SIZE),
            wraplength=350
        )
        self.confirmation_label.pack(pady=5)

        # Schedule details ouput label
        self.output_link_label = customtkinter.CTkLabel(
            master=self.frame,
            text="",
            font=(self.STANDARD_FONT, self.CONFIRMATION_LABEL_FONT_SIZE, "underline"),
            text_color="#4682B4",
            cursor="hand2",
            wraplength=350
        )
        self.output_link_label.pack(pady=5)

    def handle_open_schedule_file(self, event, label: customtkinter.CTkLabel, filepath: str) -> None:
        """
        Opens the schedule file located at the specified filepath using the default application
        and updates the link color to indicate it has been clicked.

        Args:
            event: The custometkinter event that triggered this handler (if any).
            label (customtkinter.CTkLabel): The CTkLabel that was clicked.
            filepath (str): The path to the file to open.
        """
        os.startfile(os.path.join(".", filepath), "open")
        label.configure(text_color="#9b30ff")

    def handle_create_button_click(self) -> None:
        """
        Event handler for the 'CREATE' button click.

        This function performs several actions upon clicking the 'CREATE' button:
        - Retrieves the start and end dates from date entry widgets.
        - Validates the input dates and displays appropriate error messages if necessary.
        - Adjusts dates to ensure they fall within the permissible range if needed.
        - Creates a schedule for the specified date range.
        - Configures the confirmation message label widget.
        """
        start_date = self.start_date_entry.get_date()
        self.logger.debug(f"Start Date: {str(start_date)}")

        end_date = self.end_date_entry.get_date()
        self.logger.debug(f"End Date: {str(end_date)}")

        if not start_date or not end_date:
            self.reset_output_labels()
            self.confirmation_label.configure(
                text="Missing Input!",
                font=(self.STANDARD_FONT, self.CONFIRMATION_LABEL_FONT_SIZE),
                text_color="red",
                cursor="arrow",
            )
            return

        if start_date > end_date:
            self.reset_output_labels()
            self.confirmation_label.configure(
                text="Invalid Input!",
                font=(self.STANDARD_FONT, self.CONFIRMATION_LABEL_FONT_SIZE),
                text_color="red",
                cursor="arrow",
            )
            return

        if (not self.is_within_date_range(start_date)
            and not self.is_within_date_range(end_date)
            and not self.is_preaching_schedule_within_date_range(start_date, end_date)):
            self.reset_output_labels()
            self.confirmation_label.configure(
                text="No preaching schedule available within specified dates!",
                font=(self.STANDARD_FONT, self.CONFIRMATION_LABEL_FONT_SIZE),
                text_color="red",
                cursor="arrow",
            )
            return

        start_date, end_date, is_adjusted = self.adjust_dates_within_range(start_date=start_date, end_date=end_date)
        if is_adjusted:
            message = f"Preaching schedule is only available from {str(start_date)} to {str(end_date)}."
            messagebox.showinfo("Alert", message)
            self.logger.warning(message)

        try:
            self.create_schedule(start_date=start_date, end_date=end_date)

            self.reset_output_labels()
            self.confirmation_label.bind("<Button-1>", lambda e: self.handle_open_schedule_file(e, label=self.confirmation_label, filepath=SCHEDULE_CSV_FILE_PATH))
            self.confirmation_label.configure(
                text="View Schedule",
                font=(self.STANDARD_FONT, self.CONFIRMATION_LABEL_FONT_SIZE, "underline"),
                text_color="#4682B4",
                cursor="hand2",
            )

            self.output_link_label.bind("<Button-1>", lambda e: self.handle_open_schedule_file(e, self.output_link_label, SCHEDULE_DETAILS_HTML_FILE_PATH))
            self.output_link_label.configure(text="View Schedule Details")
        except PermissionError:
            self.handle_schedule_creation_exception(message="Please close any open\noutput files and try again.")
        except Exception:
            self.handle_schedule_creation_exception(message="An unexpected error occurred.")
            

    def reset_output_labels(self) -> None:
        """
        Resets the confirmation/output labels.
        """
        self.confirmation_label.unbind("<Button-1>")
        self.output_link_label.unbind("<Button-1>")
        self.output_link_label.configure(
            text="",
            text_color="#4682B4"
        )

    def handle_schedule_creation_exception(self, message):
        """
        Handles exceptions that occur during schedule creation by logging the error, 
        resetting output labels, and updating the output labels with an error message.

        Args:
            message (str): The error message to display on the confirmation label.
        """
        self.logger.error(traceback.format_exc())
        self.reset_output_labels()
        self.confirmation_label.configure(
            text=message,
            font=(self.STANDARD_FONT, self.CONFIRMATION_LABEL_FONT_SIZE),
            text_color="red",
            cursor="arrow",
        )
        self.output_link_label.bind("<Button-1>", lambda e: self.handle_open_schedule_file(e, self.output_link_label, LOG_FILE_PATH))
        self.output_link_label.configure(
            text="Click to view logs.",
            font=(self.STANDARD_FONT, self.CONFIRMATION_LABEL_FONT_SIZE, "underline")
        )


    def calculate_preaching_date_range(self) -> Tuple[date, date]:
        """
        Calculates the earliest and latest preaching dates.

        Returns:
            Tuple[date, date]: A tuple containing the earliest and latest preaching dates found
            among all preachers.
        """
        all_dates = [
            preaching_date
            for preacher in self.preachers
            for preaching_date in preacher.dates
        ]
        all_unique_dates = set(all_dates)

        earliest_date = min(all_unique_dates)
        latest_date = max(all_unique_dates)

        return (earliest_date, latest_date)

    def is_within_date_range(self, reference_date: date) -> bool:
        """
        Checks if the given reference_date falls within the date range defined by
        self.earliest_date and self.latest_date.

        Args:
            reference_date (date): The date to check against the date range.

        Returns:
            bool: True if reference_date is within the range [self.earliest_date, self.latest_date],
            False otherwise.
        """
        return self.earliest_date <= reference_date <= self.latest_date
    
    def is_preaching_schedule_within_date_range(self, start_date: date, end_date: date) -> bool:
        """
        Checks if the preaching schedule dates are within the specified
        start and end dates.

        Args:
            start_date (date): The start date of the range to check against.
            end_date (date): The end date of the range to check against.

        Returns:
            bool: True if the preaching schedule is within the range [start_date, end_date],
            False otherwise.
        """
        return start_date <= self.earliest_date <= self.latest_date <= end_date

    def adjust_dates_within_range(self, start_date: date, end_date: date) -> Tuple[date, date, bool]:
        """
        Adjusts the provided start_date and end_date to ensure they fall within the
        permissible date range defined by self.earliest_date and self.latest_date.

        Args:
            start_date (date): The initial start date to adjust.
            end_date (date): The initial end date to adjust.

        Returns:
            Tuple[date, date, bool]: Adjusted start_date, adjusted end_date, and a boolean
            indicating if any adjustments were made (`True` if adjustments were made, `False` otherwise).
        """
        is_adjusted = False

        if start_date < self.earliest_date:
            start_date = self.earliest_date
            is_adjusted = True

        if end_date > self.latest_date:
            end_date = self.latest_date
            is_adjusted = True

        return (start_date, end_date, is_adjusted)

    def create_schedule(self, start_date: date, end_date: date) -> None:
        """
        Creates a schedule from the specified start date to end date.

        Args:
            start_date (date): The start date of the schedule.
            end_date (date): The end date of the schedule.
        """
        # Log the start of the schedule creation
        self.logger.info(f"Creating schedule from {str(start_date)} to {str(end_date)}")

        # Deep copy self.team to prevent modifications from persisting between calls
        team_copy = copy.deepcopy(self.team)

        # Obtain Sunday dates within specified date range
        dates_to_assign = get_all_sundays(start_date=start_date, end_date=end_date)
        self.logger.debug(f"Sunday Dates:\n{str(dates_to_assign)}\n")

        # Build Schedule
        events, updated_team_details = Schedule(
            team=team_copy,
            preachers=self.preachers,
            rotation=self.rotation,
            event_dates=dates_to_assign
        ).build()

        # Generate schedule details in HTML string format
        html_content = generate_team_schedule_html(
            start_date,
            end_date,
            events,
            updated_team_details
        )
        self.logger.debug(f"Schedule Details HTML Data:\n{html_content}\n")

        # Generate HTML document
        create_html(content=html_content, filepath=SCHEDULE_DETAILS_HTML_FILE_PATH)

        # Prepare and format schedule data for CSV export
        csv_data = get_schedule_data_for_csv(events=events)
        formatted_csv_data = format_data_for_csv(data=csv_data)
        self.logger.debug(f"Schedule CSV Data:\n{formatted_csv_data}\n")

        # Generate CSV file
        create_csv(data=formatted_csv_data, filepath=SCHEDULE_CSV_FILE_PATH)
