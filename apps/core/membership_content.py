"""
Shared marketing copy for membership benefits and member-only resources.
"""
from django.utils.translation import gettext_lazy as _


MEMBERSHIP_BENEFIT_PILLARS = [
    {
        "eyebrow": _("Students"),
        "title": _("Academic survival toolkit"),
        "description": _(
            "Member dues unlock guided packs for enrollment, scholarships, DSU and "
            "ISEE paperwork, residence-permit admin, and the real deadlines that "
            "usually catch new students off guard."
        ),
    },
    {
        "eyebrow": _("Professionals"),
        "title": _("Career and relocation support"),
        "description": _(
            "Graduates, workers, and researchers get access to job-search resources, "
            "Italian CV guidance, qualification-recognition notes, and community "
            "introductions that help them settle faster."
        ),
    },
    {
        "eyebrow": _("Supporters"),
        "title": _("Community influence and belonging"),
        "description": _(
            "Non-students who join ASCAI strengthen the network while gaining practical "
            "association resources, event visibility, governance participation, and a "
            "clear place in the Cameroonian community in Lazio."
        ),
    },
]


MEMBER_RESOURCE_COLLECTIONS = [
    {
        "audience": _("For students"),
        "title": _("Arrival and campus starter vault"),
        "description": _(
            "Enrollment checklists, university admin templates, scholarship calendars, "
            "housing tips, and forms that reduce mistakes during the first year in Italy."
        ),
        "accent": "green",
    },
    {
        "audience": _("For graduates and workers"),
        "title": _("Career and professional growth kit"),
        "description": _(
            "Practical guides for job applications, Italian-style CVs, internships, "
            "qualification recognition, and networking opportunities inside the association."
        ),
        "accent": "red",
    },
    {
        "audience": _("For families and supporters"),
        "title": _("Community support and participation desk"),
        "description": _(
            "Association documents, trusted orientation resources, event access, and "
            "community pathways for people who want to contribute beyond student life."
        ),
        "accent": "yellow",
    },
]
