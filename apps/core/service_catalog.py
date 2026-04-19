"""
Fallback catalog data for association services and provider partnerships.
"""
from django.utils.translation import gettext_lazy as _


DEFAULT_COMMUNITY_SERVICES = [
    {
        "title": _("Embassy and consular file clinic"),
        "category": _("Consular support"),
        "audience": _("Cameroonians handling official files in Italy"),
        "summary": _(
            "Pre-checklists and guided support for consular card files, procurations, "
            "document legalisation, reddito attestations, and other embassy-bound documents."
        ),
        "access": _("Member support"),
        "delivery": _("Checklist pack and appointment prep"),
        "revenue": _("Included in annual dues"),
        "association_benefit": _(
            "Keeps members paying annually for practical help they repeatedly need during the year."
        ),
    },
    {
        "title": _("Reddito, CAF, and family paperwork desk"),
        "category": _("Documentation"),
        "audience": _("Students, workers, and families"),
        "summary": _(
            "Orientation for CAF appointments, income documentation, family files, and "
            "supporting papers commonly requested for housing, benefits, and embassy procedures."
        ),
        "access": _("Member support"),
        "delivery": _("Resource vault and group clinic"),
        "revenue": _("Included in annual dues + paid clinics"),
        "association_benefit": _(
            "Creates repeat participation through seasonal admin clinics tied to the academic and tax calendar."
        ),
    },
    {
        "title": _("Residence and settlement support"),
        "category": _("Arrival support"),
        "audience": _("New arrivals and people regularising their stay"),
        "summary": _(
            "Guides for permesso renewals, comune registration, first-arrival orientation, "
            "and the local steps that usually slow down integration in Lazio."
        ),
        "access": _("Member support"),
        "delivery": _("Starter pack and peer guidance"),
        "revenue": _("Included in annual dues"),
        "association_benefit": _(
            "Strengthens the first-year value proposition that turns new arrivals into paying members."
        ),
    },
    {
        "title": _("Verified remittance partner referrals"),
        "category": _("Money transfer"),
        "audience": _("Members sending money home to Cameroon"),
        "summary": _(
            "A vetted partner lane for members looking for trusted money-transfer providers, "
            "with visibility into who is verified by the association before referrals are made."
        ),
        "access": _("Member-only referrals"),
        "delivery": _("Verified partner directory"),
        "revenue": _("Partner listing fee"),
        "association_benefit": _(
            "Lets the association earn predictable partner revenue while solving a real diaspora need."
        ),
    },
    {
        "title": _("CV, jobs, and business visibility support"),
        "category": _("Career and business"),
        "audience": _("Graduates, workers, freelancers, and founders"),
        "summary": _(
            "Italian CV support, opportunity sharing, business spotlighting, and network-driven "
            "visibility for Cameroonians building careers or small businesses in Lazio."
        ),
        "access": _("Member support"),
        "delivery": _("Workshops and profile exposure"),
        "revenue": _("Dues + event workshops"),
        "association_benefit": _(
            "Broadens the revenue base beyond students and keeps professionals engaged after graduation."
        ),
    },
    {
        "title": _("Translation and file-running network"),
        "category": _("Documentation"),
        "audience": _("People managing multilingual or time-sensitive paperwork"),
        "summary": _(
            "Trusted access to translators, document runners, and admin helpers who can "
            "support legalisation, certifications, and file preparation workflows."
        ),
        "access": _("Member referrals and partner offers"),
        "delivery": _("Partner directory and referral flow"),
        "revenue": _("Partner listing fee"),
        "association_benefit": _(
            "Creates a marketplace-style premium layer the association can monetise responsibly."
        ),
    },
]


DEFAULT_PARTNER_OPPORTUNITIES = [
    {
        "title": _("Money transfer operators"),
        "summary": _(
            "Providers sending funds to Cameroon can pay to be listed as verified partners "
            "and receive trusted visibility on the platform."
        ),
        "listing_fee_eur": "20",
        "value": _("Visibility, trust badge, and member referrals"),
    },
    {
        "title": _("Translators and document facilitators"),
        "summary": _(
            "Professionals who help with translations, legalisation prep, or administrative file handling."
        ),
        "listing_fee_eur": "20",
        "value": _("Access to members with urgent paperwork needs"),
    },
    {
        "title": _("Housing and relocation helpers"),
        "summary": _(
            "Relocation agents, room finders, and settlement helpers supporting newcomers in Lazio."
        ),
        "listing_fee_eur": "20",
        "value": _("Qualified community demand during high-arrival periods"),
    },
    {
        "title": _("Travel, shipping, and event vendors"),
        "summary": _(
            "Partners handling airport pickups, parcel shipping, event services, or diaspora logistics."
        ),
        "listing_fee_eur": "20",
        "value": _("Presence in front of a focused Cameroonian audience in Italy"),
    },
]


DEFAULT_REVENUE_CHANNELS = [
    {
        "title": _("Annual member dues"),
        "summary": _(
            "Members continue paying regular annual dues for practical support, resources, and community access."
        ),
    },
    {
        "title": _("Verified partner listing fee"),
        "summary": _(
            "Service providers pay EUR 20 per year to appear as association-verified partners on the platform."
        ),
    },
    {
        "title": _("Admin clinics and themed workshops"),
        "summary": _(
            "The association can sell targeted sessions around reddito files, embassy preparation, CV support, and arrival admin."
        ),
    },
    {
        "title": _("Sponsored visibility packages"),
        "summary": _(
            "Collaborators and diaspora-focused businesses can fund premium visibility around high-trust community services."
        ),
    },
]
