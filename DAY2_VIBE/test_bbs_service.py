from bbs_service import BbsService, MAX_ARTICLES


def test_post_and_get_article_success() -> None:
    service = BbsService()

    ok = service.post_article("제목", "본문", "2026-02-24 15:10:00")

    assert ok is True
    listed = service.get_list()
    assert len(listed) == 1
    article_id, title, created_time = listed[0]
    assert title == "제목"
    assert created_time == "2026-02-24 15:10:00"
    assert service.get_article(article_id) == ("제목", "본문", "2026-02-24 15:10:00")


def test_post_fail_when_length_exceeded() -> None:
    service = BbsService()

    long_title = "가" * 21
    long_body = "나" * 201

    assert service.post_article(long_title, "본문", "2026-02-24 15:10:00") is False
    assert service.post_article("제목", long_body, "2026-02-24 15:10:00") is False
    assert service.post_article("제목", "본문", "") is False
    assert service.get_list() == []


def test_only_latest_10_articles_kept() -> None:
    service = BbsService()

    for i in range(MAX_ARTICLES + 2):
        assert service.post_article(
            f"제목{i}", f"본문{i}", f"2026-02-24 15:10:{i:02d}"
        ) is True

    listed = service.get_list()
    assert len(listed) == MAX_ARTICLES

    ids = [article_id for article_id, _, _ in listed]
    assert min(ids) == 3
    assert max(ids) == 12


def test_list_is_latest_first() -> None:
    service = BbsService()

    assert service.post_article("첫 글", "첫 본문", "2026-02-24 15:10:01") is True
    assert service.post_article("둘째 글", "둘째 본문", "2026-02-24 15:10:02") is True

    listed = service.get_list()
    assert listed[0][1] == "둘째 글"
    assert listed[1][1] == "첫 글"


def test_delete_article_success_and_fail() -> None:
    service = BbsService()

    assert service.post_article("삭제 대상", "본문", "2026-02-24 15:10:00") is True
    article_id = service.get_list()[0][0]

    assert service.delete_article(article_id) is True
    assert service.get_article(article_id) is None
    assert service.delete_article(article_id) is False
