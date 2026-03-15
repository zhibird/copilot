from uuid import uuid4


def test_chat_echo_requires_configured_user_team(client) -> None:
    suffix = uuid4().hex[:8]
    team_id = f"team_{suffix}"
    user_id = f"u_{suffix}"

    team_response = client.post(
        "/api/v1/teams",
        json={
            "team_id": team_id,
            "name": "Ops Team",
            "description": "for chat test",
        },
    )
    assert team_response.status_code == 201

    user_response = client.post(
        "/api/v1/users",
        json={
            "user_id": user_id,
            "team_id": team_id,
            "display_name": "Alice",
            "role": "owner",
        },
    )
    assert user_response.status_code == 201

    chat_response = client.post(
        "/api/v1/chat/echo",
        json={
            "user_id": user_id,
            "team_id": team_id,
            "message": "hello",
        },
    )

    assert chat_response.status_code == 200
    body = chat_response.json()
    assert body["answer"] == "[Echo] hello"


def test_chat_echo_rejects_unknown_user(client) -> None:
    unknown_user_id = f"u_unknown_{uuid4().hex[:8]}"

    response = client.post(
        "/api/v1/chat/echo",
        json={
            "user_id": unknown_user_id,
            "team_id": "team_ops",
            "message": "hello",
        },
    )

    assert response.status_code == 404


def test_chat_ask_returns_answer_and_hits(client) -> None:
    suffix = uuid4().hex[:8]
    team_id = f"team_ask_{suffix}"
    user_id = f"u_ask_{suffix}"

    create_team = client.post(
        "/api/v1/teams",
        json={
            "team_id": team_id,
            "name": "Ask Team",
            "description": "for ask test",
        },
    )
    assert create_team.status_code == 201

    create_user = client.post(
        "/api/v1/users",
        json={
            "user_id": user_id,
            "team_id": team_id,
            "display_name": "Operator",
            "role": "member",
        },
    )
    assert create_user.status_code == 201

    import_response = client.post(
        "/api/v1/documents/import",
        json={
            "team_id": team_id,
            "source_name": "ops.md",
            "content_type": "md",
            "content": (
                "# Ops Guide\n\n"
                "Always check alerts first. "
                "Escalate incidents quickly. "
                "Keep channels updated every 10 minutes."
            ),
        },
    )
    assert import_response.status_code == 201
    document_id = import_response.json()["document_id"]

    chunk_response = client.post(
        f"/api/v1/documents/{document_id}/chunk",
        json={
            "team_id": team_id,
            "max_chars": 100,
            "overlap": 10,
        },
    )
    assert chunk_response.status_code == 200

    index_response = client.post(
        "/api/v1/retrieval/index",
        json={
            "team_id": team_id,
            "document_id": document_id,
        },
    )
    assert index_response.status_code == 200

    ask_response = client.post(
        "/api/v1/chat/ask",
        json={
            "user_id": user_id,
            "team_id": team_id,
            "question": "alerts first?",
            "top_k": 3,
            "document_id": document_id,
        },
    )

    assert ask_response.status_code == 200
    body = ask_response.json()
    assert body["user_id"] == user_id
    assert body["team_id"] == team_id
    assert body["answer"]
    assert len(body["hits"]) >= 1


def test_chat_ask_requires_indexed_chunks(client) -> None:
    suffix = uuid4().hex[:8]
    team_id = f"team_ask_no_index_{suffix}"
    user_id = f"u_ask_no_index_{suffix}"

    create_team = client.post(
        "/api/v1/teams",
        json={
            "team_id": team_id,
            "name": "NoIndex Team",
            "description": "ask without index",
        },
    )
    assert create_team.status_code == 201

    create_user = client.post(
        "/api/v1/users",
        json={
            "user_id": user_id,
            "team_id": team_id,
            "display_name": "Operator",
            "role": "member",
        },
    )
    assert create_user.status_code == 201

    ask_response = client.post(
        "/api/v1/chat/ask",
        json={
            "user_id": user_id,
            "team_id": team_id,
            "question": "alerts first?",
            "top_k": 3,
        },
    )

    assert ask_response.status_code == 404