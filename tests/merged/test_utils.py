from mex.common.merged.utils import extend_list_in_dict, prune_list_in_dict


def test_extend_list_in_dict() -> None:
    dict_ = {"existing-key": ["already-here"]}

    extend_list_in_dict(dict_, "new-key", "single-value")
    assert dict_ == {
        "existing-key": ["already-here"],
        "new-key": ["single-value"],
    }

    extend_list_in_dict(dict_, "existing-key", "another-value")
    assert dict_ == {
        "existing-key": ["already-here", "another-value"],
        "new-key": ["single-value"],
    }

    extend_list_in_dict(dict_, "existing-key", None)
    assert dict_ == {
        "existing-key": ["already-here", "another-value"],
        "new-key": ["single-value"],
    }

    extend_list_in_dict(dict_, "another-key", None)
    assert dict_ == {
        "existing-key": ["already-here", "another-value"],
        "new-key": ["single-value"],
        "another-key": [],
    }


def test_prune_list_in_dict() -> None:
    dict_ = {
        "existing-key": ["leave-me-alone"],
        "prune-me": ["1", "2", "42", "foo"],
    }

    prune_list_in_dict(dict_, "prune-me", ["1", "2"])
    assert dict_ == {
        "existing-key": ["leave-me-alone"],
        "prune-me": ["42", "foo"],
    }

    prune_list_in_dict(dict_, "prune-me", "foo")
    assert dict_ == {
        "existing-key": ["leave-me-alone"],
        "prune-me": ["42"],
    }

    prune_list_in_dict(dict_, "prune-me", None)
    assert dict_ == {
        "existing-key": ["leave-me-alone"],
        "prune-me": ["42"],
    }

    prune_list_in_dict(dict_, "does-not-exist", "42")
    assert dict_ == {
        "existing-key": ["leave-me-alone"],
        "prune-me": ["42"],
        "does-not-exist": [],
    }
