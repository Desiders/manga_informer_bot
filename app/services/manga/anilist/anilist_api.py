from typing import Optional

from aiohttp import ClientResponse, ClientSession, ClientTimeout
from app.html_utils import escape_html
from app.services.manga.anilist.exceptions import MangaNotFound, ServerError
from app.services.manga.anilist.schemas import MangaPreview, MangaRelation
from structlog import get_logger
from structlog.stdlib import BoundLogger

logger: BoundLogger = get_logger()


class AnilistApi:
    source_url = "https://graphql.anilist.co"

    def __init__(self) -> None:
        self._session: Optional[ClientSession] = None

    def get_new_session(self) -> ClientSession:
        return ClientSession(
            timeout=ClientTimeout(total=60),
        )

    @property
    def session(self) -> ClientSession:
        if self._session is None or self._session.closed:
            self._session = self.get_new_session()
        return self._session

    async def close(self) -> None:
        session = self._session
        if session is not None and not session.closed:
            await session.close()

    async def send_request_to_source(
        self,
        query: str,
        variables: dict,
    ) -> ClientResponse:
        response = await self.session.post(
            url=self.source_url,
            json={
                "query": query,
                "variables": variables,
            },
        )
        if response.status >= 500:
            raise ServerError(await response.text)
        return response

    async def manga_preview_by_name(self, name: str) -> MangaPreview:
        query = """
        query ($search: String) {
            Media(search: $search, type: MANGA) {
                id
                title {
                    english
                    romaji
                    native
                }
                siteUrl
                description
                genres
            }
        }
        """
        variables = {
            "search": name,
        }

        response = await self.send_request_to_source(
            query=query, variables=variables,
        )
        if response.status == 404:
            raise MangaNotFound(
                "Manga with this name not found!"
            )

        result = await response.json()

        data = result["data"]["Media"]
        title = data["title"]

        return MangaPreview(
            id=data["id"],
            english_name=title["english"],
            romaji_name=title["romaji"],
            native_name=title["native"],
            url=data["siteUrl"],
            description=escape_html(data["description"]),
            genres=data["genres"],
        )

    async def manga_preview_page_by_name(
        self,
        page: int,
        name: str,
    ) -> MangaPreview:
        query = """
        query ($page: Int, $search: String) {
            Page(page: $page, perPage: 1) {
                media(search: $search, type: MANGA) {
                    id
                    title {
                        english
                        romaji
                        native
                    }
                    siteUrl
                    description
                    genres
                }
            }
        }
        """
        variables = {
            "page": page,
            "search": name,
        }

        response = await self.send_request_to_source(
            query=query, variables=variables,
        )

        result = await response.json()

        data = result["data"]["Page"]["media"]
        if not data:
            raise MangaNotFound("Manga not found!")
        else:
            data = data[0]
        title = data["title"]

        return MangaPreview(
            id=data["id"],
            english_name=title["english"],
            romaji_name=title["romaji"],
            native_name=title["native"],
            url=data["siteUrl"],
            description=(
                escape_html(data["description"])
                if data["description"]
                else None
            ),
            genres=data["genres"],
        )

    async def manga_relations_by_id(self, id: int) -> list[MangaRelation]:
        query = """
        query ($id: Int) {
            Media(id: $id) {
                relations {
                    edges {
                        node {
                            id
                            title {
                                english
                                romaji
                                native
                            }
                        }
                        relationType
                    }
                }
            }
        }
        """
        variables = {
            "id": id,
        }

        response = await self.send_request_to_source(
            query=query, variables=variables,
        )
        if response.status == 404:
            raise MangaNotFound(
                "Manga with this id not found!"
            )

        result = await response.json()

        data = result["data"]["Media"]
        relations = data["relations"]
        edges = relations["edges"]

        manga_relations: list[MangaRelation] = []
        for edge in edges:
            node = edge["node"]
            title = node["title"]

            manga_relations.append(
                MangaRelation(
                    id=node["id"],
                    english_name=title["english"],
                    romaji_name=title["romaji"],
                    native_name=title["native"],
                    relation_type=edge["relationType"].replace("_", " "),
                ),
            )
        return manga_relations