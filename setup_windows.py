import os
from cx_Freeze import setup, Executable

os.environ["PYTHONIOENCODING"] = "utf-8"

# Dependencies are automatically detected, but they might need fine-tuning.
build_exe_options = {
    "includes": ["tkinter", "time", "datetime", "webbrowser", "subprocess", "sys", "os", "re", "copy", "socket",\
        "idlelib.tooltip", "pprint", "cgi", "requests", "importlib", "hashlib", "CameraMotionDetection", "functools", \
        "cryptography.fernet", "ftplib", "locale", "glob", "shutil", "random", "csv", "pathlib", "server", "threading", \
        "xlsxwriter", "math", "openpyxl", "urllib.request", "zipfile", "redmail", "cryptography.fernet"],
    "include_files": ["favicon.ico","create_shortcuts.py", \
        "CameraMotionDetection.py", "FonctionsAssistance.py", "FonctionsDiffusionInternet.py", "FonctionsMetiers.py", "jquery-3.6.0.js", \
        "LICENSE", "mystyle.css", "mystyle_mode-sombre.css", "mystyleWeb.css", "openh264-1.8.0-win64.dll", "resultatsDiffusion.py", \
        "server.py", "Videos.html", \
        "cgi", "documentation", "gs", "gsview", "hooks", "IM", "maj", "media", "modeles", "secret", "texlive", "www"]
}

# build_mac_options = { "iconfile": "Icon.icns",
#                      "bundle_name": "Découpe Copies UM"}

build_msi_options = {"upgrade_code": "{66212526-7761-6E69-6F6E-6C129E797817}",
                     "target_name" :"ChronoHB",
                     "data": {
                            "Shortcut": [
        ("DesktopShortcut", "DesktopFolder", "ChronoHB", "TARGETDIR", "[TARGETDIR]ChronoHB.exe", None, "favicon.ico", None, None, None, None, 'TARGETDIR'),
        ("StartMenuShortcut", "ProgramMenuFolder", "ChronoHB", "TARGETDIR", "[TARGETDIR]ChronoHB.exe", None, "favicon.ico", None, None, None, None, 'TARGETDIR')
                                    ],
                        # Associer l'extension .chb au type ChronoHBFile
                        "Extension": [
                            (".chb", "TARGETDIR", "ChronoHBFile", 0, 1)
                        ],
                        # Associer le type ChronoHBFile à l'exécutable chronoHB.exe
                        "FileType": [
                            ("ChronoHBFile", "ChronoHB File", "[TARGETDIR]chronoHB.exe", None, None)
                        ]
                        # "Extension": [
                        #         # Association pour les fichiers .chb
                        #         ("Extension", "FileType", ".chb", "ChronoHBFile")
                        #         ],
                        # "FileType": [
                        #         ("FileType", None, "ChronoHB File", "[TARGETDIR]chronoHB.exe", None)
                        #         ]
                            }
                    }

setup(
    name="ChronoHB",
    version="2.1.0",
    description="Chronométrage de courses",
    options={"build_exe": build_exe_options,
             "bdist_msi": build_msi_options},
    executables=[Executable("chronoHB.pyw", base="gui", target_name='ChronoHB')],
)