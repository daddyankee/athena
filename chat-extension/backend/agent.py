from pydantic import BaseModel
from typing import List, Dict

class PageData(BaseModel):
    url: str
    headings: List[Dict]
    links: List[Dict]
    forms: List[Dict]
    inputs: List[Dict]
    scripts: List[Dict]
    styles: List[Dict]
    detectedDirectives: List[Dict]
    contentMetrics: Dict

class AnalysisResponse(BaseModel):
    summary: str
    actions: List[Dict]

async def analyze_page(data: PageData) -> AnalysisResponse:
    # Sample logic: count sections, detect forms with submit buttons
    has_form = len(data.forms) > 0
    headline_count = len(data.headings)
    link_count = len(data.links)
    form_actions = []
    if has_form:
        for form in data.forms:
            form_actions.append({
                "action": "inspect_form",
                "id": form.get("id"),
                "inputs": [i.get("name") for i in form.get("inputs", [])]
            })
    return AnalysisResponse(
        summary=f"Page has {headline_count} headings, {link_count} links, {len(data.forms)} forms.",
        actions=form_actions
    )
