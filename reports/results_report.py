"""
results_report
"""

from artifacts.artifact import Artifact
from reports.reportBuilder import Report
from timeStamps.dateStamp import DateStamp
from timeStamps.timeStamp import TimeStamp


def generate_results_report(date_stamps: list[DateStamp], artifact: Artifact):
    """
    hours report
    accomplishments report
    estimate report
    """

    # get time stamps from date stamps
    time_stamps: list[TimeStamp] = []
    for date_stamp in date_stamps:
        time_stamps.extend(TimeStamp.generate_timestamps(date_stamp.datetime()))

    all_rolled_up_results = artifact.get_rolled_up_results()
    filtered_results = all_rolled_up_results.filter(time_stamps)

    # report of each time stamp and what task was performed and brief description
    time_stamp_report_contents: list[str] = list()
    for ts in time_stamps:
        wa = ""
        desc = ""
        result_at_ts = list(filter(lambda res: res.time_stamp == ts, filtered_results.result_set))
        if result_at_ts:
            wa = result_at_ts[0].work_authorization.build_reference()
            desc = result_at_ts[0].description.replace(chr(10)," ")
        time_stamp_report_line = f"{ts.build()}: {wa} - {desc}"
        time_stamp_report_contents.append(time_stamp_report_line)

    first_date = sorted(date_stamps)[0].build()
    last_date = sorted(date_stamps)[-1].build()

    results_report = Report("Results Report", 1, f"Provides the results for the period between {first_date} and {last_date}")

    total_hours_report = Report("Total Hours")
    total_hours_report.description = f"Total Hours: {filtered_results.total_hours():.2f}"
    results_report.add_subsection(total_hours_report)


    time_stamp_report = Report("Time Stamps")
    time_stamp_report.description = chr(10).join(sorted(time_stamp_report_contents))
    results_report.add_subsection(time_stamp_report)
    
    rolled_up_results = Report("Results Full Description")
    rolled_up_results.description = f"{filtered_results.build()}"
    results_report.add_subsection(rolled_up_results)

    return results_report


def generate_task_summary_report(artifact: Artifact) -> Report:
    task_summary_report = Report("Task Summary Report", 1, f"Collects the Descriptions of children tasks into a single report")
    tasks = artifact.get_children()
    for task in tasks:
        temp_report = Report(task.identifier.build(), 2, task.detail)
        task_summary_report.add_subsection(temp_report)
    return task_summary_report


def generate_project_summary_report(artifact: Artifact) -> Report:
    project_summary_report = Report("Project Summary Report", 1, f"Collects the Descriptions of children tasks and task-proxy activities into a single report")
    activity_report = Report(artifact.identifier.build(), 2, artifact.detail)
    project_summary_report.add_subsection(activity_report)
    tasks = artifact.get_children()
    for task in tasks:
        if not task.proxy.is_null():
            project_summary_report.add_subsection(generate_project_summary_report(task))
        temp_report = Report(task.identifier.build(), 3, task.detail)
        project_summary_report.add_subsection(temp_report)
    return project_summary_report
