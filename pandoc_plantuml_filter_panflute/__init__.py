from panflute import toJSONFilter

from pandoc_plantuml_filter_panflute.filter import plantuml


def main():
    """Main"""
    toJSONFilter(plantuml)
