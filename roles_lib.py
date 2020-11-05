#!/usr/bin/env python3
#-*- coding: utf8 -*-
"""
A small library to work with roles for a Discord servers.

- To adapt to each use case: here I have roles IE-1A to IE-9B, MA1-1 to MA4-8.
- Work in progress.
- See https://github.com/Naereen/Discord-bot-to-add-spoiler-to-any-code-snippet.git
- Author: Lilian Besson (Naereen)
- Date: 04/11/2020
- License: [MIT License](https://lbesson.mit-license.org/)
"""

def extract_role(name):
    """ Extract the role from given username."""
    name = sanitize_name(name)
    if ' - prof' in name:
        return "prof"
    for l in [1,2,3,4,5,6,7,8,9]:
        for g in ["A", "B"]:
            role = f'IE-{l}{g}'
            if name.endswith(role):
                return role
    for l in [1,2,3,4]:
        for g in [2*l-1, 2*l]:
            role = f'MA{l}-{g}'
            if name.endswith(role):
                return role
    return "TODO"

# TODO sanitize pseudo of a user
def sanitize_name(name):
    """ Clean-up the given username."""
    name = name.strip()

    # clean up group
    name = name.replace('- IE', ' -IE')
    name = name.replace('- MA', ' -MA')
    for l in [1,2,3,4,5,6,7,8,9]:
        for g in "AB":
            name = name.replace(f'IE{l}-{g}', f'IE-{l}{g}')
            name = name.replace(f'IE{l}{g}', f'IE-{l}{g}')
    for l in [1,2,3,4]:
        for g in [2*l-1, 2*l]:
            name = name.replace(f'MA-{l}{g}', f'MA{l}-{g}')
            name = name.replace(f'MA{l}{g}', f'MA{l}-{g}')

    # clean up name
    try:
        parts = name.split(' ')
        firstname = parts[0].title()
        group = parts[-1]
        familynames = parts[1:-1]
        familyname = " ".join(f.upper() for f in familynames)
        name = f"{firstname} {familyname} {group}"
        name = name.replace('-IE', '- IE')
        name = name.replace('-MA', '- MA')
    except:
        pass
    while "  " in name:
        name = name.replace('  ', ' ')
    return name

letters = list("abcdefghijklmnopqrstuvwxyz") + list("ààâçéèêäôöîïùûüŷÿñ")
LETTERS = [l.upper() for l in letters]
numbers = list("123456789")
all_letters = set(letters + LETTERS + numbers + [" ", "-", "'"])

# TODO
def check_name(name):
    """ check if the pseudo of a user is valid."""
    name = sanitize_name(name)
    for letter in name:
        if letter not in all_letters:
            # print(f"Bad letter = {letter}")
            return False
    role = extract_role(name)
    # remove group
    name = name.replace(f' - {role}', '')
    try:
        parts = name.split(' ')
        firstname = parts[0].title()
        if firstname[0] not in letters:
            return False
        for letter in firstname[1:]:
            if letter not in LETTERS:
                return False
        familynames = parts[1:]
        for familyname in familynames:
            if familyname[0] not in letters:
                return False
            for letter in familyname[1:]:
                if letter not in LETTERS:
                    return False
        return True
    except:
        return False

# List of roles
roles = ["prof", "TODO"] + [
        f"IE-{l}{g}" for l in [1,2,3,4,5,6,7,8,9] for g in ["A", "B"]
    ] + [
        f"MA{l}-{g}" for l in [1,2,3,4] for g in [2*l-1, 2*l]
    ]
all_roles = set(roles)

def check_role(role):
    """ check if role is correct."""
    return role in all_roles

def tests_names_roles(verbose=True):
    """ use good_names.txt and bad_names.txt to test previous functions."""
    # good names
    names = []
    with open("tests/good_names.txt") as f:
        for line in f.readlines():
            line = line.replace('\n', '')
            if line and not line.startswith("#"):
                names.append(line)
    for name in names:
        if verbose:
            print(f"'{name}' --> '{sanitize_name(name)}' of group '{extract_role(name)}'")
        # assert check_name(name)
        role = extract_role(name)
        assert check_role(role) and role != "TODO"

    # bad names
    names = []
    with open("tests/bad_names.txt") as f:
        for line in f.readlines():
            line = line.replace('\n', '')
            if line and not line.startswith("#"):
                names.append(line)
    for name in names:
        if verbose:
            print(f"'{name}' --> '{sanitize_name(name)}' of group '{extract_role(name)}'")
        # assert check_name(name)
        role = extract_role(name)
        assert (not check_name(name)) or (role == "TODO")


if __name__ == '__main__':
    tests_names_roles(verbose=True)
