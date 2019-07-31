"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import re
import textwrap

import colorful as cf
import pytest

from radish.formatters.gherkin import (
    write_feature_footer,
    write_feature_header,
    write_rule_header,
    write_tagline,
)
from radish.models import Background, DefaultRule, Feature, Rule, Step, Tag


@pytest.fixture(name="disabled_colors", scope="function")
def disable_ansi_colors():
    """Fixture to disable ANSI colors"""
    orig_colormode = cf.colormode
    cf.disable()
    yield
    cf.colormode = orig_colormode


def dedent_feature_file(contents):
    """Dedent the given Feature File contents"""
    dedented = textwrap.dedent(contents)
    # remove first empty line
    return "\n".join(dedented.splitlines()[1:]) + "\n"


def assert_output(capsys, expected_stdout):
    """Assert that the captured stdout matches"""
    actual_stdout = capsys.readouterr().out
    for actual_stdout_line, expected_stdout_line in zip(
        actual_stdout.splitlines(), expected_stdout.splitlines()
    ):
        assert re.match(
            "^" + expected_stdout_line + "$", actual_stdout_line
        ), "{!r} == {!r}".format(expected_stdout_line, actual_stdout_line)


def test_gf_write_tag_after_an_at_sign(disabled_colors, capsys, mocker):
    """Test that the Gherkin Formatter writes a Tag after the @-sign on a single line"""
    # given
    tag = mocker.MagicMock(spec=Tag)
    tag.name = "tag-a"

    # when
    write_tagline(tag)

    # then
    stdout = capsys.readouterr().out
    assert stdout == "@tag-a\n"


def test_gf_write_tag_with_given_identation(disabled_colors, capsys, mocker):
    """Test that the Gherkin Formatter writes a Tag with the given indentation"""
    # given
    tag = mocker.MagicMock(spec=Tag)
    tag.name = "tag-a"
    indentation = " " * 4

    # when
    write_tagline(tag, indentation)

    # then
    stdout = capsys.readouterr().out
    assert stdout == "    @tag-a\n"


def test_gf_write_feature_header_without_tags_without_description_without_background(
    disabled_colors, capsys, mocker
):
    """
    Test that the Gherkin Formatter properly writes a Feature header
    with no Tags, no description and no Background
    """
    # given
    feature = mocker.MagicMock(spec=Feature)
    feature.short_description = "My Feature"
    feature.description = []
    feature.tags = []
    feature.background = None

    # when
    write_feature_header(feature)

    # then
    stdout = capsys.readouterr().out
    assert stdout == "Feature: My Feature\n"


def test_gf_write_feature_header_with_tags_without_description_without_background(
    disabled_colors, capsys, mocker
):
    """
    Test that the Gherkin Formatter properly writes a Feature header
    with Tags, but no description and no Background
    """
    # given
    feature = mocker.MagicMock(spec=Feature)
    feature.short_description = "My Feature"
    feature.description = []
    first_tag = mocker.MagicMock(spec=Tag)
    first_tag.name = "tag-a"
    second_tag = mocker.MagicMock(spec=Tag)
    second_tag.name = "tag-b"
    feature.tags = [first_tag, second_tag]
    feature.background = None

    # when
    write_feature_header(feature)

    # then
    stdout = capsys.readouterr().out
    assert stdout == dedent_feature_file(
        """
        @tag-a
        @tag-b
        Feature: My Feature
        """
    )


def test_gf_write_feature_header_without_tags_with_description_without_background(
    disabled_colors, capsys, mocker
):
    """
    Test that the Gherkin Formatter properly writes a Feature header
    without Tags and Background, but description
    """
    # given
    feature = mocker.MagicMock(spec=Feature)
    feature.short_description = "My Feature"
    feature.description = ["foo", "bar", "bla"]
    feature.tags = []
    feature.background = None

    # when
    write_feature_header(feature)

    # then
    stdout = capsys.readouterr().out
    assert stdout == dedent_feature_file(
        """
        Feature: My Feature
            foo
            bar
            bla

        """
    )


def test_gf_write_feature_header_without_description_with_empty_background_no_short_description(
    disabled_colors, capsys, mocker
):
    """
    Test that the Gherkin Formatter properly writes a Feature header
    without Tags and Description, but with an empty Background with no short description
    """
    # given
    feature = mocker.MagicMock(spec=Feature)
    feature.short_description = "My Feature"
    feature.description = []
    feature.tags = []
    feature.background = mocker.MagicMock(spec=Background)
    feature.background.short_description = None
    feature.background.steps = []

    # when
    write_feature_header(feature)

    # then
    assert_output(
        capsys,
        dedent_feature_file(
            """
            Feature: My Feature
                Background:[ ]

            """
        ),
    )


def test_gf_write_feature_header_with_description_with_empty_background_no_short_description(
    disabled_colors, capsys, mocker
):
    """
    Test that the Gherkin Formatter properly writes a Feature header
    without Tags, but Description and an empty Background with no short description
    """
    # given
    feature = mocker.MagicMock(spec=Feature)
    feature.short_description = "My Feature"
    feature.description = ["foo", "bar", "bla"]
    feature.tags = []
    feature.background = mocker.MagicMock(spec=Background)
    feature.background.short_description = None
    feature.background.steps = []

    # when
    write_feature_header(feature)

    # then
    assert_output(
        capsys,
        dedent_feature_file(
            """
            Feature: My Feature
                foo
                bar
                bla

                Background:[ ]

            """
        ),
    )


def test_gf_write_feature_header_empty_background_with_short_description(
    disabled_colors, capsys, mocker
):
    """
    Test that the Gherkin Formatter properly writes a Feature header
    without Tags and Description but an empty Background with short description
    """
    # given
    feature = mocker.MagicMock(spec=Feature)
    feature.short_description = "My Feature"
    feature.description = []
    feature.tags = []
    feature.background = mocker.MagicMock(spec=Background)
    feature.background.short_description = "My Background"
    feature.background.steps = []

    # when
    write_feature_header(feature)

    # then
    assert_output(
        capsys,
        dedent_feature_file(
            """
            Feature: My Feature
                Background: My Background

            """
        ),
    )


def test_gf_write_feature_header_background_with_steps(disabled_colors, capsys, mocker):
    """
    Test that the Gherkin Formatter properly writes a Feature header
    without Tags and Description but a Background with Steps
    """
    # given
    feature = mocker.MagicMock(spec=Feature)
    feature.short_description = "My Feature"
    feature.description = []
    feature.tags = []
    feature.background = mocker.MagicMock(spec=Background)
    feature.background.short_description = "My Background"
    first_step = mocker.MagicMock(
        spec=Step,
        keyword="Given",
        text="there is a Step",
        doc_string=None,
        data_table=None,
    )
    second_step = mocker.MagicMock(
        spec=Step,
        keyword="When",
        text="there is a Step",
        doc_string=None,
        data_table=None,
    )
    feature.background.steps = [first_step, second_step]

    # when
    write_feature_header(feature)

    # then
    assert_output(
        capsys,
        dedent_feature_file(
            """
            Feature: My Feature
                Background: My Background
                    Given there is a Step
                    When there is a Step
            """
        ),
    )


def test_gf_write_feature_footer_blank_line_if_no_description_and_no_rules(
    disabled_colors, capsys, mocker
):
    """
    Test that the Gherkin Formatter writes a blank line after a Feature
    without a description and Rules
    """
    # given
    feature = mocker.MagicMock(spec=Feature)
    feature.description = []
    feature.rules = []

    # when
    write_feature_footer(feature)

    # then
    stdout = capsys.readouterr().out
    assert stdout == "\n"


def test_gf_write_feature_footer_no_blank_line_if_description(
    disabled_colors, capsys, mocker
):
    """
    Test that the Gherkin Formatter writes no blank line after a Feature
    with a Description
    """
    # given
    feature = mocker.MagicMock(spec=Feature)
    feature.description = ["foo"]
    feature.rules = []

    # when
    write_feature_footer(feature)

    # then
    stdout = capsys.readouterr().out
    assert stdout == ""


def test_gf_write_feature_footer_no_blank_line_if_rules(
    disabled_colors, capsys, mocker
):
    """
    Test that the Gherkin Formatter writes no blank line after a Feature
    with a Rule
    """
    # given
    feature = mocker.MagicMock(spec=Feature)
    feature.description = []
    feature.rules = ["foo"]

    # when
    write_feature_footer(feature)

    # then
    stdout = capsys.readouterr().out
    assert stdout == ""


def test_gf_write_rule_header(disabled_colors, capsys, mocker):
    """Test that the Gherkin Formatter properly writes a Rule"""
    # given
    rule = mocker.MagicMock(spec=Rule)
    rule.short_description = "My Rule"

    # when
    write_rule_header(rule)

    # then
    assert_output(
        capsys,
        dedent_feature_file(
            """
            (?P<indentation>    )Rule: My Rule

            """
        ),
    )


def test_gf_write_rule_header_nothing_for_default_rule(disabled_colors, capsys, mocker):
    """Test that the Gherkin Formatter writes no Rule header for a DefaultRule"""
    # given
    rule = mocker.MagicMock(spec=DefaultRule)

    # when
    write_rule_header(rule)

    # then
    stdout = capsys.readouterr().out
    assert stdout == ""
