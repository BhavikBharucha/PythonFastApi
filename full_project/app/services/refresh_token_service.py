from app.models.refresh_token import RefreshToken


def create_token(
    db,
    user_id,
    token_id,
    expires_at
):
    token = RefreshToken(
        user_id=user_id,
        token_id=token_id,
        expires_at=expires_at
    )

    db.add(token)
    db.commit()

    return token

def get_by_token_id(
    db,
    token_id: str
):
    return (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token_id == token_id
        )
        .first()
    )

def revoke_token(
    db,
    token_id: str
):
    token = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token_id == token_id
        )
        .first()
    )

    if token:
        token.is_revoked = True
        db.commit()

    return token

def revoke_all_user_tokens(
    db,
    user_id: int
):
    tokens = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False
        )
        .all()
    )

    for token in tokens:
        token.is_revoked = True

    db.commit()

    return len(tokens)