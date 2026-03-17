# Prompt

`Prompt` is a PollyWeb wrapper for the Prompt chat payload described in the PollyWeb chats documentation.

## Usage

```python
import pollyweb as pw

prompt = pw.Prompt(
    Text = "What size pizza would you like?",
    Details = "Choose one of the standard menu sizes.",
    Options = ["small", "medium", "large"],
    Default = "medium",
    Input = "select",
)
```

Wrap it in a PollyWeb message when you want to send it through the normal chat pipeline:

```python
msg = prompt.to_msg(
    To = "shop.example.com",
)
assert msg.Subject == "Prompted@Host"
```

Parse a received prompt either from a raw body mapping or from a `Msg`:

```python
received = pw.Prompt.from_msg(msg)
same = pw.Prompt.parse({
    "Text": "What size pizza would you like?",
    "Options": ["small", "medium", "large"],
})
```

## Fields

- `Text`: required prompt text shown to the user.
- `Details`: optional supporting explanation.
- `Options`: optional list of choices or richer option objects.
- `Default`: optional default answer or selected value.
- `Appendix`: optional extra content shown after the main prompt.
- `Input`: optional input hint such as `text`, `select`, or another UI mode from the host.
- `Format`: optional output or rendering format hint.
- `Status`: optional prompt state marker supplied by the host.

## Methods

- `to_dict()`: returns the wire-format body mapping.
- `to_msg(To, ...)`: wraps the prompt in a `Msg` with `Subject = "Prompted@Host"`.
- `Prompt.from_dict(value)`: builds a prompt from a body mapping.
- `Prompt.from_msg(value)`: extracts a prompt from a `Prompted@Host` message.
- `Prompt.parse(value)`: accepts a `Prompt`, `Msg`, mapping, JSON, YAML, or bytes.
- `Prompt.load(value)`: alias for `parse(value)`.

## Validation

`PromptValidationError` is raised when:

- `Text` is missing or empty.
- one of the optional text fields is not a string.
- `Options` is not a list.
- `from_msg()` receives a message whose subject is not `Prompted@Host`.
- `from_msg()` receives a message whose body is not a mapping.
