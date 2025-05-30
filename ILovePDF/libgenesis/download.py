import re
import time
import aiohttp
import aiofiles
import logging
import requests
from .utils import Util
from pathlib import Path
from tldextract import extract
from bs4 import BeautifulSoup as bsoup
from typing import Awaitable, Callable, Optional

logg = logging.getLogger(__name__)


class LibgenDownload:
    def __init__(self) -> None:
        self.dest_folder = Path.cwd()
        self.mirrors = ["library.lol", "libgen.lc", "libgen.gs", "b-ok.cc"]
        self.regex = re.compile(
            r"^(?:http|ftp)s?://"  # http:// or https://  domain...
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )

    async def download(
        self,
        url: str,
        dest_folder: Path = None,
        progress: Optional[Callable[..., Awaitable[None]]] = None,
        progress_args: list = [],
    ) -> Path:

        if (
            not re.match(self.regex, url)
            or (str(extract(url).domain) + "." + str(extract(url).suffix))
            not in self.mirrors
        ):
            raise Exception(f'Supported links are {" - ".join(self.mirrors)}')

        if not dest_folder:
            dest_folder = self.dest_folder
        if not Path(dest_folder).is_dir():
            Path(dest_folder).mkdir(parents=True, exist_ok=True)

        direct_links = await self.get_directlink(url)
        for link in direct_links:
            file = await self.__download(link, dest_folder, progress, progress_args)
            if not file:
                continue
            return file
        logg.error("Could not download the book from the given url.")
        return None

    @staticmethod
    async def __download(
        url: str,
        dest_folder: Path,
        progress: Optional[Callable[..., Awaitable[None]]],
        progress_args: list,
    ) -> Path:

        try:
            async with aiohttp.ClientSession() as dl_ses:
                async with dl_ses.get(url) as resp:
                    total_size = (
                        int(resp.headers.get("Content-Length"))
                        if resp.headers.get("Content-Length")
                        else "Unknown size"
                    )
                    file_name = await Util().get_filename(
                        resp.headers.get("Content-Disposition")
                    )
                    temp_file = Path(dest_folder).joinpath(file_name)

                    async with aiofiles.open(temp_file, mode="wb") as dl_file:
                        current = 0
                        logg.info(f"Starting download: {file_name}")
                        st_time = time.time()
                        async for chunk, _ in resp.content.iter_chunks():
                            await dl_file.write(chunk)
                            current += len(chunk)
                            cr_time = time.time()
                            if cr_time - st_time > 1:
                                if progress:
                                    await progress(current, total_size, *progress_args)
                                
                                st_time = cr_time
        except Exception as e:
            logg.exception(e)
            return None

        return temp_file

    async def get_directlink(self, url: str) -> list:

        tld = extract(url)
        r = requests.get(url, allow_redirects=True)
        logg.debug(f"Requesting download page resulted in code: {r.status_code}")
        if r.status_code != 200:
            await Util().raise_error(r.status_code, r.reason)

        soup = bsoup(r.content, "lxml")
        for s in soup.findAll("script"):
            s.decompose()

        domain = str(tld.domain) + "." + str(tld.suffix)
        direct_links = []
        if domain == "library.lol":
            div = soup.find("div", attrs={"id": "download"})
            direct_links.append(div.h2.a["href"])
            for li in div.ul.findAll("li"):
                direct_links.append(li.a["href"])
        elif domain == "libgen.lc" or domain == "libgen.gs":
            table = soup.find("table", attrs={"id": "main"})
            direct_links.append(table.tr.findAll("td")[1].a["href"])
        elif domain == "b-ok.cc":
            table = soup.find("table", attrs={"class": "resItemTable"})
            if table:
                zl_page = "http://b-ok.cc" + str(
                    table.tr.findAll("td")[1].table.tr.td.h3.a["href"]
                )
                zl_r = requests.get(zl_page, allow_redirects=True)
                logg.debug(f"Requesting b-ok page resulted in code: {zl_r.status_code}")
                if zl_r.status_code != 200:
                    await Util().raise_error(zl_r.status_code, r.reason)

                zl_soup = bsoup(zl_r.content, "lxml")
                for s in zl_soup.findAll("script"):
                    s.decompose()

                direct_links.append(
                    zl_soup.find(
                        "a",
                        attrs={"class": "btn btn-primary dlButton addDownloadedBook"},
                    )
                )
            else:
                await Util().raise_error(0, "Book not found on Z-library")
        else:
            logg.error(
                f'Unsuportted link. Only support download from {",".join(self.mirrors)}'
            )
            return direct_links

        return direct_links
