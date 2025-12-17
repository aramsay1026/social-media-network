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
    # get_friends_of_friends: O(V + E)

    def __init__(self):
        self.profiles = LinkedDictionary()   # name -> UserProfile
        self.graph = UndirectedGraph()       # relationships

    def add_profile(self, name, location, relationship_status, age,
                    occupation, astrological_sign, status=""):
        if self.profiles.get_value(name) is not None:
            return False

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
        # Remove the profile from the dictionary and rebuild the graph

        if self.profiles.get_value(name) is None:
            return False

        self.profiles.remove(name)

        remaining_names = self.profiles.get_keys()
        old_edges = self.graph.get_edges()

        self.graph.clear()
        for n in remaining_names:
            self.graph.add_vertex(n)

        for u, v, w in old_edges:
            if u != name and v != name:
                self.graph.add_edge(u, v, w)

        for n in remaining_names:
            profile = self.profiles.get_value(n)
            if profile is not None:
                profile.remove_friend(name)

        return True

    def connect_profiles(self, name1, name2, weight=0):
        # Create a friendship connection between two profiles

        p1 = self.profiles.get_value(name1)
        p2 = self.profiles.get_value(name2)

        if p1 is None or p2 is None:
            return False

        self.graph.add_edge(name1, name2, weight)
        p1.add_friend(name2)
        p2.add_friend(name1)

        return True

    def display_profiles(self):
        # Returns all profile names
        return self.profiles.get_keys()

    def display_profile_details(self, name):
        profile = self.profiles.get_value(name)
        if profile is None:
            print("Profile not found.")
            return
        profile.print_details()

    def get_friends_of_friends(self, name):
        # Friends-of-friends = neighbors of neighbors minus direct friends

        if not self.graph.contains(name):
            return []

        user_vertex = self.graph.get_vertex(name)
        if user_vertex is None:
            return []

        direct_friends = set(nbr.get_id() for nbr in user_vertex.get_connections())
        fof = set()

        for friend_name in direct_friends:
            friend_vertex = self.graph.get_vertex(friend_name)
            if friend_vertex is None:
                continue
            for nbr in friend_vertex.get_connections():
                fof.add(nbr.get_id())

        fof.discard(name)
        fof -= direct_friends

        return sorted(fof)

    def read_profiles_from_csv(self, file_path):
        # Expected header:
        # name,status,picture,location,relationship_status,age,occupation,astrological_sign,friends
        # friends column uses | like: Bob|Charlie

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
                        name,
                        location,
                        relationship_status,
                        age,
                        occupation,
                        astrological_sign,
                        status
                    )

        for row in rows:
            name = row.get("name", "").strip()
            friends_str = row.get("friends", "").strip()
            if not name or not friends_str:
                continue

            for friend in friends_str.split("|"):
                friend = friend.strip()
                if self.profiles.get_value(friend) is not None:
                    self.connect_profiles(name, friend)

    def create_user_graph(self, current_user, depth=1, out_path="AliceNetwork"):
        # Creates a graph of the current user's network within N hops
        # Tries to output PNG using graphviz, otherwise writes DOT

        if not self.graph.contains(current_user):
            print("Current user not found in graph.")
            return None

        nodes = {current_user}
        frontier = {current_user}
        edges_list = self.graph.get_edges()
        edges = []
        for _ in range(depth):
            next_frontier = set()
            for name in frontier:
                vertex = self.graph.get_vertex(name)
                vertex_id = vertex.get_id()
                if vertex is None:
                    continue
                for nbr in vertex.get_connections():
                    nbr_name = nbr.get_id()
                    if nbr_name not in nodes:
                        nodes.add(nbr_name)
                        next_frontier.add(nbr_name)
                    if (vertex_id,nbr_name,0) in edges_list:
                        edges.append((vertex_id,nbr_name,0))
            frontier = next_frontier

        try:
            from graphviz import Digraph

            g = Digraph("Network", format="png")
            g.attr(label=f"{current_user}'s Network (depth={depth})", labelloc="t")

            for n in sorted(nodes):
                g.node(n)

            drawn = set()
            for u, v, w in edges:
                g.edge(u, v, label=str(w) if w not in (None, 0) else None)
                drawn.add((u, v))
                # Only draw reverse edge if it exists in the data
                if (v, u) in edges and (v, u) not in drawn:
                    g.edge(v, u, label=str(w) if w not in (None, 0) else None)
                    drawn.add((v, u))

            output_file = g.render(filename=out_path, cleanup=True)
            print("Wrote:", output_file)
            return output_file

        except Exception:
            dot_path = f"{out_path}.dot"
            with open(dot_path, "w", encoding="utf-8") as f:
                f.write("graph Network {\n")
                f.write(
                    f'  labelloc="t"; label="{current_user}\'s Network (depth={depth})";\n'
                )
                for n in sorted(nodes):
                    f.write(f'  "{n}";\n')
                for u, v, w in edges:
                    label = f' [label="{w}"]' if w not in (None, 0) else None
                    f.write(f'  "{u}" -- "{v}"{label};\n')
                f.write("}\n")

            print(f"Wrote DOT file: {dot_path}")
            print(f"dot -Tpng {dot_path} -o {out_path}.png")
            return dot_path
