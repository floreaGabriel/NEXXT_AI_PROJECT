"""Patch LiteLLM to disable all async logging that causes event loop errors."""

import os
import sys
import warnings

# Suppress all warnings
warnings.filterwarnings("ignore")

# Set environment before any litellm imports
os.environ["LITELLM_TELEMETRY"] = "False"
os.environ["LITELLM_LOG"] = "ERROR"
os.environ["LITELLM_SUCCESS_CALLBACK"] = ""
os.environ["LITELLM_FAILURE_CALLBACK"] = ""
os.environ["LITELLM_DROP_PARAMS"] = "True"


def patch_litellm():
    """Completely disable LiteLLM's async logging worker to prevent event loop errors."""
    try:
        import litellm
        from litellm.litellm_core_utils.logging_worker import LoggingWorker
        
        # Disable all logging callbacks
        litellm.success_callback = []
        litellm.failure_callback = []
        litellm._async_success_callback = []
        litellm._async_failure_callback = []
        litellm.suppress_debug_info = True
        litellm.set_verbose = False
        
        # Monkey-patch the GLOBAL_LOGGING_WORKER to do nothing
        class NoOpLoggingWorker:
            """No-op logging worker that does nothing."""
            
            def ensure_initialized_and_enqueue(self, *args, **kwargs):
                """Do nothing - no logging."""
                pass
            
            def enqueue(self, *args, **kwargs):
                """Do nothing - no logging."""
                pass
        
        # Replace the global logging worker
        litellm.litellm_core_utils.logging_worker.GLOBAL_LOGGING_WORKER = NoOpLoggingWorker()
        
        # Patch the print_verbose function to suppress "[non-fatal] Tracing client error" messages
        original_print_verbose = litellm.print_verbose
        
        def silent_print_verbose(message):
            """Suppress tracing error messages."""
            if isinstance(message, str):
                # Suppress tracing and OpenAI API key errors
                if "[non-fatal]" in message or "Tracing client error" in message:
                    return
                if "Incorrect API key provided" in message:
                    return
            # Call original for other messages
            original_print_verbose(message)
        
        litellm.print_verbose = silent_print_verbose
        
        # Suppress litellm.utils logger
        import logging
        logging.getLogger("LiteLLM").setLevel(logging.CRITICAL)
        logging.getLogger("litellm").setLevel(logging.CRITICAL)
        
        return True
        
    except Exception as e:
        # Silently fail - don't print errors during patching
        return False


# Auto-patch on import
patch_litellm()
