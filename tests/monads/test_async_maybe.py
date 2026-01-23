"""Tests for AsyncMaybe monad."""

import pytest

from better_py.monads import AsyncMaybe


class TestAsyncMaybe:
    """Tests for AsyncMaybe monad."""

    @pytest.mark.asyncio
    async def test_some_creation(self):
        """some should create Some variant."""
        result = AsyncMaybe.some(42)
        assert await result.is_some_async()

    @pytest.mark.asyncio
    async def test_nothing_creation(self):
        """nothing should create Nothing variant."""
        result = AsyncMaybe.nothing()
        assert await result.is_nothing_async()

    @pytest.mark.asyncio
    async def test_from_value(self):
        """from_value should create Some from value."""
        result = AsyncMaybe.from_value(42)
        assert await result.is_some_async()
        assert await result.unwrap() == 42

    @pytest.mark.asyncio
    async def test_from_value_none(self):
        """from_value should create Nothing from None."""
        result = AsyncMaybe.from_value(None)
        assert await result.is_nothing_async()

    @pytest.mark.asyncio
    async def test_map(self):
        """map should transform the value."""
        result = AsyncMaybe.some(5).map(lambda x: x * 2)
        assert await result.unwrap() == 10

    @pytest.mark.asyncio
    async def test_map_nothing(self):
        """map should preserve Nothing."""
        result = AsyncMaybe.nothing().map(lambda x: x * 2)
        assert await result.is_nothing_async()

    @pytest.mark.asyncio
    async def test_bind(self):
        """bind should chain async operations."""
        async def double(x):
            return AsyncMaybe.some(x * 2)

        result = await AsyncMaybe.some(5).bind(double)
        assert await result.unwrap() == 10

    @pytest.mark.asyncio
    async def test_bind_nothing(self):
        """bind should short-circuit on Nothing."""
        async def double(x):
            return AsyncMaybe.some(x * 2)

        result = await AsyncMaybe.nothing().bind(double)
        assert await result.is_nothing_async()

    @pytest.mark.asyncio
    async def test_map_async(self):
        """map_async should apply async function."""
        async def fetch(x):
            return x * 2

        result = await AsyncMaybe.some(5).map_async(fetch)
        assert await result.unwrap() == 10

    @pytest.mark.asyncio
    async def test_to_maybe(self):
        """to_maybe should convert to Maybe."""
        result = AsyncMaybe.some(42).to_maybe()
        assert result.is_some()
        assert result.unwrap() == 42
