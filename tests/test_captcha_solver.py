# tests/test_captcha_solver.py
import pytest
import requests
from unittest.mock import Mock, patch
from src.anti_scraping.captcha_solver import CaptchaSolver, CaptchaSolverError


class TestCaptchaSolver:
    """Test cases for CaptchaSolver timeout handling"""

    @pytest.fixture
    def captcha_solver(self):
        """Create a CaptchaSolver instance for testing"""
        with patch("src.anti_scraping.captcha_solver.config") as mock_config:
            mock_config.CAPTCHA_SOLVER_API_KEY = "test-api-key"
            mock_config.CAPTCHA_SOLVER_PROVIDER = "2captcha"
            mock_config.CAPTCHA_INITIAL_REQUEST_TIMEOUT = 30
            mock_config.CAPTCHA_POLLING_REQUEST_TIMEOUT = 10
            return CaptchaSolver()

    def test_init_requires_api_key(self):
        """Test that CaptchaSolver requires an API key"""
        with patch("src.anti_scraping.captcha_solver.config") as mock_config:
            mock_config.CAPTCHA_SOLVER_API_KEY = ""
            with pytest.raises(ValueError, match="CAPTCHA API key is required"):
                CaptchaSolver()

    @patch("src.anti_scraping.captcha_solver.requests.post")
    def test_2captcha_submission_timeout(self, mock_post, captcha_solver):
        """Test that 2captcha submission handles timeout properly"""
        # Mock timeout exception
        mock_post.side_effect = requests.Timeout()

        with pytest.raises(
            CaptchaSolverError, match="CAPTCHA submission request timed out"
        ):
            captcha_solver._solve_with_2captcha("test-site-key", "https://example.com")

        # Verify timeout parameter was used
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]["timeout"] == 30

    @patch("src.anti_scraping.captcha_solver.requests.post")
    def test_2captcha_submission_network_error(self, mock_post, captcha_solver):
        """Test that 2captcha submission handles network errors properly"""
        # Mock network error
        mock_post.side_effect = requests.RequestException("Network error")

        with pytest.raises(
            CaptchaSolverError, match="CAPTCHA submission request failed: Network error"
        ):
            captcha_solver._solve_with_2captcha("test-site-key", "https://example.com")

    @patch("src.anti_scraping.captcha_solver.requests.get")
    @patch("src.anti_scraping.captcha_solver.requests.post")
    def test_2captcha_polling_timeout(self, mock_post, mock_get, captcha_solver):
        """Test that 2captcha polling handles timeout properly"""
        # Mock successful submission
        mock_post.return_value.json.return_value = {
            "status": 1,
            "request": "captcha-id-123",
        }

        # Mock timeout on polling
        mock_get.side_effect = requests.Timeout()

        with pytest.raises(
            CaptchaSolverError, match="CAPTCHA polling request timed out"
        ):
            captcha_solver._solve_with_2captcha("test-site-key", "https://example.com")

        # Verify polling timeout parameter was used
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[1]["timeout"] == 10

    @patch("src.anti_scraping.captcha_solver.requests.post")
    def test_anticaptcha_submission_timeout(self, mock_post, captcha_solver):
        """Test that Anticaptcha submission handles timeout properly"""
        # Mock timeout exception on first call
        mock_post.side_effect = requests.Timeout()

        with pytest.raises(
            CaptchaSolverError, match="CAPTCHA submission request timed out"
        ):
            captcha_solver._solve_with_anticaptcha(
                "test-site-key", "https://example.com"
            )

        # Verify timeout parameter was used
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]["timeout"] == 30

    @patch("src.anti_scraping.captcha_solver.requests.post")
    def test_anticaptcha_polling_timeout(self, mock_post, captcha_solver):
        """Test that Anticaptcha polling handles timeout properly"""
        # Mock successful submission on first call, timeout on second call
        mock_post.side_effect = [
            Mock(
                json=lambda: {"errorId": 0, "taskId": "task-123"}
            ),  # Successful submission
            requests.Timeout(),  # Timeout on polling
        ]

        with pytest.raises(
            CaptchaSolverError, match="CAPTCHA polling request timed out"
        ):
            captcha_solver._solve_with_anticaptcha(
                "test-site-key", "https://example.com"
            )

        # Verify both calls were made with correct timeouts
        assert mock_post.call_count == 2

        # Check submission call (first call)
        submission_call = mock_post.call_args_list[0]
        assert submission_call[1]["timeout"] == 30

        # Check polling call (second call)
        polling_call = mock_post.call_args_list[1]
        assert polling_call[1]["timeout"] == 10

    @patch("src.anti_scraping.captcha_solver.requests.post")
    def test_solve_recaptcha_propagates_timeout_error(self, mock_post, captcha_solver):
        """Test that solve_recaptcha propagates CaptchaSolverError"""
        mock_post.side_effect = requests.Timeout()

        # The solve_recaptcha method should propagate CaptchaSolverError, not catch it
        with pytest.raises(CaptchaSolverError):
            captcha_solver.solve_recaptcha("test-site-key", "https://example.com")

    def test_solve_recaptcha_unsupported_provider(self, captcha_solver):
        """Test that solve_recaptcha raises ValueError for unsupported provider"""
        captcha_solver.provider = "unsupported"

        with pytest.raises(
            ValueError, match="Unsupported CAPTCHA provider: unsupported"
        ):
            captcha_solver.solve_recaptcha("test-site-key", "https://example.com")

    @patch("src.anti_scraping.captcha_solver.requests.get")
    @patch("src.anti_scraping.captcha_solver.requests.post")
    def test_2captcha_successful_flow_with_timeouts(
        self, mock_post, mock_get, captcha_solver
    ):
        """Test successful 2captcha flow uses correct timeouts"""
        # Mock successful submission
        mock_post.return_value.json.return_value = {
            "status": 1,
            "request": "captcha-id-123",
        }

        # Mock successful polling
        mock_get.return_value.json.return_value = {
            "status": 1,
            "request": "solved-captcha-response",
        }

        result = captcha_solver._solve_with_2captcha(
            "test-site-key", "https://example.com"
        )

        assert result == "solved-captcha-response"

        # Verify timeouts were used correctly
        submission_call = mock_post.call_args
        assert submission_call[1]["timeout"] == 30

        polling_call = mock_get.call_args
        assert polling_call[1]["timeout"] == 10

    @patch("src.anti_scraping.captcha_solver.requests.post")
    def test_anticaptcha_successful_flow_with_timeouts(self, mock_post, captcha_solver):
        """Test successful Anticaptcha flow uses correct timeouts"""
        # Mock successful submission and polling
        mock_post.side_effect = [
            Mock(
                json=lambda: {"errorId": 0, "taskId": "task-123"}
            ),  # Successful submission
            Mock(
                json=lambda: {
                    "status": "ready",
                    "solution": {"gRecaptchaResponse": "solved-response"},
                }
            ),  # Successful polling
        ]

        result = captcha_solver._solve_with_anticaptcha(
            "test-site-key", "https://example.com"
        )

        assert result == "solved-response"

        # Verify both calls used correct timeouts
        assert mock_post.call_count == 2

        for call_args in mock_post.call_args_list:
            # Submission uses 30s timeout, polling uses 10s timeout
            timeout = call_args[1]["timeout"]
            assert timeout in [30, 10]
