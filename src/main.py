from profile_manager import ProfileManager


def prompt_nonempty(msg):
    while True:
        val = input(msg).strip()
        if val:
            return val
        print("Please enter a value.")


def prompt_int(msg, min_val=None, max_val=None):
    while True:
        raw = input(msg).strip()
        try:
            val = int(raw)
        except ValueError:
            print("Please enter a valid number.")
            continue

        if min_val is not None and val < min_val:
            print(f"Enter a number >= {min_val}")
            continue
        if max_val is not None and val > max_val:
            print(f"Enter a number <= {max_val}")
            continue

        return val


def choose_traversal():
    choice = input("Show order as BFS or DFS? ").strip().upper()
    if choice == "DFS":
        return "DFS"
    return "BFS"


def get_distances(graph, start):
    # BFS distances from start
    # distance = number of edges away from start
    if not graph.contains(start):
        return {}

    distances = {start: 0}
    queue = [start]

    while queue:
        current = queue.pop(0)
        current_v = graph.get_vertex(current)
        if current_v is None:
            continue

        for nbr in current_v.get_connections():
            nbr_name = nbr.get_id()
            if nbr_name not in distances:
                distances[nbr_name] = distances[current] + 1
                queue.append(nbr_name)

    return distances


def dfs_limited(graph, start, max_depth):
    # Depth-limited DFS order (names only)
    # Returns a list that includes start first
    if not graph.contains(start):
        return []

    visited = set()
    order = []
    stack = [(start, 0)]

    while stack:
        node, depth = stack.pop()
        if node in visited:
            continue

        visited.add(node)
        order.append(node)

        if depth >= max_depth:
            continue

        v = graph.get_vertex(node)
        if v is None:
            continue

        neighbors = [nbr.get_id() for nbr in v.get_connections()]
        neighbors.sort(reverse=True)  # stable-ish DFS order
        for nbr_name in neighbors:
            if nbr_name not in visited:
                stack.append((nbr_name, depth + 1))

    return order


def print_names_list(title, names):
    print(title)
    if not names:
        print("(none)")
        return
    for n in names:
        print("-", n)


def create_profile_flow(pm):
    name = prompt_nonempty("Name: ")
    location = input("Location: ").strip()
    relationship_status = input("Relationship Status: ").strip()
    age = prompt_int("Age: ", 0, 130)
    occupation = input("Occupation: ").strip()
    astrological_sign = input("Astrological Sign: ").strip()
    status = input("Status (optional): ").strip()

    ok = pm.add_profile(name, location, relationship_status, age, occupation, astrological_sign, status)
    if not ok:
        print("That profile already exists.")
        return None
    return name


def modify_profile_flow(pm, current_user):
    p = pm.get_profile(current_user)
    if p is None:
        print("Current user not found.")
        return

    print("Modify Profile")
    print("1) Change status")
    choice = prompt_int("Choose: ", 1, 1)

    if choice == 1:
        new_status = input("Enter new status: ").strip()
        p.set_status(new_status)
        print("Status updated.")


def view_all_profiles_flow(pm, current_user):
    traversal = choose_traversal()

    # Start with traversal from current_user
    if traversal == "BFS":
        order = pm.graph.bfs(current_user)
    else:
        order = pm.graph.dfs(current_user)

    # If graph is disconnected, add any profiles not reached
    all_names = pm.display_profiles()
    seen = set(order)
    for n in all_names:
        if n not in seen:
            order.append(n)

    print_names_list("Profiles (names only):", order)


def view_friend_list_flow(pm, current_user):
    traversal = choose_traversal()

    distances = get_distances(pm.graph, current_user)
    if not distances:
        print("Current user not found in graph.")
        return

    # Friends are distance 1
    if traversal == "BFS":
        full_order = pm.graph.bfs(current_user)
        friends = [n for n in full_order if distances.get(n) == 1]
    else:
        full_order = dfs_limited(pm.graph, current_user, 1)
        friends = [n for n in full_order if n != current_user and distances.get(n) == 1]

    print_names_list("Your friends (names only):", friends)


def view_friends_friend_list_flow(pm):
    friend_name = prompt_nonempty("Enter your friend's name: ").strip()
    traversal = choose_traversal()

    if not pm.graph.contains(friend_name):
        print("That friend was not found.")
        return

    distances = get_distances(pm.graph, friend_name)

    # Friend's friends are distance 1 from friend_name
    if traversal == "BFS":
        full_order = pm.graph.bfs(friend_name)
        friends = [n for n in full_order if distances.get(n) == 1]
    else:
        full_order = dfs_limited(pm.graph, friend_name, 1)
        friends = [n for n in full_order if n != friend_name and distances.get(n) == 1]

    print_names_list(f"{friend_name}'s friends (names only):", friends)


def add_friend_flow(pm, current_user):
    friend = prompt_nonempty("Enter friend name to add: ").strip()
    if friend == current_user:
        print("You cannot friend yourself.")
        return

    ok = pm.connect_profiles(current_user, friend, weight=0)
    if ok:
        print("Friend added.")
    else:
        print("Could not add friend. Make sure the friend profile exists first.")


def delete_profile_flow(pm, mode, current_user):
    if mode == "ADMIN":
        target = prompt_nonempty("Enter profile name to delete: ").strip()
        ok = pm.remove_profile(target)
        if ok:
            print("Deleted.")
            if target == current_user:
                return None
        else:
            print("Profile not found.")
        return current_user

    # USER mode: allow deleting self only
    confirm = input(f"Delete your own profile ({current_user})? (y/n): ").strip().lower()
    if confirm == "y":
        ok = pm.remove_profile(current_user)
        if ok:
            print("Deleted your profile. Logging out.")
            return "__LOGOUT__"
        print("Could not delete profile.")
    return current_user


def switch_user_flow(pm):
    new_user = prompt_nonempty("Enter new current user name: ").strip()
    if pm.get_profile(new_user) is None:
        print("That user does not exist.")
        return None
    return new_user


def read_csv_flow(pm):
    path = prompt_nonempty("Enter CSV file path: ").strip()
    try:
        pm.read_profiles_from_csv(path)
        print("CSV loaded.")
    except Exception as e:
        print("Error reading CSV:", e)
        return None

    # Instruction says to switch to Alice to verify graph
    if pm.get_profile("Alice") is not None:
        print("Switched current user to Alice.")
        return "Alice"

    return None


def create_graph_flow(pm, current_user):
    depth = prompt_int("Depth (1 = friends, 2 = friends-of-friends): ", 1, 5)
    pm.create_user_graph(current_user, depth=depth, out_path=f"{current_user}Network")


def run():
    pm = ProfileManager()

    print("Welcome to Social Media Network")
    mode = input("Login as ADMIN or USER? ").strip().upper()
    if mode not in ("ADMIN", "USER"):
        mode = "USER"

    print("\nYou must create a profile to start.")
    current_user = create_profile_flow(pm)
    while current_user is None:
        current_user = create_profile_flow(pm)

    while True:
        print("\nMenu:")
        print("1. Create a profile")
        print("2. Modify profile")
        print("3. View all profiles")
        print("4. Add a friend")
        print("5. View your friend list")
        print("6. View your friend's friend list")

        if mode == "ADMIN":
            print("7. Delete a profile")
            print("8. Switch the current user")
            print("9. Read profiles from CSV")
        else:
            print("7. Delete your profile")
            # hide 8 and 9 in USER mode because they don't make sense for normal users

        print("10. Create graph of current user's network")
        print("11. Logout (end program)")

        choice = prompt_int("Choose an option (1-11): ", 1, 11)

        if mode == "USER" and choice in (8, 9):
            print("That option is only available in ADMIN mode.")
            continue

        if choice == 1:
            new_name = create_profile_flow(pm)
            if new_name:
                print("Created profile:", new_name)

        elif choice == 2:
            modify_profile_flow(pm, current_user)

        elif choice == 3:
            view_all_profiles_flow(pm, current_user)

        elif choice == 4:
            add_friend_flow(pm, current_user)

        elif choice == 5:
            view_friend_list_flow(pm, current_user)

        elif choice == 6:
            view_friends_friend_list_flow(pm)

        elif choice == 7:
            result = delete_profile_flow(pm, mode, current_user)
            if result == "__LOGOUT__":
                break
            current_user = result if result is not None else current_user

        elif choice == 8:
            new_user = switch_user_flow(pm)
            if new_user:
                current_user = new_user
                print("Switched current user to:", current_user)

        elif choice == 9:
            maybe_user = read_csv_flow(pm)
            if maybe_user:
                current_user = maybe_user

        elif choice == 10:
            create_graph_flow(pm, current_user)

        elif choice == 11:
            print("Goodbye!")
            break


if __name__ == "__main__":
    run()
