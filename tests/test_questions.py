from application.commands import extract_values
from application.question_sets import questions


def test_prev_next_slugs_are_valid():

    for stage in questions.keys():
        qs = questions[stage]
        slugs = set([next(iter(q.keys())) for q in qs])
        next_prev_slugs = set([])
        for q in qs:
            extract_values(q, next_prev_slugs)

        assert next_prev_slugs.issubset(slugs)


def test_question_page_returns_404_for_invalid_stage(client, consideration):
    response = client.get("/planning-consideration/test-consideration-1/backlog/")
    assert response.status_code == 200

    response = client.get("/planning-consideration/test-consideration-1/invalid-stage/")
    assert response.status_code == 404
