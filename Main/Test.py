import os
from dotenv import load_dotenv

import requests
import json

load_dotenv(".gitignore/Secrets/bd.env")

LINK_BD = os.getenv("LINK_BD")

tagID = "32fc12c"

DADOS = {
    'ATIVO': False
}

req = requests.patch(f"{LINK_BD}/TAGS/{tagID}.json", data=json.dumps(DADOS))
