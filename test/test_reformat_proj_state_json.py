from codebasegpt import utils

def test_reformat_embed_in_json():
    sample_json = """
{
    "remove_comments": true,
    "files": [
        {
            "path": "some/path",
            "embed": [
                0.1,
                0.2,
                0.3
            ]
        }
    ]
}
    """
    expected_output = """
{
    "remove_comments": true,
    "files": [
        {
            "path": "some/path",
            "embed": [0.1, 0.2, 0.3]
        }
    ]
}
    """

    reformatted_json = utils.reformat_proj_state_json(sample_json)
    print(reformatted_json)

    assert reformatted_json == expected_output
