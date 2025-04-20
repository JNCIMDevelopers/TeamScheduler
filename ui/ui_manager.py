# Third-Party Imports
import customtkinter
from tkcalendar import DateEntry

# Local Imports
from ui.ui_schedule_handler import UIScheduleHandler
from ui.ui_event_handler import UIEventHandler

# Appearance settings for customtkinter
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")


class UIManager:
    """
    Manages the user interface for the application.

    This class is responsible for setting up the UI, adding widgets, and
    delegating event handling to the appropriate handlers.
    """

    def __init__(
        self,
        app: customtkinter.CTk,
        schedule_handler: UIScheduleHandler,
        event_handler: UIEventHandler,
        title: str,
    ):
        """
        Initializes the UI manager with the application, schedule handler, and event handler.

        Args:
            app (customtkinter.CTk): The main application instance.
            schedule_handler (UIScheduleHandler): The handler for schedule-related logic.
            event_handler (UIEventHandler): The handler for user interactions and events.
            title (str): The title of the application window.
        """
        self.app = app
        self.schedule_handler = schedule_handler
        self.event_handler = event_handler
        self.title = title

    def setup(self) -> None:
        """
        Sets up the user interface for the application.

        This method configures the main window and adds widgets to the UI.
        """
        # Setup window
        self.app.title(self.title)
        self.app.STANDARD_FONT = "Roboto"
        self.app.CONFIRMATION_LABEL_FONT_SIZE = 20

        window_width = 500
        window_height = 375
        screen_width = self.app.winfo_screenwidth()
        screen_height = self.app.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.app.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Create frame to hold all widgets
        self.app.frame = customtkinter.CTkFrame(master=self.app)
        self.app.frame.pack(pady=20, padx=60, fill="both", expand=True)

        # Add widgets to the frame
        self.add_widgets()

    def add_widgets(self) -> None:
        """
        Adds widgets to the application window.

        This method creates and configures labels, buttons, and date entry fields
        for the user interface.
        """
        # Title label
        self.app.title_label = customtkinter.CTkLabel(
            master=self.app.frame,
            text="Schedule Builder",
            font=(self.app.STANDARD_FONT, 24),
        )
        self.app.title_label.pack(pady=20)

        # Start date label and entry
        self.app.start_date_label = customtkinter.CTkLabel(
            master=self.app.frame, text="START DATE", font=(self.app.STANDARD_FONT, 14)
        )
        self.app.start_date_label.pack()
        self.app.start_date_entry = DateEntry(
            master=self.app.frame,
            selectmode="day",
            locale="en_US",
            date_pattern="MM/dd/yyyy",
            font=(self.app.STANDARD_FONT, 12),
        )
        self.app.start_date_entry.pack(pady=(0, 10))

        # End date label and entry
        self.app.end_date_label = customtkinter.CTkLabel(
            master=self.app.frame, text="END DATE", font=(self.app.STANDARD_FONT, 14)
        )
        self.app.end_date_label.pack()
        self.app.end_date_entry = DateEntry(
            master=self.app.frame,
            selectmode="day",
            locale="en_US",
            date_pattern="MM/dd/yyyy",
            font=(self.app.STANDARD_FONT, 12),
        )
        self.app.end_date_entry.pack(pady=(0, 10))

        # Create button
        self.app.create_button = customtkinter.CTkButton(
            master=self.app.frame,
            text="CREATE",
            command=self.event_handler.handle_create_button_click,
            font=(self.app.STANDARD_FONT, 14),
        )
        self.app.create_button.pack(pady=10)

        # Confirmation label
        self.app.confirmation_label = customtkinter.CTkLabel(
            master=self.app.frame,
            text="",
            font=(self.app.STANDARD_FONT, self.app.CONFIRMATION_LABEL_FONT_SIZE),
            wraplength=350,
        )
        self.app.confirmation_label.pack(pady=5)

        # Schedule details ouput label
        self.app.output_link_label = customtkinter.CTkLabel(
            master=self.app.frame,
            text="",
            font=(
                self.app.STANDARD_FONT,
                self.app.CONFIRMATION_LABEL_FONT_SIZE,
                "underline",
            ),
            text_color="#4682B4",
            cursor="hand2",
            wraplength=350,
        )
        self.app.output_link_label.pack(pady=5)
