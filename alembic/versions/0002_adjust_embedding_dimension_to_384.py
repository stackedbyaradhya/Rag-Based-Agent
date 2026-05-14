"""adjust embedding vector dimension to 384

Revision ID: 0002_embed_dim_384
Revises: 0001_initial_schema
Create Date: 2026-04-29
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "0002_embed_dim_384"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DELETE FROM document_chunks;")
    op.execute(
        "ALTER TABLE document_chunks "
        "ALTER COLUMN embedding TYPE vector(384) "
        "USING NULL;"
    )


def downgrade() -> None:
    op.execute("DELETE FROM document_chunks;")
    op.execute(
        "ALTER TABLE document_chunks "
        "ALTER COLUMN embedding TYPE vector(768) "
        "USING NULL;"
    )
