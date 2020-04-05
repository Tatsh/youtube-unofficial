from typing import Any, Iterable, Mapping, Sequence, Tuple

from typing_extensions import TypedDict


class FormattedTitle(TypedDict):
    simpleText: str


class GuideEntryDataDict(TypedDict):
    guideEntryId: str


class EntryDataDict(TypedDict):
    guideEntryData: GuideEntryDataDict


class GuideEntryRendererDict(TypedDict):
    entryData: EntryDataDict
    formattedTitle: FormattedTitle


class GuideCollapsibleEntryRendererDict(TypedDict):
    expandableItems: Sequence[Any]


class SectionItemDict(TypedDict):
    guideCollapsibleEntryRenderer: GuideCollapsibleEntryRendererDict
    guideEntryRenderer: GuideEntryRendererDict


class GuideCollapsibleSectionEntryRendererDict(TypedDict):
    sectionItems: Sequence[SectionItemDict]


class Item2Dict(TypedDict):
    guideCollapsibleSectionEntryRenderer: GuideCollapsibleSectionEntryRendererDict


class GuideSectionRenderDict(TypedDict):
    items: Sequence[Item2Dict]


class ItemDict(TypedDict):
    guideSectionRenderer: GuideSectionRenderDict


class GuideData(TypedDict):
    items: Sequence[ItemDict]
