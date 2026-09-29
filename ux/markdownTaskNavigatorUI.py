"""
"""

from pathlib import Path
from tkinter import Tk, Frame, TclError
import logging
import os
from dataclasses import dataclass
from resources.resource import Resource
from resources.resourceSet import ResourceSet
from artifacts.artifact import Artifact
from artifacts.process import Process
from artifacts.role import Role
from artifacts.responsibility import Responsibility
from artifacts.activity import Activity
from artifacts.task import Task
from identifiers.identifier import Identifier
from reports.results_report import generate_task_summary_report, generate_project_summary_report
from fileio.files import output_to_file
from markdownBuilders.markdownTextReport import build_markdown_text_report
from markdownBuilders.artifactBuilderMarkdown import ArtifactBuilderMarkdown
from markdownBuilders.markdownTextReport import output_results_report
from ux.filteredListFrame import FilteredListFrame, distribute_rows_and_columns
from timeStamps.dateStamp import DateStamp
from fileio.files import open_folder


# Create action commands for selected item

# OPEN
def open_src_command(filtered_list_frame: FilteredListFrame) -> None:
    filtered_list_frame.selected_item_object.open_source_file()
    

def open_folder_command(filtered_list_frame: FilteredListFrame) -> None:
    filtered_list_frame.selected_item_object.open_project_folder()
    

def open_wi_command(filtered_list_frame: FilteredListFrame) -> None:
    filtered_list_frame.selected_item_object.open_work_instruction_file()

def open_best_practices_command(filtered_list_frame: FilteredListFrame) -> None:
    filtered_list_frame.selected_item_object.open_best_practices_file()

def open_client_command(filtered_list_frame: FilteredListFrame) -> None:
    if filtered_list_frame.selected_item_object.client.is_null():
        filtered_list_frame.display_message_to_user("No Client")
    else:
        client = filtered_list_frame.selected_item_object.get_client_artifact()
        client.open_source_file()


def open_proxy_command(filtered_list_frame: FilteredListFrame) -> None:
    if filtered_list_frame.selected_item_object.proxy.is_null():
        filtered_list_frame.display_message_to_user("No Proxy")
    else:
        proxy = filtered_list_frame.selected_item_object.get_proxy_artifact()
        proxy.open_source_file()


# MARKUP
def send_res_to_parent_command(filtered_list_frame: FilteredListFrame) -> None:
    filtered_list_frame.selected_item_object.send_resources_to_parent()
    

def send_del_to_parent_command(filtered_list_frame: FilteredListFrame) -> None:
    filtered_list_frame.selected_item_object.send_deliverables_to_parent()
    

def send_res_to_children_command(filtered_list_frame: FilteredListFrame) -> None:
    filtered_list_frame.selected_item_object.send_resources_to_children()
    

def send_del_to_children_command(filtered_list_frame: FilteredListFrame) -> None:
    filtered_list_frame.selected_item_object.send_deliverables_to_children()
    

def add_dropped_deliverable_command(filtered_list_frame: FilteredListFrame) -> None:
    """add_dropped_deliverable"""
    # Parse input
    #    deliverable name:description
    input_text = filtered_list_frame.get_text_input()
    if chr(10) in input_text:
        filtered_list_frame.display_message_to_user("Only 1 line-item allowed at a time")
    name: str
    line_item_text: str
    line_item: tuple[str,str]
    name, line_item_text = input_text.split(":", maxsplit=1)
    line_item = [tuple(line_item_text.split("||", maxsplit=1))]
    
    filtered_list_frame.selected_item_object.add_deliverable(Resource(name, line_item))
    

def show_deliverables(filtered_list_frame: FilteredListFrame) -> None:
    deliverables = filtered_list_frame.selected_item_object.deliverables.show_names()
    filtered_list_frame.display_message_to_user(":\n".join(deliverables))

def send_wa_to_children_command(filtered_list_frame: FilteredListFrame) -> None:
    """send_work_authorization_to_children"""
    filtered_list_frame.selected_item_object.send_work_authorization_to_open_children()
    

def lesson_learned_command(filtered_list_frame: FilteredListFrame) -> None:
    """lesson_learned"""
    filtered_list_frame.selected_item_object.lesson_learned(filtered_list_frame.get_text_input())
    

# STATE
def start_command(filtered_list_frame: FilteredListFrame) -> None:
    #start
    filtered_list_frame.selected_item_object.start()
    

def complete_command(filtered_list_frame: FilteredListFrame) -> None:
    #complete
    filtered_list_frame.selected_item_object.complete()
    

def block_command(filtered_list_frame: FilteredListFrame) -> None:
    #block
    filtered_list_frame.selected_item_object.block()
    

def cancel_command(filtered_list_frame: FilteredListFrame) -> None:
    #cancel
    filtered_list_frame.selected_item_object.cancel()
    

def continual_command(filtered_list_frame: FilteredListFrame) -> None:
    #continual
    filtered_list_frame.selected_item_object.continual()
    

# NEW CHILD

def create_new_child(filtered_list_frame: FilteredListFrame) -> None:
    filtered_list_frame.selected_item_object.new_child(filtered_list_frame.get_text_input())
    filtered_list_frame.reload()
    filtered_list_frame.child_filtered_list_frame.reload()


def create_new_children_from_breakdown(filtered_list_frame: FilteredListFrame) -> None:
    activity: Activity = filtered_list_frame.selected_item_object
    activity.new_children_from_work_breakdown()
    filtered_list_frame.reload()
    filtered_list_frame.child_filtered_list_frame.reload()


def log_result_command(filtered_list_frame: FilteredListFrame) -> None:
    #new_result
    input_text = filtered_list_frame.get_text_input()
    filtered_list_frame.selected_item_object.new_result(input_text)


def log_previous_result_command(filtered_list_frame: FilteredListFrame) -> None:
    #previous_result
    input_text = filtered_list_frame.get_text_input()
    filtered_list_frame.selected_item_object.previous_result(input_text)
    

def log_next_result_command(filtered_list_frame: FilteredListFrame) -> None:
    #next_result
    input_text = filtered_list_frame.get_text_input()
    filtered_list_frame.selected_item_object.next_result(input_text)
    

def backfill_timestamps_command(filtered_list_frame: FilteredListFrame) -> None:
    #backfill_timestamps
    input_text = filtered_list_frame.get_text_input()
    filtered_list_frame.selected_item_object.backfill_timestamps(input_text)


def start_link_from_proxy(filtered_list_frame: FilteredListFrame) -> None:
    """the proxy artifact is an activity"""
    proxy_object = filtered_list_frame.selected_item_object
    ProxyLink.set_link(proxy_object)


def link_to_client(filtered_list_frame: FilteredListFrame) -> None:
    """this action is performed by the proxy artifact (activity)
    after a link has been started from the client (task)"""
    proxy_object = filtered_list_frame.selected_item_object
    client_link = ClientLink.consume_link()
    if not client_link:
        filtered_list_frame.display_message_to_user(f"A client (task) artifact must be selected first")
    try:
        proxy_object.set_client(client_link)
    except RuntimeError as rte:
        filtered_list_frame.display_message_to_user("".join(rte.args))

def start_link_from_client(filtered_list_frame: FilteredListFrame) -> None:
    """the client artifact is a task"""
    client_object = filtered_list_frame.selected_item_object
    ClientLink.set_link(client_object)


def link_to_proxy(filtered_list_frame: FilteredListFrame) -> None:
    """this action is performed by the client artifact (task)
    after a link has been started from the proxy (activity)"""
    client_object = filtered_list_frame.selected_item_object
    proxy_link = ProxyLink.consume_link()
    if not proxy_link:
        filtered_list_frame.display_message_to_user(f"A proxy (activity) artifact must be selected first")
    try:
        client_object.set_proxy(proxy_link)
    except RuntimeError as rte:
        filtered_list_frame.display_message_to_user("".join(rte.args))

# REPORTS
def hours_command(filtered_list_frame: FilteredListFrame) -> None:
    hours = filtered_list_frame.selected_item_object.get_hours()
    filtered_list_frame.display_message_to_user(f"Hours Spent: {hours: .1f}")


def hours_today(filtered_list_frame: FilteredListFrame) -> None:
    logging.debug("hours_today")
    selected_artifact_resultset = filtered_list_frame.selected_item_object.get_rolled_up_results()
    filtered_resultset = selected_artifact_resultset.filter(time_stamp_value = [DateStamp.today()])
    hours = filtered_resultset.total_hours()
    filtered_list_frame.display_message_to_user(f"Hours Today: {hours: .1f}")


def hours_this_week(filtered_list_frame: FilteredListFrame) -> None:
    logging.debug("hours_this_week")
    selected_artifact_resultset = filtered_list_frame.selected_item_object.get_rolled_up_results()
    filtered_resultset = selected_artifact_resultset.filter(time_stamp_value = DateStamp.this_week_stamps())
    hours = filtered_resultset.total_hours()
    filtered_list_frame.display_message_to_user(f"Hours This Week: {hours: .1f}")


def results_day(filtered_list_frame: FilteredListFrame) -> None:
    #if day provided use it, else use today
    input_text = filtered_list_frame.get_text_input()
    try:
        date_stamp = DateStamp.parse(input_text)
    except ValueError as err:
        date_stamp = DateStamp.today()

    if date_stamp.is_null():
        date_stamp = DateStamp.today()
    selected_artifact = filtered_list_frame.selected_item_object
    if not isinstance(selected_artifact, Artifact):
        raise RuntimeError
    reports_path = Path(selected_artifact.builder.vault).joinpath("reports")
    open_folder(selected_artifact.builder.vault, "reports")
    date_stamps = [date_stamp]

    output_results_report(reports_path, date_stamps, selected_artifact)


def results_week(filtered_list_frame: FilteredListFrame) -> None:
    #if day provided use it, else use today
    input_text = filtered_list_frame.get_text_input()
    try:
        date_stamp = DateStamp.parse(input_text)
    except ValueError as err:
        date_stamp = DateStamp.today()

    if date_stamp.is_null():
        date_stamp = DateStamp.today()
    selected_artifact = filtered_list_frame.selected_item_object
    if not isinstance(selected_artifact, Artifact):
        raise RuntimeError
    reports_path = Path(selected_artifact.builder.vault).joinpath("reports")
    open_folder(selected_artifact.builder.vault, "reports")
    date_stamps = DateStamp.week_of_stamps(date_stamp.datetime())

    output_results_report(reports_path, date_stamps, selected_artifact)


def task_summary_report(filtered_list_frame: FilteredListFrame) -> None:
    selected_artifact = filtered_list_frame.selected_item_object
    reports_path = Path(selected_artifact.builder.vault).joinpath("reports")
    task_summary_report = generate_task_summary_report(selected_artifact)
    task_summary_report_text = build_markdown_text_report(task_summary_report)
    output_to_file(reports_path, f"{selected_artifact.identifier.build()} Task Summary Report.md", task_summary_report_text)


def project_summary_report(filtered_list_frame: FilteredListFrame) -> None:
    selected_artifact = filtered_list_frame.selected_item_object
    reports_path = Path(selected_artifact.builder.vault).joinpath("reports")
    project_summary_report = generate_project_summary_report(selected_artifact)
    project_summary_report_text = build_markdown_text_report(project_summary_report)
    output_to_file(reports_path, f"{selected_artifact.identifier.build()} Project Summary Report.md", project_summary_report_text)


# Create action commands for listframe
def set_filter_pattern_command(filtered_list_frame: FilteredListFrame) -> None:
    #set_filter_pattern')
    """"""
    
def display_heading_message(filtered_list_frame: FilteredListFrame) -> None:
    filtered_list_frame.display_message_to_user('This is just a heading')
    

def proxy_hours_command(filtered_list_frame: FilteredListFrame) -> None:
    hours = filtered_list_frame.selected_item_object.get_proxy_hours()
    filtered_list_frame.display_message_to_user(f"Hours Spent: {hours: .1f}")


def select_artifact(filtered_list_frame: FilteredListFrame) -> None:
    # auto select the parent
    if filtered_list_frame.parent_filtered_list_frame:
        current_selected_artifact = filtered_list_frame.selected_item_object.identifier.build()
        parent_id_text = filtered_list_frame.selected_item_object.parent.build()
        filtered_list_frame.parent_filtered_list_frame.set_selected_item(parent_id_text)
        filtered_list_frame.set_selected_item(current_selected_artifact)
    
    # auto filter in-work children, alternately all children after a second click
    if filtered_list_frame.child_filtered_list_frame:
        children_artifacts = filtered_list_frame.selected_item_object.get_children_artifacts()
        if filtered_list_frame.child_filtered_list_frame.filtered_objects == children_artifacts:
            open_children = filtered_list_frame.selected_item_object.get_not_closed_children()
            filtered_list_frame.child_filtered_list_frame.set_filtered_list(open_children)
        else:
            if children_artifacts:
                filtered_list_frame.child_filtered_list_frame.set_filtered_list(children_artifacts)
            else:
                filtered_list_frame.child_filtered_list_frame.set_filtered_list([])


def reload_roles(filtered_list_frame: FilteredListFrame):
    try:
        current_selected_item = filtered_list_frame.selected_item_object
    except RuntimeError as er:
        if filtered_list_frame.all_objects:
            current_selected_item = filtered_list_frame.all_objects[0]
        else:
            return
    all_roles = current_selected_item.get_roles()
    filtered_list_frame.set_base_list(all_roles)
    filtered_list_frame.set_selected_item(current_selected_item)


def reload_responsibilities(filtered_list_frame: FilteredListFrame):
    try:
        current_selected_item = filtered_list_frame.selected_item_object
    except RuntimeError as er:
        if filtered_list_frame.all_objects:
            current_selected_item = filtered_list_frame.all_objects[0]
        else:
            return
    responsibilities = current_selected_item.get_responsibilities()
    filtered_list_frame.set_base_list(responsibilities)
    filtered_list_frame.set_selected_item(current_selected_item)


def reload_activities(filtered_list_frame: FilteredListFrame):
    try:
        current_selected_item = filtered_list_frame.selected_item_object
    except RuntimeError as er:
        if filtered_list_frame.all_objects:
            current_selected_item = filtered_list_frame.all_objects[0]
        else:
            return
    all_activities = current_selected_item.get_activities()
    filtered_list_frame.set_base_list(all_activities)
    filtered_list_frame.set_selected_item(current_selected_item)


def reload_tasks(filtered_list_frame: FilteredListFrame):
    try:
        current_selected_item = filtered_list_frame.selected_item_object
    except RuntimeError as er:
        if filtered_list_frame.all_objects:
            current_selected_item = filtered_list_frame.all_objects[0]
        else:
            return
    all_tasks = current_selected_item.get_tasks()
    filtered_list_frame.set_base_list(all_tasks)
    filtered_list_frame.set_selected_item(current_selected_item)


class Link:
    """behaves like a singleton"""

    link: Artifact = None

    @classmethod
    def set_link(cls, link: Artifact) -> None:
        cls.link = link
        logging.debug(f"{cls.__name__}  link created: {str(link)}")

    @classmethod
    def consume_link(cls) -> Identifier:
        """get the link identifier and then clear the link attribute so that it is not accidentally consumed for another link"""
        link = cls.link
        cls.link = None

        logging.debug(f"{cls.__name__} link consumed: {str(link)}")
        return link


class ProxyLink(Link):
    ...


class ClientLink(Link):
    ...


@dataclass(frozen=True)
class WindowGeometry:
    width: int
    height: int
    # window_alignment: Tuple(top/bottom/center, Left/right/center)  default is bottom-right


def tk_callback_exception_handler(exc_type, exc_value, exc_traceback):
    logging.error("Unhandled exception in Task Navigator Tk Inter callback: ", exc_info=(exc_type, exc_value, exc_traceback))


class MainApplication:
    
    def __init__(self, vault: str, top_level_file: str, installation_path: Path, window_geometry: WindowGeometry):
        # Configure the artifact classes
        artifact_builder = ArtifactBuilderMarkdown(vault)

        Process.builder = artifact_builder
        Process.set_child_type(Role)

        Role.builder = artifact_builder
        Role.set_child_type(Responsibility)

        Responsibility.builder = artifact_builder
        Responsibility.set_child_type(Activity)
        
        Activity.builder = artifact_builder
        Activity.set_child_type(Task)

        Task.builder = artifact_builder
        # task has no child type (no children artifacts)

        # initialize the top level process
        top_level_process_identifier = Identifier(top_level_file)
        top_level_process = Process.load(top_level_process_identifier)

        # Setup the root TK application
        self.root = Tk()
        self.root.report_callback_exception = tk_callback_exception_handler
        self.root.title("Task Navigator")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = window_geometry.width
        window_height = window_geometry.height
        x_offset = screen_width - window_width
        y_offset = screen_height - window_height
        self.root.geometry(f"{window_width}x{window_height}+{x_offset}+{y_offset}")

        if os.name == "nt":
            try:
                self.root.iconbitmap(str(installation_path.joinpath("icon", "icon.ico")))
            except TclError:
                pass

            import ctypes
            app_id: str = "mycompany.myproduct.subproduct.version"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

        main_frame = Frame(self.root)

        proc_selector = FilteredListFrame(main_frame, [top_level_process])
        role_selector = FilteredListFrame(main_frame, top_level_process.get_roles())
        resp_selector = FilteredListFrame(main_frame, top_level_process.get_responsibilities())
        acts_selector = FilteredListFrame(main_frame, top_level_process.get_activities())
        task_selector = FilteredListFrame(main_frame, top_level_process.get_tasks())

        proc_selector.set_child_filtered_list_frame(role_selector)
        role_selector.set_child_filtered_list_frame(resp_selector)
        resp_selector.set_child_filtered_list_frame(acts_selector)
        acts_selector.set_child_filtered_list_frame(task_selector)

        proc_selector.bind_reload(lambda filtered_list_frame: None)
        role_selector.bind_reload(reload_roles)
        resp_selector.bind_reload(reload_responsibilities)
        acts_selector.bind_reload(reload_activities)
        task_selector.bind_reload(reload_tasks)

        distribute_rows_and_columns(main_frame, [10, 10, 20, 25, 35], [1], min_height=100)

        proc_selector.grid(row=0, column=0, sticky='nsew')
        role_selector.grid(row=1, column=0, sticky='nsew')
        resp_selector.grid(row=2, column=0, sticky='nsew')
        acts_selector.grid(row=3, column=0, sticky='nsew')
        task_selector.grid(row=4, column=0, sticky='nsew')

        # PROCESS SELECTOR MENU
        proc_selector.register_menu_function("OPEN",                  display_heading_message)
        proc_selector.register_menu_function("    Note",              open_src_command)
        proc_selector.register_menu_function("NEW",                   display_heading_message)
        proc_selector.register_menu_function("    Role",              create_new_child)
        proc_selector.register_menu_function("REPORTS",               display_heading_message)
        proc_selector.register_menu_function("    Hours This Day",    hours_today)
        proc_selector.register_menu_function("    Hours This Week",   hours_this_week)
        proc_selector.register_menu_function("    Results This Day",   results_day)
        proc_selector.register_menu_function("    Results This Week",   results_week)
        
        proc_selector.bind_filtered_list_left_click(lambda *args: print("Process Selected"))
        proc_selector.bind_filtered_list_double_click(open_src_command)
        proc_selector.bind_filtered_list_middle_click(lambda *args: print("Tried to run: proc_selector.bind_filtered_list_middle_click\n... but nothing was defined"))
        proc_selector.bind_registered_actions_to_dropdown()
        
        # ROLES SELECTOR MENU
        role_selector.register_menu_function("OPEN",                  lambda *args: print(""))
        role_selector.register_menu_function("    Note",              open_src_command)

        role_selector.register_menu_function("NEW",                   display_heading_message)
        role_selector.register_menu_function("    Responsibility",    create_new_child)

        role_selector.register_menu_function("REPORTS",               display_heading_message)
        role_selector.register_menu_function("    Hours",             hours_command)

        role_selector.bind_filtered_list_left_click(select_artifact)
        role_selector.bind_filtered_list_double_click(open_src_command)
        role_selector.bind_filtered_list_middle_click(lambda *args: print("Tried to run: role_selector.bind_filtered_list_middle_click\n... but nothing was defined"))
        role_selector.bind_registered_actions_to_dropdown()

        # RESPONSIBILITY SELECTOR MENU
        resp_selector.register_menu_function("OPEN",                    lambda *args: print(""))
        resp_selector.register_menu_function("    Note",                open_src_command)
        resp_selector.register_menu_function("    Open Best Practices", open_best_practices_command)

        resp_selector.register_menu_function("MARKUP",               display_heading_message)
        resp_selector.register_menu_function("    Send Work Authorization to Children", send_wa_to_children_command)

        resp_selector.register_menu_function("NEW",                   display_heading_message)
        resp_selector.register_menu_function("    Activity",          create_new_child)

        resp_selector.register_menu_function("REPORTS",               display_heading_message)
        resp_selector.register_menu_function("    Hours",             hours_command)

        resp_selector.bind_filtered_list_left_click(select_artifact)
        resp_selector.bind_filtered_list_double_click(open_src_command)
        resp_selector.bind_filtered_list_middle_click(lambda *args: print("Tried to run: resp_selector.bind_filtered_list_middle_click\n... but nothing was defined"))
        resp_selector.bind_registered_actions_to_dropdown()

        # ACTIVITY SELECTOR MENU
        acts_selector.register_menu_function("OPEN",                  lambda *args: print(""))
        acts_selector.register_menu_function("    Note",              open_src_command)
        acts_selector.register_menu_function("    Folder",            open_folder_command)
        acts_selector.register_menu_function("    Show Opened Note",  open_src_command)
        acts_selector.register_menu_function("    Open Client",        open_client_command)

        acts_selector.register_menu_function("MARKUP",                display_heading_message)
        acts_selector.register_menu_function("    Send Resources to Tasks",                   lambda x: print(x))
        acts_selector.register_menu_function("    Send Deliverables to Tasks",                lambda x: print(x))
        acts_selector.register_menu_function("    Send Work Authorization to Children", send_wa_to_children_command)

        acts_selector.register_menu_function("STATE",                 display_heading_message)
        acts_selector.register_menu_function("    Start",             start_command)
        acts_selector.register_menu_function("    Block",             block_command)
        acts_selector.register_menu_function("    Cancel",            cancel_command)
        acts_selector.register_menu_function("    Continual",         continual_command)
        acts_selector.register_menu_function("    Complete",          complete_command)

        acts_selector.register_menu_function("NEW",                   display_heading_message)
        acts_selector.register_menu_function("    Task",              create_new_child)
        acts_selector.register_menu_function("    Tasks from Work Breakdown", create_new_children_from_breakdown)
        acts_selector.register_menu_function("    Set as a Proxy Activity", start_link_from_proxy)
        acts_selector.register_menu_function("    Link to Selected Client", link_to_client)
        
        acts_selector.register_menu_function("REPORTS",               display_heading_message)
        acts_selector.register_menu_function("    Hours",             hours_command)
        acts_selector.register_menu_function("    Project Hours",       proxy_hours_command)
        acts_selector.register_menu_function("    Task Summary",       task_summary_report)
        acts_selector.register_menu_function("    Project Summary",       project_summary_report)


        acts_selector.bind_filtered_list_left_click(select_artifact)
        acts_selector.bind_filtered_list_double_click(open_src_command)
        acts_selector.bind_filtered_list_middle_click = lambda *args: print("Tried to run: acts_selector.bind_filtered_list_middle_click\n... but nothing was defined")
        acts_selector.bind_registered_actions_to_dropdown()

        # TASK SELECTOR MENU
        task_selector.register_menu_function("OPEN",                  lambda *args: print(""))
        task_selector.register_menu_function("    Note",              open_src_command)
        task_selector.register_menu_function("    Folder",            open_folder_command)
        task_selector.register_menu_function("    Show Opened Note",  open_src_command)
        task_selector.register_menu_function("    Work Instructions", open_wi_command)
        task_selector.register_menu_function("    Open Proxy",        open_proxy_command)

        task_selector.register_menu_function("MARKUP",                            display_heading_message)
        task_selector.register_menu_function("    Send Deliverables to Activity", send_del_to_parent_command)
        task_selector.register_menu_function("    Send Resources to Activity",    send_res_to_parent_command)
        task_selector.register_menu_function("    Add Dropped Deliverable",       add_dropped_deliverable_command)
        task_selector.register_menu_function("    Show Deliverables",             show_deliverables)
        
        task_selector.register_menu_function("    Lesson Learned",                lesson_learned_command)

        task_selector.register_menu_function("STATE",                 display_heading_message)
        task_selector.register_menu_function("    Start",             start_command)
        task_selector.register_menu_function("    Block",             block_command)
        task_selector.register_menu_function("    Cancel",            cancel_command)
        task_selector.register_menu_function("    Continual",         continual_command)
        task_selector.register_menu_function("    Complete",          complete_command)
        
        task_selector.register_menu_function("NEW",                   display_heading_message)
        task_selector.register_menu_function("    Result",            log_result_command)
        task_selector.register_menu_function("    Previous Result",   log_previous_result_command)
        task_selector.register_menu_function("    Backfill Result",    backfill_timestamps_command)
        task_selector.register_menu_function("    Next Result",       log_next_result_command)
        task_selector.register_menu_function("    Set as a Client Task", start_link_from_client)
        task_selector.register_menu_function("    Link to Selected Proxy", link_to_proxy)

        task_selector.register_menu_function("REPORTS",               display_heading_message)
        task_selector.register_menu_function("    Hours",             hours_command)
        task_selector.register_menu_function("    Proxy Hours",       proxy_hours_command)

        task_selector.bind_filtered_list_left_click(select_artifact)
        task_selector.bind_filtered_list_double_click(open_src_command)
        task_selector.bind_filtered_list_middle_click = lambda *args: print("Tried to run: task_selector.bind_filtered_list_middle_click\n... but nothing was defined")
        task_selector.bind_registered_actions_to_dropdown()
        
        
        self.root.frame = main_frame
        self.root.frame.grid(row=0, column=0,sticky="NSEW")
        distribute_rows_and_columns(self.root.frame, [1], [1], min_height=100)
        distribute_rows_and_columns(self.root, [1], [1], min_height=100)

    def start(self):
        self.root.mainloop()

