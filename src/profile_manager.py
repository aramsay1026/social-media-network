# Worked on by: Amy Ramsay

import csv

from linked_adts import LinkedDictionary
from graph_adt import UndirectedGraph
from user_profile import UserProfile


class ProfileManager:
    # Runtime notes (high level):
    # add_profile: O(1) average
    # get_profile: O(1) average
    # connect_profiles: O(1) average
    # display_profiles: O(n)
    # get_friends_of_friends: O(V + E) in worst case (depends on network size)

    def __init__(self):
        self.profiles = LinkedDictionary()   # name -> UserProfile
        self.graph = UndirectedGraph()       # relationships

    def add_profile(self, name, location, relationship_status, age, occupation, astrological_sign, status=""):
        if self.profiles.get_value(name) is not None:
            return False  # profile already exists

        profile = UserProfile(
            name=name,
            location=location,
            relationship_status=relationship_status,
            age=age,
            occupation=occupation,
            astrological_sign=astrological_sign,
            status=status
        )

        self.profiles.add(name, profile)
        self.graph.add_vertex(name)
        return True

    def get_profile(self, name):
        return self.profiles.get_value(name)

    def remove_profile(self, name):
        # Remove the profile from the dictionary and remove their vertex from the graph.
        # Simplest safe approach is to rebuild the graph without that user.
        if self.profiles.get_value(name) is None:
            return False

        # Remove from profiles dictionary
        self.profiles.remove(name)

        # Rebuild graph from remaining profiles + their current edges
        remaining_names = self.profiles.get_keys()
        old_edges = self.graph.get_edges()

        self.graph.clear()
        for n in remaining_names:
            self.graph.add_vertex(n)

        for u, v, w in old_edges:
            if u != name and v != name and u in remaining_names and v in remaining_names:
                self.graph.add_edge(u, v, w)

        # Also remove from other profiles' friend lists (if you’re using it)
        for n in remaining_names:
            p = self.profiles.get_value(n)
            if p is not None:
                p.remove_friend(name)

        return True

    def connect_profiles(self, name1, name2, weight=0):
        # Create a friendship connection between two existing profiles.
        # weight is optional (extra credit uses 1 for close friend, 0 otherwise).

        p1 = self.profiles.get_value(name1)
        p2 = self.profiles.get_value(name2)

        if p1 is None or p2 is None:
            return False

        self.graph.add_edge(name1, name2, weight)

        # keep profile-level friend lists in sync (optional, but helpful)
        p1.add_friend(name2)
        p2.add_friend(name1)

        return True

    def display_profiles(self):
        # For the menu: you’ll ask BFS vs DFS elsewhere
       #  This just returns all profile names
        return self.profiles.get_keys()

    def display_profile_details(self, name):
        profile = self.profiles.get_value(name)
        if profile is None:
            print("Profile not found.")
            return
        profile.print_details()

    def get_friends_of_friends(self, name):
        # Friends-of-friends = (neighbors of neighbors) minus direct neighbors minus self.
        if not self.graph.contains(name):
            return []

        user_vertex = self.graph.get_vertex(name)
        if user_vertex is None:
            return []

        direct_friends = set([nbr.get_id() for nbr in user_vertex.get_connections()])
        fof = set()

        for friend_name in direct_friends:
            friend_vertex = self.graph.get_vertex(friend_name)
            if friend_vertex is None:
                continue
            for nbr in friend_vertex.get_connections():
                fof.add(nbr.get_id())

        # remove direct friends and the user
        fof.discard(name)
        fof = fof - direct_friends

        return sorted(list(fof))

    def read_profiles_from_csv(self, file_path):
       #  Expected header:
       # name,status,picture,location,relationship_status,age,occupation,astrological_sign,friends
       # friends column uses | like: Bob|Charlie

        # Pass 1: create all profiles
        rows = []
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
                name = row.get("name", "").strip()
                if not name:
                    continue

                status = row.get("status", "").strip()
                location = row.get("location", "").strip()
                relationship_status = row.get("relationship_status", "").strip()
                occupation = row.get("occupation", "").strip()
                astrological_sign = row.get("astrological_sign", "").strip()

                age_raw = row.get("age", "").strip()
                try:
                    age = int(age_raw) if age_raw else 0
                except ValueError:
                    age = 0

                if self.profiles.get_value(name) is None:
                    self.add_profile(
                        name=name,
                        location=location,
                        relationship_status=relationship_status,
                        age=age,
                        occupation=occupation,
                        astrological_sign=astrological_sign,
                        status=status
                    )

        # Pass 2: connect friends (only if friend exists in profiles)
        for row in rows:
            name = row.get("name", "").strip()
            friends_str = row.get("friends", "").strip()
            if not name or not friends_str:
                continue

            friend_names = [f.strip() for f in friends_str.split("|") if f.strip()]
            for friend in friend_names:
                if self.profiles.get_value(friend) is not None:
                    self.connect_profiles(name, friend, weight=0)

    def create_user_graph(self, current_user, depth=1):
        # TODO: build subgraph of nodes within 'depth' hops of current_user
        # TODO: render with graphviz (dot) to png
        pass
