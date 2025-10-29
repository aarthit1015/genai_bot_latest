# tests/test_rag.py
import pytest
from rag import MiniRAG
from db import init_db

def test_embed_and_retrieve():
    init_db()
    r = MiniRAG()
    # add simple docs
    r.add_documents([("doc1","This document explains how to reset your password."),
                     ("doc2","This doc describes pizza recipes and baking.")])
    res = r.retrieve("How to change password", k=1)
    assert res, "should return at least 1 result"
    assert "password" in res[0][1].lower()

def test_answer():
    r = MiniRAG()
    out = r.answer("How to reset password?")
    assert isinstance(out, str)
