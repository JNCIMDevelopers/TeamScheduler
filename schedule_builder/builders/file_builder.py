# Standard Library Imports
import csv
import logging
import os
import sys
from datetime import date
from typing import List

# Local Imports
from ..builders.html_builder import HTMLBuilder
from ..models.event import Event
from ..models.person import Person
from ..models.role import Role


def resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource, works for development and for PyInstaller.

    Args:
        relative_path (str): The relative path to the resource.

    Returns:
        str: The absolute path to the resource.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def generate_team_schedule_html(
    start_date: date, end_date: date, events: List[Event], team: List[Person]
) -> str:
    """
    Generates an HTML document for a team schedule.

    Args:
        start_date (date): The start date of the schedule.
        end_date (date): The end date of the schedule.
        events (List[Event]): A list of events.
        team (List[Person]): A list of team members.

    Returns:
        str: The generated HTML document as a string.
    """
    builder = HTMLBuilder("Worship Schedule")

    # Adding CSS
    css = """
    body { font-family: Arial, sans-serif; }
    .link { display: block; margin-bottom: 20px; color: #0056b3; text-decoration: none; }
    .section { margin-bottom: 20px; }
    h2 { background-color: #f0f0f0; padding: 10px; border-radius: 5px; }
    h2, h3, h4 { text-transform: uppercase; font-weight: bold; }
    ul { list-style-type: none; padding: 0; }
    li, p { padding: 5px; border-bottom: 1px solid #ddd; }
    .back-to-top {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 50px;
        height: 50px;
        background-color: #007BFF;
        color: white;
        text-align: center;
        line-height: 50px;
        border-radius: 50%;
        text-decoration: none;
        font-size: 24px;
        transition: background-color 0.3s, transform 0.3s;
    }
    .back-to-top:hover {
        background-color: #0056b3;
        transform: translateY(-5px);
    }
    """
    builder.add_css(css)

    # Adding page links
    team_members_by_role_id = "roles"
    team_members_by_role_section_title = "Team Members by Role"
    team_member_details_id = "team"
    schedule_section_title = f"Team Schedule from {start_date.strftime('%B-%d-%Y')} to {end_date.strftime('%B-%d-%Y')}"
    events_id = "events"
    events_section_title = "Sunday Events"

    page_links = f"""

    <nav>
        <a class="link" href="#{team_members_by_role_id}">{team_members_by_role_section_title}</a>
        <a class="link" href="#{team_member_details_id}">{schedule_section_title}</a>
        <a class="link" href="#{events_id}">{events_section_title}</a>
    </nav>
    """
    builder.add_section(
        section_title="Jump to Section", content=page_links, id="nav-links"
    )

    # Adding team members by role
    role_content = ""
    for role in Role.get_schedule_order():
        members = [member.name for member in team if role in member.roles]
        role_content += f"<h3>Role: {role}</h3>"
        capable_members_content = builder.add_list(
            items=members, class_name="members-by-role"
        )
        role_content += capable_members_content
    builder.add_section(
        section_title=team_members_by_role_section_title,
        content=role_content,
        id=team_members_by_role_id,
    )

    # Adding team member details
    team_content = ""
    for member in team:
        member_name = f"<h3>{member.name}</h3>"
        member_details = str(member).split("\n")[1:]
        member_content = member_name
        member_content += builder.add_list(
            items=member_details, class_name="member-details"
        )
        team_content += member_content
    builder.add_section(
        section_title=schedule_section_title,
        content=team_content,
        id=team_member_details_id,
    )

    # Adding events
    events_content = ""
    event_headers = [
        "Preaching",
        "Assigned Roles",
        "Unassigned Roles",
        "Unassigned People",
    ]
    for event in events:
        event_details = str(event).split("\n")
        event_title = f"<h3>{event_details[0]}</h3>"
        event_details_elements = [element.strip() for element in event_details[1:]]
        event_details_html = [
            f"<h4>{detail}</h4>" if detail in event_headers else detail
            for detail in event_details_elements
        ]
        event_section = builder.add_list(
            items=event_details_html, class_name="event-details"
        )
        events_content += event_title
        events_content += event_section
    builder.add_section(
        section_title=events_section_title, content=events_content, id=events_id
    )

    # Adding scroll back to the top link
    scroll_back_to_top_link = "<a href='#' class='back-to-top'>&uarr;</a>"
    builder.body_content += scroll_back_to_top_link

    return builder.build_html()


def create_html(content: str, filepath: str) -> None:
    """
    Create a HTML file with the provided content.

    Args:
        content (str): The content to write to the file.
        filepath (str): The path to the file to create.

    Returns:
        None
    """
    with open(filepath, "w", newline="") as htmlfile:
        htmlfile.write(content)

    logging.info(f"HTML file '{filepath}' has been created.")


def get_schedule_data_for_csv(events: List[Event]) -> List[List[str]]:
    """
    Generate data for a CSV file containing the schedule details.

    Args:
        events (List[Event]): A list of event objects.

    Returns:
        List[List[str]]: A list of rows, where each row is a list of strings for the CSV file.
    """
    # Initialize the data list with headers
    data = [["Role"] + [event.date.strftime("%B %d, %Y") for event in events]]

    # Add preacher and graphics support
    preacher_row = ["PREACHER"]
    graphics_row = ["GRAPHICS"]
    for event in events:
        preacher = event.get_assigned_preacher
        preacher_row.append(preacher.name if preacher and preacher.name else "")
        graphics_row.append(
            preacher.graphics_support if preacher and preacher.graphics_support else ""
        )
    data.append(preacher_row)
    data.append(graphics_row)

    # Iterate through each role and populate with the assigned person for each event
    for role in Role.get_schedule_order():
        row = [role.value]
        for event in events:
            assigned_person = event.roles[role]
            row.append(assigned_person if assigned_person else "")
        data.append(row)

    return data


def create_csv(data: List[List[str]], filepath: str) -> None:
    """
    Create a CSV file with the provided data.

    Args:
        data (List[List[str]]): The data to write to the CSV file.
        filepath (str): The path to the file to create.

    Returns:
        None
    """
    with open(filepath, "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(data)

    logging.info(f"CSV file '{filepath}' has been created.")
