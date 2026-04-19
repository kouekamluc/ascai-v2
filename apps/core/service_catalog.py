"""
Fallback catalog data for association services and provider partnerships.
"""

DEFAULT_COMMUNITY_SERVICES = [
    {
        "title": "Embassy and consular file clinic",
        "category": "consular_support",
        "audience": "Cameroonians handling official files in Italy",
        "summary": (
            "Pre-checklists and guided support for consular card files, procurations, "
            "document legalisation, reddito attestations, and other embassy-bound documents."
        ),
        "access": "Member support",
        "delivery": "Checklist pack and appointment prep",
        "revenue": "Included in annual dues",
        "association_benefit": (
            "Keeps members paying annually for practical help they repeatedly need during the year."
        ),
    },
    {
        "title": "Reddito, CAF, and family paperwork desk",
        "category": "documentation",
        "audience": "Students, workers, and families",
        "summary": (
            "Orientation for CAF appointments, income documentation, family files, and "
            "supporting papers commonly requested for housing, benefits, and embassy procedures."
        ),
        "access": "Member support",
        "delivery": "Resource vault and group clinic",
        "revenue": "Included in annual dues + paid clinics",
        "association_benefit": (
            "Creates repeat participation through seasonal admin clinics tied to the academic and tax calendar."
        ),
    },
    {
        "title": "Residence and settlement support",
        "category": "arrival_support",
        "audience": "New arrivals and people regularising their stay",
        "summary": (
            "Guides for permesso renewals, comune registration, first-arrival orientation, "
            "and the local steps that usually slow down integration in Lazio."
        ),
        "access": "Member support",
        "delivery": "Starter pack and peer guidance",
        "revenue": "Included in annual dues",
        "association_benefit": (
            "Strengthens the first-year value proposition that turns new arrivals into paying members."
        ),
    },
    {
        "title": "Verified remittance partner referrals",
        "category": "money_transfer",
        "audience": "Members sending money home to Cameroon",
        "summary": (
            "A vetted partner lane for members looking for trusted money-transfer providers, "
            "with visibility into who is verified by the association before referrals are made."
        ),
        "access": "Member-only referrals",
        "delivery": "Verified partner directory",
        "revenue": "Partner listing fee",
        "association_benefit": (
            "Lets the association earn predictable partner revenue while solving a real diaspora need."
        ),
    },
    {
        "title": "CV, jobs, and business visibility support",
        "category": "career_business",
        "audience": "Graduates, workers, freelancers, and founders",
        "summary": (
            "Italian CV support, opportunity sharing, business spotlighting, and network-driven "
            "visibility for Cameroonians building careers or small businesses in Lazio."
        ),
        "access": "Member support",
        "delivery": "Workshops and profile exposure",
        "revenue": "Dues + event workshops",
        "association_benefit": (
            "Broadens the revenue base beyond students and keeps professionals engaged after graduation."
        ),
    },
    {
        "title": "Translation and file-running network",
        "category": "documentation",
        "audience": "People managing multilingual or time-sensitive paperwork",
        "summary": (
            "Trusted access to translators, document runners, and admin helpers who can "
            "support legalisation, certifications, and file preparation workflows."
        ),
        "access": "Member referrals and partner offers",
        "delivery": "Partner directory and referral flow",
        "revenue": "Partner listing fee",
        "association_benefit": (
            "Creates a marketplace-style premium layer the association can monetise responsibly."
        ),
    },
]


DEFAULT_PARTNER_OPPORTUNITIES = [
    {
        "title": "Money transfer operators",
        "summary": (
            "Providers sending funds to Cameroon can pay to be listed as verified partners "
            "and receive trusted visibility on the platform."
        ),
        "listing_fee_eur": "20",
        "value": "Visibility, trust badge, and member referrals",
    },
    {
        "title": "Translators and document facilitators",
        "summary": (
            "Professionals who help with translations, legalisation prep, or administrative file handling."
        ),
        "listing_fee_eur": "20",
        "value": "Access to members with urgent paperwork needs",
    },
    {
        "title": "Housing and relocation helpers",
        "summary": (
            "Relocation agents, room finders, and settlement helpers supporting newcomers in Lazio."
        ),
        "listing_fee_eur": "20",
        "value": "Qualified community demand during high-arrival periods",
    },
    {
        "title": "Travel, shipping, and event vendors",
        "summary": (
            "Partners handling airport pickups, parcel shipping, event services, or diaspora logistics."
        ),
        "listing_fee_eur": "20",
        "value": "Presence in front of a focused Cameroonian audience in Italy",
    },
]


DEFAULT_REVENUE_CHANNELS = [
    {
        "title": "Annual member dues",
        "summary": (
            "Members continue paying regular annual dues for practical support, resources, and community access."
        ),
    },
    {
        "title": "Verified partner listing fee",
        "summary": (
            "Service providers pay €20 per year to appear as association-verified partners on the platform."
        ),
    },
    {
        "title": "Admin clinics and themed workshops",
        "summary": (
            "The association can sell targeted sessions around reddito files, embassy preparation, CV support, and arrival admin."
        ),
    },
    {
        "title": "Sponsored visibility packages",
        "summary": (
            "Collaborators and diaspora-focused businesses can fund premium visibility around high-trust community services."
        ),
    },
]
