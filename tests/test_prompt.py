"""Tests for the PollyWeb Prompt wrapper."""

import pytest

import pollyweb as pw


class TestPrompt:
    def test_to_dict_omits_empty_optional_fields(self):
        # Empty optional values should stay out of the wire payload.
        prompt = pw.Prompt(
            Text = "Choose a size",
        )

        assert prompt.to_dict() == {
            "Text": "Choose a size",
        }

    def test_prompt_round_trips_full_payload(self):
        # A rich prompt should keep all prompt-specific metadata intact.
        prompt = pw.Prompt(
            Text = "Choose a size",
            Details = "Available today only.",
            Options = [
                "small",
                {
                    "Value": "medium",
                    "Label": "Medium",
                },
            ],
            Default = "medium",
            Appendix = "Delivery takes 30 minutes.",
            Input = "select",
            Format = "plain",
            Status = "required",
        )

        parsed = pw.Prompt.from_dict(prompt.to_dict())

        assert parsed == prompt

    def test_to_msg_uses_prompted_subject(self):
        # Prompt messages should use the standard Prompted@Host subject.
        prompt = pw.Prompt(
            Text = "Choose a size",
            Options = ["small", "medium"],
        )

        msg = prompt.to_msg(
            To = "shop.example.com",
        )

        assert msg.Subject == "Prompted@Host"
        assert msg.To == "shop.example.com"
        assert msg.Body == prompt.to_dict()

    def test_from_msg_reads_prompted_host_body(self):
        # Received Prompted@Host messages should parse directly into prompts.
        msg = pw.Msg(
            From = "shop.example.com",
            To = "user.example.com",
            Subject = "Prompted@Host",
            Body = {
                "Text": "Choose a size",
                "Options": ["small", "medium"],
            },
        )

        prompt = pw.Prompt.from_msg(msg)

        assert prompt.Text == "Choose a size"
        assert prompt.Options == ["small", "medium"]

    def test_parse_accepts_wire_message_mapping(self):
        # Prompt.parse should recognize a full PollyWeb message envelope too.
        msg = pw.Msg(
            From = "shop.example.com",
            To = "user.example.com",
            Subject = "Prompted@Host",
            Body = {
                "Text": "Choose a size",
                "Default": "medium",
            },
        )

        prompt = pw.Prompt.parse(msg.to_dict())

        assert prompt.Default == "medium"

    def test_from_msg_rejects_other_subjects(self):
        # The wrapper should fail fast when the message is not a prompt.
        msg = pw.Msg(
            From = "shop.example.com",
            To = "user.example.com",
            Subject = "Hello@Host",
            Body = {
                "Text": "Choose a size",
            },
        )

        with pytest.raises(pw.PromptValidationError):
            pw.Prompt.from_msg(msg)

    def test_validation_rejects_empty_text(self):
        # The prompt text is the only required field.
        with pytest.raises(pw.PromptValidationError):
            pw.Prompt(
                Text = "",
            )
