"""
Integration tests for authentication endpoints.
"""
from __future__ import annotations

import pytest

REGISTER_PAYLOAD = {
    "email": "astro@test.com",
    "password": "test1234",
    "full_name": "Test Astrologer",
    "tenant_slug": "testastro",
    "tenant_display_name": "Test Astrology",
}


class TestRegister:
    async def test_register_success(self, client):
        resp = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_register_duplicate_slug_fails(self, client):
        await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        resp2 = await client.post("/api/v1/auth/register", json={
            **REGISTER_PAYLOAD,
            "email": "other@test.com",
        })
        assert resp2.status_code == 409

    async def test_register_invalid_slug(self, client):
        resp = await client.post("/api/v1/auth/register", json={
            **REGISTER_PAYLOAD,
            "tenant_slug": "UPPERCASE",
        })
        assert resp.status_code == 422

    async def test_register_reserved_slug(self, client):
        resp = await client.post("/api/v1/auth/register", json={
            **REGISTER_PAYLOAD,
            "tenant_slug": "www",
        })
        assert resp.status_code == 422

    async def test_register_weak_password(self, client):
        resp = await client.post("/api/v1/auth/register", json={
            **REGISTER_PAYLOAD,
            "password": "no-digits-here",
        })
        assert resp.status_code == 422


class TestLogin:
    @pytest.fixture(autouse=True)
    async def setup(self, client):
        await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)

    async def test_login_success(self, client):
        resp = await client.post("/api/v1/auth/login", json={
            "email": REGISTER_PAYLOAD["email"],
            "password": REGISTER_PAYLOAD["password"],
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    async def test_login_wrong_password(self, client):
        resp = await client.post("/api/v1/auth/login", json={
            "email": REGISTER_PAYLOAD["email"],
            "password": "wrongpassword1",
        })
        assert resp.status_code == 401

    async def test_login_unknown_email(self, client):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "nobody@test.com",
            "password": "test1234",
        })
        assert resp.status_code == 401


class TestTokenRefresh:
    async def test_refresh_returns_new_token(self, client):
        reg = await client.post("/api/v1/auth/register", json={
            **REGISTER_PAYLOAD,
            "email": "refresh@test.com",
            "tenant_slug": "refreshtest",
        })
        old_rt = reg.json()["refresh_token"]

        resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": old_rt})
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        # New refresh token should differ from old one
        assert data["refresh_token"] != old_rt

    async def test_refresh_with_access_token_fails(self, client):
        reg = await client.post("/api/v1/auth/register", json={
            **REGISTER_PAYLOAD,
            "email": "badrefresh@test.com",
            "tenant_slug": "badrefreshtest",
        })
        access_token = reg.json()["access_token"]

        resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": access_token})
        assert resp.status_code == 401


class TestMe:
    async def test_me_returns_user(self, client):
        reg = await client.post("/api/v1/auth/register", json={
            **REGISTER_PAYLOAD,
            "email": "me@test.com",
            "tenant_slug": "metest",
        })
        token = reg.json()["access_token"]

        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "me@test.com"
        assert data["role"] == "tenant_admin"

    async def test_me_without_token_fails(self, client):
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 401
