"""
Modulo per la summarizzazione di testi.
"""

from .bart_summarizer import BartSummarizer, process_json_file

__all__ = ['BartSummarizer', 'process_json_file']