""""""

from __future__ import annotations


class Report:
    def __init__(self, heading: str, level: int = 1, description: str = ""):
        self.heading_text: str = heading
        self.level: int = level
        self.description: str = description
        self.subsections: list[Report] = []

    def set_level(self, level: int) -> None:
        self.level = level
        for report in self.subsections:
            report.set_level(level + 1)

    def add_subsection(self, *subsection: Report):
        for report in subsection:
            report.set_level(self.level + 1)
            self.subsections.append(report)
