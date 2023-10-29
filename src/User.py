from dateutil import parser

class User:
    def __init__(self, description, created, isBanned, externalAppDisplayName, hasVerifiedBadge, id, name, displayName):
        self.description = description
        self.created = created
        self.isBanned = isBanned
        self.externalAppDisplayName = externalAppDisplayName
        self.hasVerifiedBadge = hasVerifiedBadge
        self.id = id
        self.name = name
        self.displayName = displayName

    def to_dict(self):
        """
        Converts the User object to a dict for MongoDB
        """

        return {
            "description": self.description,
            "created": parser.parse(self.created),
            "isBanned": self.isBanned,
            "externalAppDisplayName": self.externalAppDisplayName,
            "hasVerifiedBadge": self.hasVerifiedBadge,
            "id": self.id,
            "name": self.name,
            "displayName": self.displayName
        }