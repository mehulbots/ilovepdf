# update.py
# This module is part of https://github.com/nabilanavab/ilovepdf

import os, logging, dotenv
from subprocess import run, CalledProcessError
from typing import List, Optional
from logging import FileHandler, StreamHandler, INFO, basicConfig

file_name: str = "ILovePDF/update.py"

# Clear previous logs if any
if os.path.exists("log.txt"):
    with open("log.txt", 'w') as f:
        pass

def setup_logging(
    format: str = "[%(asctime)s] [%(name)s | %(levelname)s] - %(message)s [%(filename)s:%(lineno)d]",
    datefmt: str = "%m/%d/%Y, %H:%M:%S %p",
    handlers: Optional[List[logging.FileHandler]] = None,
    level: int = INFO
) -> None:
    if handlers is None:
        handlers = [FileHandler('log.txt'), StreamHandler()]

    basicConfig(format=format, datefmt=datefmt, handlers=handlers, level=level)
    dotenv.load_dotenv('config.env', override=True)

setup_logging()

def update_repository(upstream_repo: str, upstream_branch: str) -> None:
    if upstream_repo:
        if os.path.exists('.git'):
            run(["rm", "-rf", ".git"])

        try:
            run(
                f"git init -q && "
                f"git add . && "
                f"git config user.name 'UpdateBot' && "
                f"git config user.email 'bot@example.com' && "
                f"git commit -sm update -q && "
                f"git remote add origin {upstream_repo} && "
                f"git fetch origin -q && "
                f"git reset --hard origin/{upstream_branch} -q",
                shell=True,
                check=True
            )
            logging.info(f'Successfully updated with latest commit from {upstream_branch}')
        except CalledProcessError as e:
            logging.error(f'Something went wrong while updating: {e}')
            logging.error(f'Check {upstream_repo} for validity and try again.')

update_repository(
    upstream_repo=os.getenv('upstream_repo'),
    upstream_branch=os.getenv('upstream_branch')
)
