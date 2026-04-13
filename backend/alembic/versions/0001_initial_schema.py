"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2026-04-12 00:00:00.000000

Creates all Phase 1 tables:
  tenants, users, refresh_tokens, clients, charts,
  plans, subscriptions, audit_logs
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # -------------------------------------------------------------------------
    # tenants
    # -------------------------------------------------------------------------
    op.create_table(
        "tenants",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("slug", sa.String(63), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("custom_domain", sa.String(253), nullable=True),
        sa.Column("logo_url", sa.Text(), nullable=True),
        sa.Column("tagline", sa.String(255), nullable=True),
        sa.Column("settings", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tenants_slug", "tenants", ["slug"], unique=True)
    op.create_index("ix_tenants_custom_domain", "tenants", ["custom_domain"], unique=True)

    # -------------------------------------------------------------------------
    # plans
    # -------------------------------------------------------------------------
    op.create_table(
        "plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("tier", sa.String(20), nullable=False),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("price_monthly_paise", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("price_yearly_paise", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_charts_per_month", sa.Integer(), nullable=False, server_default="50"),
        sa.Column("max_clients", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("max_users", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("features", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tier"),
    )

    # -------------------------------------------------------------------------
    # users
    # -------------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("password_hash", sa.String(128), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(30), nullable=True),
        sa.Column("role", sa.String(30), nullable=False, server_default="astrologer"),
        sa.Column("language", sa.String(10), nullable=False, server_default="en"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "email", name="uq_users_tenant_email"),
    )
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"])
    op.create_index("ix_users_email", "users", ["email"])

    # -------------------------------------------------------------------------
    # refresh_tokens
    # -------------------------------------------------------------------------
    op.create_table(
        "refresh_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("jti_hash", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("user_agent", sa.String(512), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("jti_hash"),
    )
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"])

    # -------------------------------------------------------------------------
    # subscriptions
    # -------------------------------------------------------------------------
    op.create_table(
        "subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("current_period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("charts_used_this_period", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("razorpay_subscription_id", sa.String(100), nullable=True),
        sa.Column("stripe_subscription_id", sa.String(100), nullable=True),
        sa.ForeignKeyConstraint(["plan_id"], ["plans.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_subscriptions_tenant_id", "subscriptions", ["tenant_id"])

    # -------------------------------------------------------------------------
    # clients
    # -------------------------------------------------------------------------
    op.create_table(
        "clients",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(320), nullable=True),
        sa.Column("phone", sa.String(30), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default="false"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_clients_tenant_id", "clients", ["tenant_id"])

    # -------------------------------------------------------------------------
    # charts
    # -------------------------------------------------------------------------
    op.create_table(
        "charts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("chart_type", sa.String(20), nullable=False, server_default="natal"),
        sa.Column("birth_name", sa.String(255), nullable=False),
        sa.Column("horary_number", sa.Integer(), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=False),
        sa.Column("birth_time", sa.Time(), nullable=False),
        sa.Column("birth_tz", sa.String(64), nullable=False),
        sa.Column("birth_lat", sa.Float(), nullable=False),
        sa.Column("birth_lon", sa.Float(), nullable=False),
        sa.Column("birth_location_name", sa.String(255), nullable=True),
        sa.Column("ayanamsa", sa.String(30), nullable=False, server_default="KP"),
        sa.Column("house_system", sa.String(20), nullable=False, server_default="Placidus"),
        sa.Column("chart_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("engine_version", sa.String(20), nullable=True),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("pdf_url", sa.String(1024), nullable=True),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_charts_tenant_id", "charts", ["tenant_id"])
    op.create_index("ix_charts_client_id", "charts", ["client_id"])
    op.create_index("ix_charts_created_by_id", "charts", ["created_by_id"])

    # -------------------------------------------------------------------------
    # audit_logs
    # -------------------------------------------------------------------------
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=True),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("request_id", sa.String(36), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_tenant_id", "audit_logs", ["tenant_id"])
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_request_id", "audit_logs", ["request_id"])

    # -------------------------------------------------------------------------
    # Seed default plans
    # -------------------------------------------------------------------------
    import uuid
    from datetime import datetime, timezone

    now = datetime.now(tz=timezone.utc).isoformat()

    op.execute(f"""
        INSERT INTO plans (id, created_at, updated_at, tier, display_name,
            price_monthly_paise, price_yearly_paise,
            max_charts_per_month, max_clients, max_users, features, is_active)
        VALUES
            ('{uuid.uuid4()}', '{now}', '{now}', 'free', 'Free',
             0, 0, 50, 50, 1, '{{"horary": false, "matching": false, "api_access": false}}', true),
            ('{uuid.uuid4()}', '{now}', '{now}', 'starter', 'Starter',
             49900, 499900, 200, 500, 3, '{{"horary": true, "matching": true, "api_access": false}}', true),
            ('{uuid.uuid4()}', '{now}', '{now}', 'pro', 'Professional',
             99900, 999900, 1000, -1, 10, '{{"horary": true, "matching": true, "api_access": true}}', true),
            ('{uuid.uuid4()}', '{now}', '{now}', 'enterprise', 'Enterprise',
             299900, 2999900, -1, -1, -1, '{{"horary": true, "matching": true, "api_access": true, "white_label": true}}', true)
    """)


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("charts")
    op.drop_table("clients")
    op.drop_table("subscriptions")
    op.drop_table("refresh_tokens")
    op.drop_table("users")
    op.drop_table("plans")
    op.drop_table("tenants")
