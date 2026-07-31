# The committee's fixed set of assignable positions, in official display order
# (used for the About Us committee listing — see MemberProfile.display_order).
# Free text is deliberately not allowed here: a fixed vocabulary keeps the public
# committee page and the admin UI in sync without relying on admins typing titles
# consistently.
COMMITTEE_POSITION_CHOICES = (
    "Advisors",
    "President",
    "Senior Vice President",
    "Vice President",
    "General Secretary",
    "Joint General Secretary",
    "Assistant General Secretary",
    "Organizing Secretary",
    "Assistant Organizing Secretary",
    "Publicity Secretary",
    "Sports Secretary",
    "Honorable Member",
    "Events Organizer",
    "General Member",
)

POSITION_DISPLAY_ORDER = {name: index for index, name in enumerate(COMMITTEE_POSITION_CHOICES)}
