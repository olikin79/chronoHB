import os
import shutil
import sys
import winshell

# Chemin vers l'exécutable
target = os.path.join(sys.prefix, "Decoupe Copies.exe")

# Raccourci sur le bureau
desktop = winshell.desktop()
shortcut_path = os.path.join(desktop, "Découpe copies UM.lnk")
with winshell.shortcut(shortcut_path) as shortcut:
    shortcut.path = target
    shortcut.description = "Découpe copies UM"
    shortcut.icon_location = (target, 0)

# Raccourci dans "Tous les programmes"
start_menu = winshell.start_menu()
programs_path = os.path.join(start_menu, "Découpe copies UM.lnk")
with winshell.shortcut(programs_path) as shortcut:
    shortcut.path = target
    shortcut.description = "Découpe copies UM"
    shortcut.icon_location = (target, 0)