"""Tests for AsyncResult monad."""

import pytest

from better_py.monads import AsyncResult


class TestAsyncResult:
    """Tests for AsyncResult monad."""

    @pytest.mark.asyncio
    async def test_ok_creation(self):
        """ok should create Ok variant."""
        result = AsyncResult.ok(42)
        assert await result.is_ok_async()

    @pytest.mark.asyncio
    async def test_error_creation(self):
        """error should create Error variant."""
        result = AsyncResult.error("failed")
        assert await result.is_error_async()

    @pytest.mark.asyncio
    async def test_from_value(self):
        """from_value should create Ok from value."""
        result = AsyncResult.from_value(42)
        assert await result.is_ok_async()
        assert await result.unwrap() == 42

    @pytest.mark.asyncio
    async def test_from_value_none(self):
        """from_value should create Error from None."""
        result = AsyncResult.from_value(None, "error")
        assert await result.is_error_async()
        assert await result.unwrap_error() == "error"

    @pytest.mark.asyncio
    async def test_map(self):
        """map should transform the success value."""
        result = AsyncResult.ok(5).map(lambda x: x * 2)
        assert await result.unwrap() == 10

    @pytest.mark.asyncio
    async def test_map_error(self):
        """map should preserve Error."""
        result = AsyncResult.error("fail").map(lambda x: x * 2)
        assert await result.is_error_async()

    @pytest.mark.asyncio
    async def test_map_async(self):
        """map_async should apply async function."""
        async def fetch(x):
            return x * 2

        result = await AsyncResult.ok(5).map_async(fetch)
        assert await result.unwrap() == 10

    @pytest.mark.asyncio
    async def test_map_async_error(self):
        """map_async should preserve Error."""
        async def fetch(x):
            return x * 2

        result = await AsyncResult.error("fail").map_async(fetch)
        assert await result.is_error_async()

    @pytest.mark.asyncio
    async def test_map_error_method(self):
        """map_error should transform the error value."""
        result = AsyncResult.error("fail").map_error(lambda e: f"Error: {e}")
        assert await result.is_error_async()
        assert await result.unwrap_error() == "Error: fail"

    @pytest.mark.asyncio
    async def test_bind(self):
        """bind should chain async operations."""
        async def double(x):
            return AsyncResult.ok(x * 2)

        result = await AsyncResult.ok(5).bind(double)
        assert await result.unwrap() == 10

    @pytest.mark.asyncio
    async def test_bind_error(self):
        """bind should short-circuit on Error."""
        async def double(x):
            return AsyncResult.ok(x * 2)

        result = await AsyncResult.error("fail").bind(double)
        assert await result.is_error_async()

    @pytest.mark.asyncio
    async def test_recover(self):
        """recover should transform error into success."""
        result = await AsyncResult.error("fail").recover(lambda _: 0)
        assert await result.is_ok_async()
        assert await result.unwrap() == 0

    @pytest.mark.asyncio
    async def test_recover_ok(self):
        """recover should preserve Ok."""
        result = await AsyncResult.ok(42).recover(lambda _: 0)
        assert await result.is_ok_async()
        assert await result.unwrap() == 42

    @pytest.mark.asyncio
    async def test_unwrap(self):
        """unwrap should return the value."""
        result = AsyncResult.ok(42)
        assert await result.unwrap() == 42

    @pytest.mark.asyncio
    async def test_unwrap_error_raises(self):
        """unwrap should raise on Error."""
        result = AsyncResult.error("fail")
        with pytest.raises(ValueError):
            await result.unwrap()

    @pytest.mark.asyncio
    async def test_unwrap_or_else(self):
        """unwrap_or_else should return value or default."""
        result = AsyncResult.error("fail")
        assert await result.unwrap_or_else(lambda: 0) == 0

    @pytest.mark.asyncio
    async def test_unwrap_or_else_ok(self):
        """unwrap_or_else should return value for Ok."""
        result = AsyncResult.ok(42)
        assert await result.unwrap_or_else(lambda: 0) == 42

    @pytest.mark.asyncio
    async def test_unwrap_error(self):
        """unwrap_error should return the error value."""
        result = AsyncResult.error("fail")
        assert await result.unwrap_error() == "fail"

    @pytest.mark.asyncio
    async def test_unwrap_error_ok_raises(self):
        """unwrap_error should raise on Ok."""
        result = AsyncResult.ok(42)
        with pytest.raises(ValueError):
            await result.unwrap_error()

    @pytest.mark.asyncio
    async def test_to_result(self):
        """to_result should convert to Result."""
        result = AsyncResult.ok(42).to_result()
        assert result.is_ok()
        assert result.unwrap() == 42

    @pytest.mark.asyncio
    async def test_equality(self):
        """AsyncResult instances should be equal if underlying Results are equal."""
        result1 = AsyncResult.ok(42)
        result2 = AsyncResult.ok(42)
        assert result1 == result2

    @pytest.mark.asyncio
    async def test_inequality(self):
        """AsyncResult instances should not be equal to different values."""
        result1 = AsyncResult.ok(42)
        result2 = AsyncResult.ok(43)
        assert result1 != result2

    @pytest.mark.asyncio
    async def test_inequality_different_types(self):
        """AsyncResult should not be equal to non-AsyncResult."""
        result = AsyncResult.ok(42)
        assert result != 42

    @pytest.mark.asyncio
    async def test_repr(self):
        """repr should show underlying Result."""
        result = AsyncResult.ok(42)
        assert repr(result) == "AsyncResult(Ok(42))"
