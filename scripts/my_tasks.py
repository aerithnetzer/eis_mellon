import os
from pathlib import Path
from fireworks import Firework, LaunchPad
from tasks import ImageTask, ImageToPDFTask
import certifi

if __name__ == "__main__":
    launchpad = LaunchPad(
        host="ocr-development.poelxty.mongodb.net",
        port=27017,
        uri_mode=False,
        name="fireworks",
        mongoclient_kwargs={
            "tls": False,
            "tlsCAFile": certifi.where(),  # or "/gpfs/projects/p32234/projects/aerith/mongodb-ca.pem"
            # Optional extras:
            # "tlsCertificateKeyFile": "/path/to/client.pem",
            # "tlsCertificateKeyFilePassword": "your_passphrase",
            # "authMechanism": "SCRAM-SHA-256"
        },
    )

    launchpad.reset("", require_password=False)
    raw_dir = Path("./data/raw")

    # Just add workflows to the database
    for dir in raw_dir.iterdir():
        if dir.is_dir():
            firework = Firework(
                [ImageTask(), ImageToPDFTask()],
                spec={"barcode_dir": str(dir.resolve())},
                name="OCR Pipeline",
            )
            launchpad.add_wf(firework)
            print(f"Added workflow for {dir.name}")

    print("\nWorkflows added. Now submit them with:")
    print("fab -H your_netid@quest.northwestern.edu qlaunch")
