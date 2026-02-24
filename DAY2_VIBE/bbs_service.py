from __future__ import annotations

from dataclasses import dataclass


MAX_TITLE_LENGTH = 20
MAX_BODY_LENGTH = 200
MAX_ARTICLES = 10


@dataclass(frozen=True)
class Article:
    id: int
    title: str
    time: str
    body: str


class BbsService:
    def __init__(self) -> None:
        self._articles: list[Article] = []
        self._next_id = 1

    def get_list(self) -> list[tuple[int, str, str]]:
        return [
            (article.id, article.title, article.time)
            for article in reversed(self._articles)
        ]

    def get_article(self, article_id: int) -> tuple[str, str, str] | None:
        for article in self._articles:
            if article.id == article_id:
                return article.title, article.body, article.time
        return None

    def post_article(self, title: str, body: str, time: str) -> bool:
        normalized_title = title.strip()
        normalized_body = body.strip()
        normalized_time = time.strip()

        if not self._is_valid(normalized_title, normalized_body, normalized_time):
            return False

        self._articles.append(
            Article(
                id=self._next_id,
                title=normalized_title,
                time=normalized_time,
                body=normalized_body,
            )
        )
        self._next_id += 1

        if len(self._articles) > MAX_ARTICLES:
            overflow = len(self._articles) - MAX_ARTICLES
            self._articles = self._articles[overflow:]

        return True

    def delete_article(self, article_id: int) -> bool:
        for index, article in enumerate(self._articles):
            if article.id == article_id:
                del self._articles[index]
                return True
        return False

    @staticmethod
    def _is_valid(title: str, body: str, time: str) -> bool:
        if not title or not body or not time:
            return False
        if len(title) > MAX_TITLE_LENGTH:
            return False
        if len(body) > MAX_BODY_LENGTH:
            return False
        return True
