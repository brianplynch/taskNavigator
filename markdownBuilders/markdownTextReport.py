from artifacts.artifact import Artifact
from reports.reportBuilder import Report
from fileio.files import output_to_file
from reports.results_report import generate_results_report
from timeStamps.dateStamp import DateStamp


def build_markdown_text_report(report: Report):
    report_text: str = ""
    report_text += f"{'#' * report.level} {report.heading_text}\n\n"
    report_text += f"{report.description}\n\n"
    for section in report.subsections:
        report_text += build_markdown_text_report(section)
    return report_text


def output_results_report(root_folder: str, date_stamps: list[DateStamp], top_level_artifact: Artifact) -> None:
    report = generate_results_report(date_stamps, top_level_artifact)
    report_text = build_markdown_text_report(report)
    output_to_file(root_folder, "Results Report.md", report_text)

