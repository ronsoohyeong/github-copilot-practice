from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from bbs_service import BbsService


app = FastAPI(title="Anonymous BBS API")
service = BbsService()


class ArticleCreateRequest(BaseModel):
    title: str
    body: str
    time: str


class PostResult(BaseModel):
    success: bool


@app.get("/articles", response_model=list[tuple[int, str, str]])
def get_list() -> list[tuple[int, str, str]]:
    return service.get_list()


@app.get("/articles/{article_id}", response_model=tuple[str, str, str])
def get_article(article_id: int) -> tuple[str, str, str]:
    article = service.get_article(article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@app.delete("/articles/{article_id}", response_model=PostResult)
def delete_article(article_id: int) -> PostResult:
    success = service.delete_article(article_id)
    return PostResult(success=success)


@app.post("/articles", response_model=PostResult)
def post_article(request: ArticleCreateRequest) -> PostResult:
    success = service.post_article(request.title, request.body, request.time)
    return PostResult(success=success)
