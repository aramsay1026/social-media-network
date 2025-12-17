class UserProfile:
    # Runtime:
    # add_friend: O(1)
    # remove_friend: O(n)
    # get_friends: O(1)

    def __init__(self, name, location, relationship_status, age, occupation, astrological_sign, status="", picture=None):
        self.name = name
        self.location = location
        self.relationship_status = relationship_status
        self.age = age
        self.occupation = occupation
        self.astrological_sign = astrological_sign
        self.status = status
        self.picture = picture
        self.friends = []   # store friend names

    def get_name(self):
        return self.name

    def get_location(self):
        return self.location

    def get_relationship_status(self):
        return self.relationship_status

    def get_age(self):
        return self.age

    def get_occupation(self):
        return self.occupation

    def get_astrological_sign(self):
        return self.astrological_sign

    def get_status(self):
        return self.status

    def set_status(self, status):
        self.status = status

    def get_friends(self):
        return self.friends

    def add_friend(self, friend_profile):
        # friend_profile may be a name or a UserProfile
        friend_name = friend_profile.get_name() if hasattr(friend_profile, "get_name") else friend_profile
        if friend_name not in self.friends:
            self.friends.append(friend_name)

    def remove_friend(self, friend_profile):
        friend_name = friend_profile.get_name() if hasattr(friend_profile, "get_name") else friend_profile
        if friend_name in self.friends:
            self.friends.remove(friend_name)

    def print_details(self):
        print("Name:", self.name)
        print("Location:", self.location)
        print("Relationship Status:", self.relationship_status)
        print("Age:", self.age)
        print("Occupation:", self.occupation)
        print("Astrological Sign:", self.astrological_sign)
        print("Status:", self.status)
        print("Friends:", ", ".join(self.friends) if self.friends else "None")
